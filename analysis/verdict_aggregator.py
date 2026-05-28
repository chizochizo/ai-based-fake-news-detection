from analysis.evidence_scorer import (
    compute_evidence_score
)


def aggregate_verdicts(
    claim,
    evidence_list
):

    scored_evidence = []

    # ==========================================
    # SCORE ALL EVIDENCE
    # ==========================================

    for evidence in evidence_list:

        scored = compute_evidence_score(

            claim,

            evidence
        )

        scored_evidence.append(
            scored
        )

    # ==========================================
    # SORT BY FINAL SCORE
    # ==========================================

    scored_evidence.sort(

        key=lambda x: x.final_score,

        reverse=True
    )

    # ==========================================
    # TOP EVIDENCE
    # ==========================================

    top = scored_evidence[0]

    # ==========================================
    # DOMINANCE MARGIN
    # ==========================================

    second_score = 0

    if len(scored_evidence) > 1:

        second_score = (
            scored_evidence[1]
            .final_score
        )

    margin = (
        top.final_score
        -
        second_score
    )

    # ==========================================
    # LABEL DECISION
    # ==========================================

    verdict = top.nli_label

    # ==========================================
    # OVERRIDE RULES
    # ==========================================

    if (

        top.final_score > 25

        and

        top.alignment_score > 0.65

        and

        top.fact_score > 15

    ):

        if top.nli_label == "NEUTRAL":

            verdict = "ENTAILMENT"

    # ==========================================
    # CONFIDENCE
    # ==========================================

    confidence = min(

        1.0,

        (
            top.final_score
            /
            40
        )

    )

    return {

        "verdict": verdict,

        "confidence": confidence,

        "top_evidence": top,

        "margin": margin
    }
