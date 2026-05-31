from datetime import datetime
import re
from dateutil import parser as date_util_parser
from rapidfuzz import fuzz
import spacy

# Integrated your imported architectural utilities
from analysis.wikidata_utils import (
    entities_match,
    entity_similarity,
    normalize_entity,
)

nlp = spacy.load("en_core_web_sm")

CURRENT_YEAR = datetime.now().year

# =====================================================
# FALLBACK EVENT TERMS
# =====================================================
EVENT_TERMS = {
    "programme", "program", "event", "seminar", "conference",
    "social", "parting", "farewell", "meeting", "summit",
    "workshop", "festival", "ceremony", "world cup", "tournament",
    "match", "cup", "championship"
}

# =====================================================
# ENTITY CONFIGURATION WEIGHTS
# =====================================================
ENTITY_WEIGHTS = {
    "ORG": 3.0,
    "PERSON": 3.0,
    "GPE": 4.0,
    "LOC": 2.5,
    "DATE": 3.5,
    "TIME": 2.0,
    "CARDINAL": 2.5,
    "ORDINAL": 3.0,
    "EVENT": 3.5,
    "PRODUCT": 2.0
}

# =====================================================
# NON-LINEAR ACTION WEIGHTS
# =====================================================
ACTION_WEIGHTS = {
    "win": 5,
    "lose": 5,
    "eliminate": 5,
    "qualify": 5,
    "launch": 4,
    "announce": 2,
    "conduct": 1,
    "complete": 1
}

# =====================================================
# LEXICAL ARRAYS
# =====================================================
NEGATION_TERMS = {
    "not", "no", "never", "none", "neither", "cancelled",
    "canceled", "fake", "false", "deny", "denied", "reject",
    "rejected", "withdrawn", "didn't", "did not", "wasn't", "was not"
}

RECENT_TERMS = {
    "today", "yesterday", "recently", "currently", "now",
    "breaking", "latest", "this year", "this week", "this month"
}

OLD_TERMS = {
    "previously", "formerly", "historical", "earlier", "past",
    "old", "archived", "years ago"
}

ACTION_NORMALIZATION = {
    "hosted": "conduct",
    "hosting": "conduct",
    "organized": "conduct",
    "organised": "conduct",
    "held": "conduct",
    "cancelled": "cancel",
    "canceled": "cancel",
    "postponed": "postpone",
    "won": "win",
    "wins": "win",
    "winning": "win",
    "lost": "lose",
    "loses": "lose",
    "completed": "complete",
    "completes": "complete",
    "finished": "complete",
    "conducted": "conduct",
    "launched": "launch",
    "announced": "announce",
    "eliminate": "eliminate",
    "eliminated": "eliminate",
    "eliminates": "eliminate",
    "eliminating": "eliminate",
    "knock": "eliminate",
    "knocked": "eliminate",
    "knockout": "eliminate",
    "knocked out": "eliminate",
    "exited": "eliminate",
    "exit": "eliminate",
    "qualify": "qualify",
    "qualified": "qualify",
    "qualifies": "qualify"
}

# Expanded complete contradiction map
CONTRADICTION_ACTIONS = {
    "launch": ["cancel", "withdraw"],
    "conduct": ["cancel", "postpone"],
    "announce": ["deny", "reject"],
    "win": ["lose", "eliminate"],
    "lose": ["win"],
    "approve": ["reject", "deny"],
    "complete": ["cancel", "postpone"],
    "elect": ["defeat", "reject"],
    "join": ["leave"],
    "increase": ["decrease", "reduction", "drop", "fall"],
    "decrease": ["increase", "rise", "growth"],
    "rise": ["fall", "drop", "decrease"],
    "fall": ["rise", "increase", "growth"],
    "open": ["close"],
    "close": ["open"],
    "start": ["stop", "terminate", "end"],
    "stop": ["start", "begin", "resume"],
    "hire": ["fire", "terminate", "dismiss"],
    "fire": ["hire", "employ", "retain"],
    "qualify": ["eliminate", "fail", "exit"],
    "eliminate": ["qualify", "win", "advance"],
    "enter": ["exit", "leave"],
    "exit": ["enter", "join", "stay"],
    "promote": ["demote", "downgrade"],
    "demote": ["promote", "upgrade"]
}


# =====================================================
# ENGINE HELPERS & DEEP PARSERS
# =====================================================

def normalize_event(text):
    text = text.lower()
    for drop in ["icc", "the", "fifa", "men's", "women's"]:
        text = text.replace(drop, "")
    return " ".join(text.split())


def event_similarity(events_a, events_b):
    best = 0
    synonyms = {"championship": "cup",
                "cup": "championship", "tournament": "cup"}

    for e1 in events_a:
        norm_e1 = normalize_event(e1)
        tokens_a = set(norm_e1.split())
        for e2 in events_b:
            norm_e2 = normalize_event(e2)
            tokens_b = set(norm_e2.split())

            mapped_a = {synonyms.get(w, w) for w in tokens_a}
            mapped_b = {synonyms.get(w, w) for w in tokens_b}

            intersection = mapped_a & mapped_b
            union = mapped_a | mapped_b
            jaccard = len(intersection) / len(union) if union else 0

            fuzzy_ratio = fuzz.token_sort_ratio(norm_e1, norm_e2) / 100.0
            combined = (jaccard * 0.6) + (fuzzy_ratio * 0.4)

            if combined > best:
                best = combined

    return int(best * 100)


def get_winning_entities(text):
    """Dependency Parser separating winners and losers via passive/active handling (Verb List Expanded)."""
    doc = nlp(text)
    results = {"winners": [], "losers": []}

    # Expanded to include advance, qualify, reach, top, finish, progress
    target_verbs = ["win", "victory", "triumph", "advance",
                    "qualify", "reach", "top", "finish", "progress"]

    for token in doc:
        lemma = token.lemma_.lower()
        if lemma in target_verbs:
            for child in token.children:
                if child.dep_ in ["nsubj", "nsubjpass", "agent"]:
                    subtree_text = "".join(
                        [t.text_with_ws for t in child.subtree]).strip().lower()
                    results["winners"].append(subtree_text)

            if token.dep_ == "acomp" and token.head.lemma_ == "be":
                for head_child in token.head.children:
                    if head_child.dep_ == "nsubj":
                        subtree_text = "".join(
                            [t.text_with_ws for t in head_child.subtree]).strip().lower()
                        results["winners"].append(subtree_text)

        elif lemma in ["defeat", "eliminate", "beat", "knock"]:
            is_passive = any(c.dep_ == "auxpass" for c in token.children)
            for child in token.children:
                subtree_text = "".join(
                    [t.text_with_ws for t in child.subtree]).strip().lower()

                if is_passive:
                    if child.dep_ == "nsubjpass":
                        results["losers"].append(subtree_text)
                    elif child.dep_ == "agent" or (child.dep_ == "prep" and child.text.lower() == "by"):
                        agent_ents = ["".join([t.text_with_ws for t in gc.subtree]).strip().lower()
                                      for gc in child.children if gc.dep_ in ["pobj", "obj"]]
                        results["winners"].extend(
                            agent_ents if agent_ents else [subtree_text])
                else:
                    if child.dep_ == "nsubj":
                        results["winners"].append(subtree_text)
                    elif child.dep_ in ["obj", "dobj"]:
                        results["losers"].append(subtree_text)

    results["winners"] = list(set(results["winners"]))
    results["losers"] = list(set(results["losers"]))
    return results


def normalize_date_string(date_str):
    """Robust ISO date normalizer preventing out-of-context string breaks."""
    try:
        parsed_dt = date_util_parser.parse(
            date_str, fuzzy=True, default=datetime(CURRENT_YEAR, 1, 1))
        return parsed_dt.strftime("%Y-%m-%d")
    except:
        return date_str.lower().strip()


def resolve_lexical_entities_match(ent_a, ent_b):
    """Hybrid structural matcher routing through Wikidata utilities (Strict ORG Guard Implemented)."""
    # Require exact normalization check for ORGs before falling back to fuzzy loops
    if ent_a["label"] == "ORG" and ent_b["label"] == "ORG":
        try:
            norm_a = normalize_entity(ent_a["text"]) or ent_a["text"]
            norm_b = normalize_entity(ent_b["text"]) or ent_b["text"]
            return norm_a == norm_b

        except:
            return ent_a["text"].strip().lower() == ent_b["text"].strip().lower()

    try:
        if entities_match(ent_a["text"], ent_b["text"]):
            return True
        if entity_similarity(ent_a["text"], ent_b["text"]) >= 0.85:
            return True
    except:
        pass

    similarity = fuzz.token_sort_ratio(ent_a["text"], ent_b["text"])
    threshold = 90 if (
        ent_a["label"] == "GPE" or ent_b["label"] == "GPE") else 80
    return similarity >= threshold


def entity_overlap_score(ids_a, ids_b):
    if not ids_a or not ids_b:
        return 0
    return len(set(ids_a) & set(ids_b))


def normalize_action(action):
    action = action.lower()
    return ACTION_NORMALIZATION.get(action, action)


def extract_negations(doc):
    negations = []
    for token in doc:
        if token.dep_ == "neg" or token.text.lower() in NEGATION_TERMS:
            negations.append(token.text.lower())
    return list(set(negations))


def extract_recency_terms(text):
    text = text.lower()
    return [term for term in RECENT_TERMS if term in text]


def extract_old_terms(text):
    text = text.lower()
    return [term for term in OLD_TERMS if term in text]


def extract_years(text):
    return re.findall(r"\b(?:19|20)\d{2}\b", text)


def enrich_entities_with_wikidata(entities):
    enriched = []
    for ent in entities:
        try:
            norm_text = normalize_entity(ent["text"]) or ent["text"]
        except:
            norm_text = ent["text"]

        enriched.append({
            "text": norm_text,
            "label": ent["label"],
            "wikidata_ids": []
        })
    return enriched


# =====================================================
# FACT STRUCTURE EXTRACTION (Dual Date Schemas Built)
# =====================================================

def extract_fact_structure(text):
    doc = nlp(text)
    text_lower = text.lower()

    structure = {
        "text": text,
        "entities": [],
        "actions": [],
        "event_terms": [],
        "noun_chunks": [],
        "years": [],
        "negations": [],
        "recency_terms": [],
        "old_terms": [],
        "ordinals": [],
        # Now holds explicit {"raw": ..., "normalized": ...} objects
        "dates": [],
        "scorelines": [],
        "quantities": [],
        "cardinals": []
    }

    scoreline_matches = re.findall(r"\b\d+\s*[:\-–]\s*\d+\b", text)
    structure["scorelines"] = [s.replace(" ", "") for s in scoreline_matches]

    unit_matches = re.findall(
        r"\b\d+\s*(?:runs|wickets|goals|points|v|vs)\b", text_lower)
    structure["scorelines"].extend(unit_matches)

    raw_entities = []
    event_terms = []

    for ent in doc.ents:
        cleaned_text = ent.text.strip().lower()
        if len(cleaned_text) > 1:
            raw_entities.append({
                "text": cleaned_text,
                "label": ent.label_
            })
            if ent.label_ == "EVENT":
                event_terms.append(cleaned_text)
            elif ent.label_ == "ORDINAL":
                structure["ordinals"].append(cleaned_text)
            elif ent.label_ in ["DATE", "TIME"]:
                if not re.match(r"\b(?:19|20)\d{2}\b", cleaned_text):
                    # Cache both raw text and parsed standard output strings
                    structure["dates"].append({
                        "raw": cleaned_text,
                        "normalized": normalize_date_string(cleaned_text)
                    })

    structure["entities"] = enrich_entities_with_wikidata(raw_entities)

    for token in doc:
        if token.pos_ == "NUM":
            num_val = token.text.strip()
            if any(num_val in sl for sl in structure["scorelines"]) or re.match(r"\b(?:19|20)\d{2}\b", num_val):
                continue

            head_word = token.head.lemma_.lower()
            if token.head.pos_ in ["NOUN", "PROPN"]:
                structure["quantities"].append((head_word, num_val))
            else:
                siblings = [t.lemma_.lower() for t in token.head.children if t.pos_ in [
                    "NOUN", "PROPN"]]
                if siblings:
                    structure["quantities"].append((siblings[0], num_val))
                else:
                    structure["cardinals"].append(num_val)

    structure["years"] = list(set(extract_years(text)))
    structure["negations"] = extract_negations(doc)
    structure["recency_terms"] = extract_recency_terms(text)
    structure["old_terms"] = extract_old_terms(text)

    actions = []
    for token in doc:
        if token.pos_ in ["VERB", "AUX"]:
            normalized = normalize_action(token.lemma_.lower())
            if len(normalized) > 2:
                actions.append(normalized)
    structure["actions"] = list(set(actions))

    for event in EVENT_TERMS:
        if event in text_lower:
            event_terms.append(event)
    structure["event_terms"] = list(set(event_terms))

    for chunk in doc.noun_chunks:
        cleaned = chunk.text.strip().lower()
        if len(cleaned) > 2:
            structure["noun_chunks"].append(cleaned)
    structure["noun_chunks"] = list(set(structure["noun_chunks"]))

    return structure


# =====================================================
# CONFLICT EVALUATION CORE
# =====================================================

def detect_conflicts(claim_struct, evidence_struct):
    conflicts = []

    entity_related = False
    for c_ent in claim_struct["entities"]:
        for e_ent in evidence_struct["entities"]:
            if resolve_lexical_entities_match(c_ent, e_ent):
                entity_related = True
                break

    shared_years = set(claim_struct["years"]) & set(evidence_struct["years"])
    event_score = event_similarity(
        claim_struct["event_terms"], evidence_struct["event_terms"])
    same_event = event_score >= 80
    same_context = bool(shared_years and same_event)

    if claim_struct["scorelines"] and evidence_struct["scorelines"]:
        if not (set(claim_struct["scorelines"]) & set(evidence_struct["scorelines"])):
            conflicts.append("score_conflict")

    # Context-bound Date matching with structural Month/Day Guard
    shared_actions = set(claim_struct["actions"]) & set(
        evidence_struct["actions"])
    if claim_struct["dates"] and evidence_struct["dates"] and same_event and shared_actions:
        date_overlap = False
        for c_date in claim_struct["dates"]:
            for e_date in evidence_struct["dates"]:
                # Parse pieces out of standard forms to check Month/Day alignment explicitly
                try:
                    c_dt = date_util_parser.parse(c_date["raw"], fuzzy=True)
                    e_dt = date_util_parser.parse(e_date["raw"], fuzzy=True)
                    if (
                        c_dt.year == e_dt.year and
                        c_dt.month == e_dt.month and
                        c_dt.day == e_dt.day
                    ):
                        date_overlap = True
                        break
                except:
                    if c_date["normalized"] == e_date["normalized"]:
                        date_overlap = True
                        break
            if date_overlap:
                break
        if not date_overlap:
            conflicts.append("date_conflict")

    if claim_struct["ordinals"] and evidence_struct["ordinals"]:
        if not (set(claim_struct["ordinals"]) & set(evidence_struct["ordinals"])):
            conflicts.append("ordinal_conflict")

    # Role-Bound Quantities with Estimation Thresholds
    for c_role, c_val in claim_struct["quantities"]:
        for e_role, e_val in evidence_struct["quantities"]:
            if c_role == e_role:
                try:
                    c_num, e_num = float(c_val), float(e_val)
                    max_num = max(c_num, e_num)
                    if max_num > 0 and (abs(c_num - e_num) / max_num) > 0.20:
                        conflicts.append("cardinal_conflict")
                except ValueError:
                    if c_val != e_val:
                        conflicts.append("cardinal_conflict")

    if claim_struct["years"] and evidence_struct["years"] and not shared_years:
        try:
            if abs(max(int(y) for y in claim_struct["years"]) - max(int(y) for y in evidence_struct["years"])) >= 2:
                conflicts.append("year_conflict")
        except:
            pass

    # ==========================================
    # TOURNAMENT RESULT CHECKS
    # ==========================================
    claim_sports = get_winning_entities(claim_struct["text"])
    evidence_sports = get_winning_entities(evidence_struct["text"])

    claim_winners, claim_losers = set(
        claim_sports["winners"]), set(claim_sports["losers"])
    evidence_winners, evidence_losers = set(
        evidence_sports["winners"]), set(evidence_sports["losers"])

    if same_context:
        claim_actions = set(claim_struct["actions"])
        evidence_actions = set(evidence_struct["actions"])

        if (claim_winners & evidence_winners) or (claim_losers & evidence_losers):
            for c_act in claim_actions:
                opposites = CONTRADICTION_ACTIONS.get(c_act, [])
                if any(e_act in opposites for e_act in evidence_actions):
                    conflicts.append("tournament_result_conflict")

        if (claim_winners and evidence_winners and claim_winners != evidence_winners) or \
           (claim_losers and evidence_losers and claim_losers != evidence_losers):
            conflicts.append("tournament_result_conflict")

    # ==========================================
    # ACTION & NEGATION VALIDATION
    # ==========================================
    if entity_related:
        for claim_action in claim_struct["actions"]:
            opposite_actions = CONTRADICTION_ACTIONS.get(claim_action, [])
            for evidence_action in evidence_struct["actions"]:
                if evidence_action in opposite_actions:
                    conflicts.append("action_conflict")

    if bool(claim_struct["negations"]) != bool(evidence_struct["negations"]) and entity_related:
        conflicts.append("negation_conflict")

    if bool(claim_struct["recency_terms"]) and bool(evidence_struct["old_terms"]):
        conflicts.append("stale_context_conflict")

    if bool(claim_struct["recency_terms"]) and evidence_struct["years"]:
        for year in evidence_struct["years"]:
            try:
                if (CURRENT_YEAR - int(year)) >= 2:
                    conflicts.append("recycled_news_conflict")
            except:
                pass

    if not same_context and claim_winners and evidence_winners and claim_winners != evidence_winners:
        conflicts.append("winner_conflict")

    return list(set(conflicts))


# =====================================================
# FACT STRUCTURE COMPARISON
# =====================================================

def compare_fact_structure(claim, evidence):
    claim_struct = extract_fact_structure(claim)
    evidence_struct = extract_fact_structure(evidence)
    score = 0

    entity_score = 0
    matched_pairs = set()

    for claim_ent in claim_struct["entities"]:
        for evidence_ent in evidence_struct["entities"]:
            pair_key = (claim_ent["text"], evidence_ent["text"])
            if pair_key in matched_pairs:
                continue
            matched_pairs.add(pair_key)

            if entity_overlap_score(claim_ent.get("wikidata_ids", []), evidence_ent.get("wikidata_ids", [])) > 0:
                entity_score += 5
                continue

            if resolve_lexical_entities_match(claim_ent, evidence_ent):
                weight = ENTITY_WEIGHTS.get(claim_ent["label"], 1.5)
                if claim_ent["label"] == evidence_ent["label"]:
                    entity_score += weight
                else:
                    entity_score += (weight * 0.5)

    score += entity_score

    for claim_action in claim_struct["actions"]:
        for evidence_action in evidence_struct["actions"]:
            if fuzz.ratio(claim_action, evidence_action) >= 85:
                score += ACTION_WEIGHTS.get(claim_action, 1)

    event_score = event_similarity(
        claim_struct["event_terms"], evidence_struct["event_terms"])
    if event_score >= 80:
        score += 4

    if claim_struct["scorelines"] and (set(claim_struct["scorelines"]) & set(evidence_struct["scorelines"])):
        score += 3

    # Update date intersection checks to scan underlying standardized objects
    c_dates = {d["normalized"] for d in claim_struct["dates"]}
    e_dates = {d["normalized"] for d in evidence_struct["dates"]}
    if c_dates and (c_dates & e_dates):
        score += 3

    if claim_struct["ordinals"] and (set(claim_struct["ordinals"]) & set(evidence_struct["ordinals"])):
        score += 2

    claim_years = set(claim_struct["years"])
    evidence_years = set(evidence_struct["years"])
    if claim_years and (claim_years & evidence_years):
        score += 5

    chunk_scores = []
    for claim_chunk in claim_struct["noun_chunks"]:
        for evidence_chunk in evidence_struct["noun_chunks"]:
            chunk_scores.append(fuzz.token_sort_ratio(
                claim_chunk, evidence_chunk) / 100.0)

    if chunk_scores:
        top_scores = sorted(chunk_scores, reverse=True)[:3]
        avg_chunk_score = sum(top_scores) / len(top_scores)
        if score > 3:
            score += avg_chunk_score * 2

    if claim_struct["years"] and evidence_struct["years"] and claim_struct["actions"] and evidence_struct["actions"]:
        if set(claim_struct["actions"]) & set(evidence_struct["actions"]):
            score += 4

    conflicts = detect_conflicts(claim_struct, evidence_struct)

    for conflict in conflicts:
        if conflict == "action_conflict":
            score -= 6
        elif conflict == "year_conflict":
            score -= 5
        elif conflict == "negation_conflict":
            score -= 8
        elif conflict == "recycled_news_conflict":
            score -= 5
        elif conflict == "stale_context_conflict":
            score -= 6
        elif conflict == "entity_conflict":
            score -= 20
        elif conflict == "winner_conflict":
            score -= 15
        elif conflict == "tournament_result_conflict":
            score -= 20
        elif conflict == "score_conflict":
            score -= 6
        elif conflict == "date_conflict":
            score -= 3
        elif conflict == "ordinal_conflict":
            score -= 1
        elif conflict == "cardinal_conflict":
            score -= 2

    if claim_struct["recency_terms"] and evidence_struct["years"]:
        try:
            if max(int(y) for y in evidence_struct["years"]) >= CURRENT_YEAR - 1:
                score += 2
        except:
            pass

    return {
        "score": round(score, 3),
        "claim": claim_struct,
        "evidence": evidence_struct,
        "conflicts": conflicts,
        "conflict_count": len(conflicts)
    }
