from transformers import pipeline


nli_pipeline = pipeline(

    "text-classification",

    model="roberta-large-mnli",

    device=-1
)


LABEL_MAP = {

    "LABEL_0": "CONTRADICTION",

    "LABEL_1": "NEUTRAL",

    "LABEL_2": "ENTAILMENT"
}


def calibrate_nli_label(
    raw_label,
    confidence,
    alignment_score,
    fact_score
):

    label = LABEL_MAP.get(
        raw_label,
        raw_label
    )

    # ==========================================
    # ENTAILMENT BOOSTING
    # ==========================================

    if (

        label == "NEUTRAL"

        and

        alignment_score > 0.65

        and

        fact_score > 12

        and

        confidence > 0.80

    ):

        label = "ENTAILMENT"

    # ==========================================
    # WEAK CONTRADICTION FILTER
    # ==========================================

    if (

        label == "CONTRADICTION"

        and

        alignment_score < 0.45

    ):

        label = "NEUTRAL"

    return label


def analyze_claim_evidence(
    claim,
    evidence_list
):

    analyzed = []

    for evidence in evidence_list:

        result = nli_pipeline(

            f"{claim} </s></s> {evidence.content}"

        )[0]

        raw_label = result["label"]

        confidence = result["score"]

        calibrated_label = calibrate_nli_label(

            raw_label=raw_label,

            confidence=confidence,

            alignment_score=evidence.alignment_score,

            fact_score=evidence.fact_score
        )

        evidence.nli_label = calibrated_label

        evidence.nli_confidence = confidence

        analyzed.append(
            evidence
        )

    return analyzed
