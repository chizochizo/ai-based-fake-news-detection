import re

import spacy

from rapidfuzz import fuzz


nlp = spacy.load(
    "en_core_web_sm"
)


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


def extract_fact_structure(text):

    doc = nlp(text)

    structure = {

        "entities": [],

        "numbers": [],

        "actions": [],

        "event_terms": [],

        "noun_chunks": []
    }

    # ==========================================
    # ENTITIES
    # ==========================================

    for ent in doc.ents:

        structure["entities"].append(
            ent.text.lower()
        )

    # ==========================================
    # NUMBERS
    # ==========================================

    numbers = re.findall(
        r"\b\d+(?:st|nd|rd|th)?\b",
        text.lower()
    )

    structure["numbers"] = numbers

    # ==========================================
    # ACTIONS
    # ==========================================

    for token in doc:

        if token.pos_ == "VERB":

            structure["actions"].append(
                token.lemma_.lower()
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

    entity_overlap = len(

        set(claim_struct["entities"])
        &
        set(evidence_struct["entities"])

    )

    score += entity_overlap * 1.5

    # =================================================
    # ACTION MATCHING
    # =================================================

    action_overlap = len(

        set(claim_struct["actions"])
        &
        set(evidence_struct["actions"])

    )

    score += action_overlap * 2

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

            score += 1

        else:

            score -= 0.5

    # =================================================
    # NOUN CHUNK SEMANTIC MATCH
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

    return {

        "score": score,

        "claim": claim_struct,

        "evidence": evidence_struct
    }
