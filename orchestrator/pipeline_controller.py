from analysis.evidence_scorer import (
    compute_evidence_score
)

from analysis.consensus_engine import (
    compute_consensus
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

        # ======================================
        # QUALITY FILTERING
        # ======================================

        weak_alignment = (
            scored.alignment_score < 0.35
        )

        weak_fact_match = (
            scored.fact_score < 5
        )

        weak_rerank = (
            scored.reranker_score < 1
        )

        weak_content = (
            len(scored.content.split()) < 10
        )

        # --------------------------------------
        # DROP VERY WEAK EVIDENCE
        # --------------------------------------

        if (
            weak_alignment
            or
            weak_fact_match
            or
            weak_rerank
            or
            weak_content
        ):
            continue

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
    # CONSENSUS ANALYSIS
    # ==========================================

    consensus = compute_consensus(
        scored_evidence[:10]
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

    # ==========================================
    # WEIGHTED LABEL SCORES
    # ==========================================

    entailment_score = 0

    contradiction_score = 0

    neutral_score = 0

    # ==========================================
    # TRUSTED EVIDENCE ONLY
    # ==========================================

    trusted_evidence = []

    for evidence in scored_evidence[:5]:

        if (

            evidence.final_score >= 20

            and

            evidence.alignment_score >= 0.45

        ):

            trusted_evidence.append(
                evidence
            )

    # ==========================================
    # LABEL ANALYSIS
    # ==========================================

    for evidence in trusted_evidence:

        if evidence.nli_label == "ENTAILMENT":

            entailment_count += 1

            entailment_score += (
                evidence.final_score
            )

        elif evidence.nli_label == "CONTRADICTION":

            contradiction_count += 1

            contradiction_score += (
                evidence.final_score
            )

        else:

            neutral_count += 1

            neutral_score += (
                evidence.final_score
            )

    # ==========================================
    # WEIGHTED VOTING
    # ==========================================

    label_scores = {

        "ENTAILMENT": entailment_score,

        "NEUTRAL": neutral_score,

        "CONTRADICTION": contradiction_score
    }

    weighted_winner = max(

        label_scores,

        key=label_scores.get
    )

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

    verdict = weighted_winner

    # ==========================================
    # STRONG ENTAILMENT OVERRIDE
    # ==========================================

    strong_entailments = [

        e for e in trusted_evidence

        if (

            e.nli_label == "ENTAILMENT"

            and

            e.final_score >= 30

            and

            e.alignment_score >= 0.60

            and

            e.fact_score >= 10
        )
    ]

    if len(strong_entailments) >= 1:

        verdict = "ENTAILMENT"

    # ==========================================
    # STRONG CONTRADICTION OVERRIDE
    # ==========================================

    strong_contradictions = [

        e for e in trusted_evidence

        if (

            e.nli_label == "CONTRADICTION"

            and

            e.final_score >= 30

            and

            e.alignment_score >= 0.60

            and

            e.fact_score >= 10
        )
    ]

    if len(strong_contradictions) >= 1:

        verdict = "CONTRADICTION"

    # ==========================================
    # FALLBACK MAJORITY LOGIC
    # ==========================================

    if verdict == "NEUTRAL":

        if entailment_count >= 2:

            verdict = "ENTAILMENT"

        elif contradiction_count >= 2:

            verdict = "CONTRADICTION"

    # ==========================================
    # HIGH CONFIDENCE OVERRIDE
    # ==========================================

    if (

        top.nli_label == "ENTAILMENT"

        and

        top.final_score >= 35

        and

        top.alignment_score >= 0.65

        and

        top.fact_score >= 12

    ):

        verdict = "ENTAILMENT"

    # ==========================================
    # CONFIDENCE
    # ==========================================

    confidence = min(

        1.0,

        (
            (
                top.final_score
                /
                40
            )
            * 0.5
            +
            consensus["strength"]
            * 0.3
            +
            (
                label_scores.get(
                    verdict,
                    0
                )
                /
                100
            )
            * 0.2
        )
    )

    # ==========================================
    # RETURN
    # ==========================================

    return {

        "verdict": verdict,

        "confidence": confidence,

        "top_evidence": top,

        "margin": margin,

        "consensus": consensus,

        "label_scores": label_scores,

        "trusted_evidence_count": len(
            trusted_evidence
        )
    }
