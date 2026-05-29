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
    # SAFETY CHECK
    # ==========================================

    if not scored_evidence:

        return {

            "verdict": "NEUTRAL",

            "confidence": 0.0,

            "top_evidence": None,

            "margin": 0
        }

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
    # LABEL COUNTS
    # ==========================================

    entailment_count = 0

    contradiction_count = 0

    neutral_count = 0

    for evidence in scored_evidence[:5]:

        if evidence.nli_label == "ENTAILMENT":

            entailment_count += 1

        elif evidence.nli_label == "CONTRADICTION":

            contradiction_count += 1

        else:

            neutral_count += 1

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
    # INITIAL LABEL
    # ==========================================

    verdict = top.nli_label

    # ==========================================
    # STRONG ENTAILMENT RULE
    # ==========================================

    if (

        entailment_count >= 2

        and

        top.alignment_score > 0.60

        and

        top.fact_score > 10

    ):

        verdict = "ENTAILMENT"

    # ==========================================
    # STRONG CONTRADICTION RULE
    # ==========================================

    if (

        contradiction_count >= 2

        and

        top.alignment_score > 0.60

    ):

        verdict = "CONTRADICTION"

    # ==========================================
    # OVERRIDE NEUTRAL
    # ==========================================

    if (

        top.final_score > 25

        and

        top.alignment_score > 0.65

        and

        top.fact_score > 12

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

    # ==========================================
    # RETURN
    # ==========================================

    return {

        "verdict": verdict,

        "confidence": confidence,

        "top_evidence": top,

        "margin": margin
    }
