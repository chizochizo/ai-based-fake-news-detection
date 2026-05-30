import traceback
from transformers import pipeline

from understanding.claim_normalizer import (
    normalize_claim
)

# =====================================================
# LOAD NLI MODEL
# =====================================================

print("\nLOADING NLI MODEL...\n")

nli_pipeline = pipeline(

    "text-classification",

    model="roberta-large-mnli",

    device=-1,

    truncation=True,

    max_length=512
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
# EVIDENCE CLEANING
# =====================================================

def clean_evidence_text(text):

    if not text:

        return ""

    # ==========================================
    # REMOVE EXCESS WHITESPACE
    # ==========================================

    text = " ".join(
        text.split()
    )

    # ==========================================
    # REMOVE URL-LIKE GARBAGE
    # ==========================================

    text = text.replace(
        "\n",
        " "
    )

    # ==========================================
    # HARD TRUNCATION
    # ==========================================

    if len(text) > 1200:

        text = text[:1800]

    return text


# =====================================================
# SENTENCE FOCUS EXTRACTION
# =====================================================

def extract_focus_sentence(
    claim,
    evidence_text,
    top_k=3
):

    claim_words = set(

        normalize_claim(claim)
        .lower()
        .split()
    )

    sentences = [
        s.strip()
        for s in evidence_text.split(".")
        if s.strip()
    ]
    scored = []

    for sentence in sentences:

        sentence_words = set(
            sentence.lower().split()
        )

        overlap = len(
            claim_words
            &
            sentence_words
        )
        scored.append(
            (
                overlap,
                sentence
            )
        )
    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )
    selected = [
        sentence
        for overlap, sentence
        in scored[:top_k]
        if overlap > 0
    ]
    if not selected:

        return evidence_text[:1000]

    return ". ".join(
        selected
    )


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
    # STRONG ENTAILMENT BOOST
    # ==========================================

    if (

        label == "NEUTRAL"

        and

        confidence >= 0.75

        and

        alignment_score >= 0.70

        and

        fact_score >= 15

    ):

        label = "ENTAILMENT"

    # ==========================================
    # VERY STRONG MATCH OVERRIDE
    # ==========================================

    if (

        alignment_score >= 0.75

        and

        fact_score >= 15
    ):

        label = "ENTAILMENT"

    # ==========================================
    # WEAK CONTRADICTION FILTER
    # ==========================================

    if (

        label == "CONTRADICTION"

        and

        alignment_score < 0.50

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

    normalized_claim = normalize_claim(
        claim
    )

    print("\n[NORMALIZED CLAIM]")
    print(normalized_claim)

    # =================================================
    # CLAIM TRUNCATION
    # =================================================

    normalized_claim = normalized_claim[
        :300
    ]

    for evidence in evidence_list:

        try:

            # ==========================================
            # SAFETY DEFAULTS
            # ==========================================

            evidence.nli_label = "NEUTRAL"

            evidence.nli_confidence = 0.0

            raw_content = getattr(
                evidence,
                "content",
                ""
            )

            normalized_evidence = normalize_claim(
                raw_content
            )

            cleaned_evidence = clean_evidence_text(
                normalized_evidence
            )

            focused_evidence = (
                extract_focus_sentence(
                    normalized_claim,
                    cleaned_evidence,
                    top_k=3
                )
            )

            # ==========================================
            # FINAL NLI INPUT
            # ==========================================

            premise = focused_evidence

            hypothesis = normalized_claim

            print("\n[NLI INPUT]")
            print("HYPOTHESIS:", hypothesis)
            print("PREMISE:", premise)

            # ==========================================
            # RUN NLI
            # ==========================================

            pair_input = (
                premise
                +
                " </s></s> "
                +
                hypothesis
            )
            result = nli_pipeline(
                pair_input
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

            alignment_score = getattr(
                evidence,
                "alignment_score",
                0.0
            )

            fact_score = getattr(
                evidence,
                "fact_score",
                0.0
            )

            print("\n[NLI DEBUG]")
            print("RAW LABEL:", raw_label)
            print("CONFIDENCE:", confidence)
            print("ALIGNMENT:", alignment_score)
            print("FACT SCORE:", fact_score)

            calibrated_label = calibrate_nli_label(

                raw_label=raw_label,

                confidence=confidence,

                alignment_score=alignment_score,

                fact_score=fact_score
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
