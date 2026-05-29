from rapidfuzz import fuzz
import spacy
import re
from datetime import datetime


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
    "ceremony"
}

# =====================================================
# ENTITY WEIGHTS
# =====================================================

ENTITY_WEIGHTS = {

    "ORG": 3.0,

    "PERSON": 3.0,

    "GPE": 2.5,

    "LOC": 2.5,

    "DATE": 3.5,

    "TIME": 2.0,

    "CARDINAL": 2.5,

    "ORDINAL": 3.0,

    "EVENT": 3.0,

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
    "withdrawn"
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
    "lost": "lose"
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

    "approve": [
        "reject",
        "deny"
    ]
}


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

    for ent in doc.ents:

        structure["entities"].append({

            "text": ent.text.lower(),

            "label": ent.label_
        })

    # ==========================================
    # NUMBERS
    # ==========================================

    numbers = re.findall(
        r"\b\d+(?:st|nd|rd|th)?\b",
        text.lower()
    )

    structure["numbers"] = numbers

    # ==========================================
    # YEARS
    # ==========================================

    structure["years"] = extract_years(
        text
    )

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

    for token in doc:

        if token.pos_ == "VERB":

            normalized = normalize_action(
                token.lemma_.lower()
            )

            structure["actions"].append(
                normalized
            )

    # ==========================================
    # EVENT TERMS
    # ==========================================

    for token in doc:

        if token.lemma_.lower() in EVENT_TERMS:

            structure["event_terms"].append(
                token.lemma_.lower()
            )

    # ==========================================
    # NOUN CHUNKS
    # ==========================================

    for chunk in doc.noun_chunks:

        structure["noun_chunks"].append(
            chunk.text.lower()
        )

    return structure


def has_entity_overlap(
    claim_entities,
    evidence_entities
):

    for claim_ent in claim_entities:

        for evidence_ent in evidence_entities:

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

                # old article framed as current

                if age >= 2:

                    conflicts.append(
                        "recycled_news_conflict"
                    )

            except:
                pass

    return list(set(conflicts))


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

    if (

        claim_numbers

        and

        evidence_numbers

        and

        not (
            claim_numbers
            &
            evidence_numbers
        )
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

    if (

        claim_years

        and

        evidence_years

        and

        not (
            claim_years
            &
            evidence_years
        )
    ):

        conflicts.append(
            "year_conflict"
        )

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

    for claim_ent in claim_struct["entities"]:

        for evidence_ent in evidence_struct["entities"]:

            similarity = fuzz.token_sort_ratio(

                claim_ent["text"],

                evidence_ent["text"]

            )

            if similarity >= 85:

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

    action_overlap = len(

        set(claim_struct["actions"])
        &
        set(evidence_struct["actions"])

    )

    score += action_overlap * 2.5

    # =================================================
    # EVENT TERM MATCHING
    # =================================================

    event_overlap = len(

        set(claim_struct["event_terms"])
        &
        set(evidence_struct["event_terms"])

    )

    score += event_overlap * 3

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

            score += 2

        else:

            score -= 2

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

            score += 3

        else:

            score -= 4

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

    score += best_chunk_score * 4

    # =================================================
    # CONFLICT DETECTION
    # =================================================

    conflicts = detect_conflicts(

        claim_struct,

        evidence_struct
    )

    for conflict in conflicts:

        if conflict == "action_conflict":

            score -= 5

        elif conflict == "year_conflict":

            score -= 4

        elif conflict == "number_conflict":

            score -= 3

        elif conflict == "negation_conflict":

            score -= 6

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

        latest_year = max(

            int(y)
            for y in evidence_struct["years"]
        )

        if latest_year >= CURRENT_YEAR - 1:

            score += 2

    # =================================================
    # RETURN
    # =================================================

    return {

        "score": score,

        "claim": claim_struct,

        "evidence": evidence_struct,

        "conflicts": conflicts,

        "conflict_count": len(
            conflicts
        )
    }
