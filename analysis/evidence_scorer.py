from analysis.semantic_alignment import (
    compute_alignment_score
)

from analysis.fact_matcher import (
    compare_fact_structure
)


def compute_evidence_score(
    claim,
    evidence
):

    # ==========================================
    # RERANK SCORE
    # ==========================================

    rerank_score = max(
        evidence.reranker_score,
        0
    )

    # ==========================================
    # NLI CONFIDENCE
    # ==========================================

    nli_score = (
        evidence.nli_confidence
    )

    # ==========================================
    # SEMANTIC ALIGNMENT
    # ==========================================

    alignment = (
        compute_alignment_score(
            claim,
            evidence.content
        )
    )

    # ==========================================
    # FACT STRUCTURE MATCHING
    # ==========================================

    fact_match = compare_fact_structure(

        claim,

        evidence.content
    )

    fact_score = fact_match["score"]

    # ==========================================
    # LABEL BONUS
    # ==========================================

    label_bonus = 0

    if evidence.nli_label == "ENTAILMENT":

        label_bonus = 2.0

    elif evidence.nli_label == "CONTRADICTION":

        label_bonus = -1.5

    # ==========================================
    # FINAL COMBINED SCORE
    # ==========================================

    combined = (

        rerank_score * 0.30

        +

        nli_score * 0.20

        +

        alignment * 3.0

        +

        fact_score * 1.5

        +

        label_bonus
    )

    # ==========================================
    # STORE SCORES
    # ==========================================

    evidence.final_score = combined

    evidence.alignment_score = (
        alignment
    )

    evidence.fact_score = (
        fact_score
    )

    evidence.fact_match = (
        fact_match
    )

    return evidence
