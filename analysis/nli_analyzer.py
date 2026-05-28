from transformers import pipeline


nli_pipeline = pipeline(

    "text-classification",

    model="roberta-large-mnli",

    device=-1
)


def analyze_claim_evidence(
    claim,
    evidence_list
):

    analyzed = []

    for evidence in evidence_list:

        sequence = claim

        hypothesis = evidence.content

        result = nli_pipeline(

            f"{sequence} </s></s> {hypothesis}"

        )[0]

        label = result["label"]

        confidence = result["score"]

        evidence.nli_label = label

        evidence.nli_confidence = confidence

        analyzed.append(
            evidence
        )

    return analyzed