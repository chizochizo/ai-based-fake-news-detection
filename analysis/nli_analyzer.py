import traceback
from transformers import pipeline


# =====================================================
# LOAD NLI MODEL
# =====================================================

print("\nLOADING NLI MODEL...\n")

nli_pipeline = pipeline(

    "text-classification",

    model="roberta-large-mnli",

    device=-1
)

print("\nNLI MODEL LOADED\n")


# =====================================================
# LABEL NORMALIZATION
# =====================================================

LABEL_MAP = {

    "LABEL_0": "CONTRADICTION",
    "LABEL_1": "NEUTRAL",
    "LABEL_2": "ENTAILMENT",

    "contradiction": "CONTRADICTION",
    "neutral": "NEUTRAL",
    "entailment": "ENTAILMENT",

    "CONTRADICTION": "CONTRADICTION",
    "NEUTRAL": "NEUTRAL",
    "ENTAILMENT": "ENTAILMENT"
}


# =====================================================
# LABEL CALIBRATION
# =====================================================

def calibrate_nli_label(
    raw_label,
    confidence,
    alignment_score,
    fact_score
):

    label = LABEL_MAP.get(
        raw_label,
        "NEUTRAL"
    )

    # ==========================================
    # ENTAILMENT BOOSTING
    # ==========================================

    if (

        label == "NEUTRAL"

        and

        alignment_score > 0.45

        and

        fact_score > 15

        and

        confidence > 0.90

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


# =====================================================
# MAIN NLI ANALYSIS
# =====================================================

def analyze_claim_evidence(
    claim,
    evidence_list
):

    analyzed = []

    for evidence in evidence_list:

        try:

            print("\n[NLI INPUT]")
            print("CLAIM:", claim)
            print("EVIDENCE:", evidence.content)

            result = nli_pipeline(
                {
                    "text": claim,
                    "text_pair": evidence.content
                }
            )
            if isinstance(result, list):
                result = result[0]

            print("\n[NLI RAW RESULT]")
            print(result)

            raw_label = result.get(
                "label",
                "NEUTRAL"
            )

            confidence = float(
                result.get(
                    "score",
                    0.0
                )
            )
            print("\n[NLI DEBUG]")
            print("RAW LABEL:", raw_label)
            print("CONFIDENCE:", confidence)
            print(
                "ALIGNMENT:",
                getattr(
                    evidence,
                    "alignment_score",
                    0
                )
            )
            print(
                "FACT SCORE:",
                getattr(
                    evidence,
                    "fact_score",
                    0
                )
            )

            calibrated_label = calibrate_nli_label(

                raw_label=raw_label,

                confidence=confidence,

                alignment_score=getattr(
                    evidence,
                    "alignment_score",
                    0
                ),

                fact_score=getattr(
                    evidence,
                    "fact_score",
                    0
                )
            )
            print(

                "CALIBRATED LABEL:",
                calibrated_label
            )

            evidence.nli_label = calibrated_label

            evidence.nli_confidence = confidence

        except Exception as e:

            print("\nNLI ERROR:")
            print(e)

            traceback.print_exc()

            evidence.nli_label = "NEUTRAL"

            evidence.nli_confidence = 0.0

        analyzed.append(
            evidence
        )

    return analyzed
