from sentence_transformers import CrossEncoder


reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank_evidence(
    claim,
    evidence_list
):

    pairs = []

    for evidence in evidence_list:

        pairs.append([
            claim,
            evidence.content
        ])
    print(
        f"[RERANKING] {len(evidence_list)} items"
    )
    scores = reranker.predict(
        pairs
    )

    scored = list(
        zip(
            evidence_list,
            scores
        )
    )

    scored.sort(
        key=lambda x: x[1],
        reverse=True
    )

    ranked_evidence = []

    for evidence, score in scored:

        evidence.reranker_score = (
            float(score)
        )

        ranked_evidence.append(
            evidence
        )

    return ranked_evidence
