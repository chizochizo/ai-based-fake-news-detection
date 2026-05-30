from rapidfuzz import fuzz
import spacy
import re
from datetime import datetime

from analysis.wikidata_utils import (
    entities_match,
    normalize_entity,
    entity_similarity
)

nlp = spacy.load(
    "en_core_web_sm"
)

CURRENT_YEAR = datetime.now().year

# =====================================================
# EVENT KEYWORDS
# =====================================================

EVENT_TERMS = {

    "programme",
    "program",
    "event",
    "seminar",
    "conference",
    "social",
    "parting",
    "farewell",
    "meeting",
    "summit",
    "workshop",
    "festival",
    "ceremony",
    "world cup",
    "tournament",
    "match",
    "cup"
}

# =====================================================
# ENTITY WEIGHTS
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
# NEGATION TERMS
# =====================================================

NEGATION_TERMS = {

    "not",
    "no",
    "never",
    "none",
    "neither",
    "cancelled",
    "canceled",
    "fake",
    "false",
    "deny",
    "denied",
    "reject",
    "rejected",
    "withdrawn",
    "didn't",
    "did not",
    "wasn't",
    "was not"
}

# =====================================================
# RECENCY TERMS
# =====================================================

RECENT_TERMS = {

    "today",
    "yesterday",
    "recently",
    "currently",
    "now",
    "breaking",
    "latest",
    "this year",
    "this week",
    "this month"
}

# =====================================================
# OLD / HISTORICAL TERMS
# =====================================================

OLD_TERMS = {

    "previously",
    "formerly",
    "historical",
    "earlier",
    "past",
    "old",
    "archived",
    "years ago"
}

# =====================================================
# ACTION NORMALIZATION
# =====================================================

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

    "announced": "announce"
}

# =====================================================
# ACTION CONTRADICTIONS
# =====================================================

CONTRADICTION_ACTIONS = {

    "launch": [
        "cancel",
        "withdraw"
    ],

    "conduct": [
        "cancel",
        "postpone"
    ],

    "announce": [
        "deny",
        "reject"
    ],

    "win": [
        "lose"
    ],

    "lose": [
        "win"
    ],

    "approve": [
        "reject",
        "deny"
    ],

    "complete": [
        "cancel",
        "postpone"
    ]
}


# =====================================================
# HELPERS
# =====================================================

def entity_overlap_score(
    ids_a,
    ids_b
):

    if not ids_a or not ids_b:

        return 0

    overlap = set(ids_a) & set(ids_b)

    return len(overlap)


def normalize_action(action):

    action = action.lower()

    return ACTION_NORMALIZATION.get(
        action,
        action
    )


def extract_negations(doc):

    negations = []

    for token in doc:

        if token.dep_ == "neg":

            negations.append(
                token.text.lower()
            )

        elif token.text.lower() in NEGATION_TERMS:

            negations.append(
                token.text.lower()
            )

    return list(set(negations))


# =====================================================
# RECENCY DETECTION
# =====================================================

def extract_recency_terms(text):

    text = text.lower()

    found = []

    for term in RECENT_TERMS:

        if term in text:

            found.append(term)

    return found


# =====================================================
# OLD CONTEXT DETECTION
# =====================================================

def extract_old_terms(text):

    text = text.lower()

    found = []

    for term in OLD_TERMS:

        if term in text:

            found.append(term)

    return found


# =====================================================
# YEAR EXTRACTION
# =====================================================

def extract_years(text):

    return re.findall(
        r"\b(?:19|20)\d{2}\b",
        text
    )


# =====================================================
# ENTITY RESOLUTION PLACEHOLDER
# =====================================================

def enrich_entities_with_wikidata(
    entities
):

    enriched = []

    for ent in entities:

        enriched.append({

            "text": ent["text"],

            "label": ent["label"],

            "wikidata_ids": []
        })

    return enriched


# =====================================================
# FACT STRUCTURE EXTRACTION
# =====================================================

def extract_fact_structure(text):

    doc = nlp(text)

    structure = {

        "entities": [],

        "numbers": [],

        "actions": [],

        "event_terms": [],

        "noun_chunks": [],

        "years": [],

        "negations": [],

        "recency_terms": [],

        "old_terms": []
    }

    # ==========================================
    # ENTITIES
    # ==========================================

    raw_entities = []

    for ent in doc.ents:

        cleaned_text = (
            ent.text
            .strip()
            .lower()
        )

        if len(cleaned_text) > 1:

            raw_entities.append({

                "text": cleaned_text,

                "label": ent.label_
            })

    structure["entities"] = (
        enrich_entities_with_wikidata(
            raw_entities
        )
    )

    # ==========================================
    # NUMBERS
    # ==========================================

    numbers = re.findall(
        r"\b\d+(?:st|nd|rd|th)?\b",
        text.lower()
    )

    structure["numbers"] = list(set(numbers))

    # ==========================================
    # YEARS
    # ==========================================

    structure["years"] = list(set(
        extract_years(text)
    ))

    # ==========================================
    # NEGATIONS
    # ==========================================

    structure["negations"] = extract_negations(
        doc
    )

    # ==========================================
    # RECENCY TERMS
    # ==========================================

    structure["recency_terms"] = (
        extract_recency_terms(text)
    )

    # ==========================================
    # OLD TERMS
    # ==========================================

    structure["old_terms"] = (
        extract_old_terms(text)
    )

    # ==========================================
    # ACTIONS
    # ==========================================

    actions = []

    for token in doc:

        if token.pos_ in ["VERB", "AUX"]:

            normalized = normalize_action(
                token.lemma_.lower()
            )

            if len(normalized) > 2:

                actions.append(
                    normalized
                )

    structure["actions"] = list(set(actions))

    # ==========================================
    # EVENT TERMS
    # ==========================================

    event_terms = []

    text_lower = text.lower()

    for event in EVENT_TERMS:

        if event in text_lower:

            event_terms.append(event)

    structure["event_terms"] = list(set(
        event_terms
    ))

    # ==========================================
    # NOUN CHUNKS
    # ==========================================

    noun_chunks = []

    for chunk in doc.noun_chunks:

        cleaned = (
            chunk.text
            .strip()
            .lower()
        )

        if len(cleaned) > 2:

            noun_chunks.append(
                cleaned
            )

    structure["noun_chunks"] = list(set(
        noun_chunks
    ))

    return structure


# =====================================================
# ENTITY OVERLAP
# =====================================================

def has_entity_overlap(
    claim_entities,
    evidence_entities
):

    for claim_ent in claim_entities:

        for evidence_ent in evidence_entities:

            # ----------------------------------
            # WIKIDATA MATCH
            # ----------------------------------

            wikidata_score = entity_overlap_score(

                claim_ent.get(
                    "wikidata_ids",
                    []
                ),

                evidence_ent.get(
                    "wikidata_ids",
                    []
                )
            )

            if wikidata_score > 0:

                return True

            # ----------------------------------
            # FUZZY MATCH
            # ----------------------------------

            similarity = fuzz.token_sort_ratio(

                claim_ent["text"],

                evidence_ent["text"]
            )

            if similarity >= 80:

                return True

    return False


# =====================================================
# CONTEXTUAL RECENCY CHECK
# =====================================================

def detect_contextual_conflicts(
    claim_struct,
    evidence_struct
):

    conflicts = []

    claim_recent = bool(
        claim_struct["recency_terms"]
    )

    evidence_old = bool(
        evidence_struct["old_terms"]
    )

    evidence_years = evidence_struct[
        "years"
    ]

    # ==========================================
    # OLD CONTENT FRAMED AS CURRENT
    # ==========================================

    if claim_recent and evidence_old:

        conflicts.append(
            "stale_context_conflict"
        )

    # ==========================================
    # RECYCLED NEWS CHECK
    # ==========================================

    if claim_recent and evidence_years:

        for year in evidence_years:

            try:

                age = CURRENT_YEAR - int(year)

                if age >= 2:

                    conflicts.append(
                        "recycled_news_conflict"
                    )

            except:
                pass

    return list(set(conflicts))


# =====================================================
# CONFLICT DETECTION
# =====================================================

def detect_conflicts(
    claim_struct,
    evidence_struct
):

    conflicts = []

    entity_related = has_entity_overlap(

        claim_struct["entities"],

        evidence_struct["entities"]
    )

    # ==========================================
    # NUMBER CONFLICTS
    # ==========================================

    claim_numbers = set(
        claim_struct["numbers"]
    )

    evidence_numbers = set(
        evidence_struct["numbers"]
    )

    shared_numbers = (
        claim_numbers
        &
        evidence_numbers
    )

    if (

        claim_numbers

        and

        evidence_numbers

        and

        not shared_numbers

    ):

        if (

            len(claim_numbers) <= 2

            and

            len(evidence_numbers) <= 2
        ):

            conflicts.append(
                "number_conflict"
            )

    # ==========================================
    # YEAR CONFLICTS
    # ==========================================

    claim_years = set(
        claim_struct["years"]
    )

    evidence_years = set(
        evidence_struct["years"]
    )

    shared_years = (
        claim_years
        &
        evidence_years
    )

    if (

        claim_years

        and

        evidence_years

        and

        not shared_years

    ):

        try:

            claim_year = max(
                int(y)
                for y in claim_years
            )

            evidence_year = max(
                int(y)
                for y in evidence_years
            )

            if abs(
                claim_year
                -
                evidence_year
            ) >= 2:

                conflicts.append(
                    "year_conflict"
                )

        except:
            pass

    # ==========================================
    # ACTION CONFLICTS
    # ==========================================

    if entity_related:

        for claim_action in claim_struct[
            "actions"
        ]:

            opposite_actions = (
                CONTRADICTION_ACTIONS.get(
                    claim_action,
                    []
                )
            )

            for evidence_action in evidence_struct[
                "actions"
            ]:

                if evidence_action in opposite_actions:

                    conflicts.append(
                        "action_conflict"
                    )

    # ==========================================
    # NEGATION CONFLICTS
    # ==========================================

    claim_has_negation = bool(
        claim_struct["negations"]
    )

    evidence_has_negation = bool(
        evidence_struct["negations"]
    )

    if claim_has_negation != evidence_has_negation:

        if entity_related:

            conflicts.append(
                "negation_conflict"
            )

    # ==========================================
    # CONTEXTUAL CONFLICTS
    # ==========================================

    contextual_conflicts = (
        detect_contextual_conflicts(
            claim_struct,
            evidence_struct
        )
    )

    conflicts.extend(
        contextual_conflicts
    )

    return list(set(conflicts))


# =====================================================
# FACT STRUCTURE COMPARISON
# =====================================================

def compare_fact_structure(
    claim,
    evidence
):

    claim_struct = (
        extract_fact_structure(claim)
    )

    evidence_struct = (
        extract_fact_structure(evidence)
    )

    score = 0

    # =================================================
    # ENTITY MATCHING
    # =================================================

    entity_score = 0

    matched_pairs = set()

    for claim_ent in claim_struct["entities"]:

        for evidence_ent in evidence_struct["entities"]:

            pair_key = (

                claim_ent["text"],
                evidence_ent["text"]
            )

            if pair_key in matched_pairs:

                continue

            matched_pairs.add(
                pair_key
            )

            # -----------------------------------------
            # WIKIDATA ENTITY BOOST
            # -----------------------------------------

            wikidata_score = entity_overlap_score(

                claim_ent.get(
                    "wikidata_ids",
                    []
                ),

                evidence_ent.get(
                    "wikidata_ids",
                    []
                )
            )

            if wikidata_score > 0:

                entity_score += 5

                continue

            # -----------------------------------------
            # FUZZY ENTITY MATCH
            # -----------------------------------------

            similarity = fuzz.token_sort_ratio(

                claim_ent["text"],

                evidence_ent["text"]
            )

            if similarity >= 80:

                weight = ENTITY_WEIGHTS.get(

                    claim_ent["label"],

                    1.5
                )

                if (
                    claim_ent["label"]
                    ==
                    evidence_ent["label"]
                ):

                    entity_score += weight

                else:

                    entity_score += (
                        weight * 0.5
                    )

    score += entity_score

    # =================================================
    # ACTION MATCHING
    # =================================================

    action_overlap = 0

    for claim_action in claim_struct["actions"]:

        for evidence_action in evidence_struct["actions"]:

            similarity = fuzz.ratio(

                claim_action,
                evidence_action
            )

            if similarity >= 85:

                action_overlap += 1

    score += action_overlap * 3

    # =================================================
    # EVENT TERM MATCHING
    # =================================================

    event_overlap = len(

        set(claim_struct["event_terms"])
        &
        set(evidence_struct["event_terms"])

    )

    score += event_overlap * 4

    # =================================================
    # NUMBER MATCHING
    # =================================================

    claim_numbers = set(
        claim_struct["numbers"]
    )

    evidence_numbers = set(
        evidence_struct["numbers"]
    )

    if claim_numbers:

        if claim_numbers & evidence_numbers:

            score += 3

        else:

            if len(claim_numbers) <= 2:

                score -= 1

    # =================================================
    # YEAR MATCHING
    # =================================================

    claim_years = set(
        claim_struct["years"]
    )

    evidence_years = set(
        evidence_struct["years"]
    )

    if claim_years:

        if claim_years & evidence_years:

            score += 5

        else:

            try:

                claim_year = max(
                    int(y)
                    for y in claim_years
                )

                evidence_year = max(
                    int(y)
                    for y in evidence_years
                )

                if abs(
                    claim_year
                    -
                    evidence_year
                ) >= 2:

                    score -= 5

            except:
                pass

    # =================================================
    # NOUN CHUNK MATCH
    # =================================================

    best_chunk_score = 0

    for claim_chunk in claim_struct[
        "noun_chunks"
    ]:

        for evidence_chunk in evidence_struct[
            "noun_chunks"
        ]:

            similarity = fuzz.token_sort_ratio(

                claim_chunk,

                evidence_chunk

            ) / 100.0

            if similarity > best_chunk_score:

                best_chunk_score = similarity

    if (
        action_overlap > 0
        or
        event_overlap > 0
        or
        entity_score > 3
    ):

        score += best_chunk_score * 4

    # =================================================
    # SPECIAL SPORTS / EVENT BOOST
    # =================================================

    if (

        claim_struct["years"]

        and

        evidence_struct["years"]

        and

        claim_struct["actions"]

        and

        evidence_struct["actions"]

    ):

        shared_actions = (

            set(claim_struct["actions"])
            &
            set(evidence_struct["actions"])

        )

        if shared_actions:

            score += 4

    # =================================================
    # CONFLICT DETECTION
    # =================================================

    conflicts = detect_conflicts(

        claim_struct,

        evidence_struct
    )

    for conflict in conflicts:

        if conflict == "action_conflict":

            score -= 6

        elif conflict == "year_conflict":

            score -= 5

        elif conflict == "number_conflict":

            score -= 3

        elif conflict == "negation_conflict":

            score -= 8

        elif conflict == "recycled_news_conflict":

            score -= 5

        elif conflict == "stale_context_conflict":

            score -= 6

    # =================================================
    # RECENCY BONUS
    # =================================================

    if (

        claim_struct["recency_terms"]

        and

        evidence_struct["years"]
    ):

        try:

            latest_year = max(

                int(y)
                for y in evidence_struct["years"]
            )

            if latest_year >= CURRENT_YEAR - 1:

                score += 2

        except:
            pass

    # =================================================
    # RETURN
    # =================================================

    return {

        "score": round(score, 3),

        "claim": claim_struct,

        "evidence": evidence_struct,

        "conflicts": conflicts,

        "conflict_count": len(
            conflicts
        )
    }
