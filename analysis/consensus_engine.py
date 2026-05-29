def compute_consensus(
    evidence_list
):

    entailment = 0

    contradiction = 0

    neutral = 0

    # ==========================================
    # COUNT LABELS
    # ==========================================

    for evidence in evidence_list:

        score = evidence.final_score

        if evidence.nli_label == "ENTAILMENT":

            entailment += score

        elif evidence.nli_label == "CONTRADICTION":

            contradiction += score

        else:

            neutral += score

    # ==========================================
    # TOTAL
    # ==========================================

    total = (

        entailment

        + contradiction

        + neutral
    )

    if total == 0:

        return {

            "winner": "NEUTRAL",

            "strength": 0
        }

    # ==========================================
    # NORMALIZE
    # ==========================================

    entailment_ratio = (
        entailment / total
    )

    contradiction_ratio = (
        contradiction / total
    )

    neutral_ratio = (
        neutral / total
    )

    # ==========================================
    # DECISION
    # ==========================================

    ratios = {

        "ENTAILMENT": entailment_ratio,

        "CONTRADICTION": contradiction_ratio,

        "NEUTRAL": neutral_ratio
    }

    winner = max(
        ratios,
        key=ratios.get
    )

    strength = ratios[winner]

    return {

        "winner": winner,

        "strength": strength,

        "ratios": ratios
    }
