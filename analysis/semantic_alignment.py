from rapidfuzz import fuzz

import spacy


nlp = spacy.load(
    "en_core_web_sm"
)


def extract_core_terms(text):

    doc = nlp(text)

    terms = []

    for token in doc:

        if token.pos_ in [

            "NOUN",
            "PROPN",
            "VERB"

        ]:

            terms.append(
                token.lemma_.lower()
            )

    return set(terms)


def compute_alignment_score(
    claim,
    evidence
):

    # ==========================================
    # FUZZY TEXT MATCH
    # ==========================================

    fuzzy = fuzz.token_sort_ratio(

        claim.lower(),

        evidence.lower()
    ) / 100.0

    # ==========================================
    # CORE TERM OVERLAP
    # ==========================================

    claim_terms = extract_core_terms(
        claim
    )

    evidence_terms = extract_core_terms(
        evidence
    )

    overlap = (
        len(
            claim_terms.intersection(
                evidence_terms
            )
        )
        /
        max(len(claim_terms), 1)
    )

    # ==========================================
    # FINAL SCORE
    # ==========================================

    final_score = (
        fuzzy * 0.5
        +
        overlap * 0.5
    )

    return final_score
