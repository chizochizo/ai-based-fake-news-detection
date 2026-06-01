from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank_evidence(claim, evidence_list):
    pairs = []
    for evidence in evidence_list:
        pairs.append([claim, f"title: {evidence.title} {evidence.content}"])

    print(f"[RERANKING] {len(evidence_list)} items")
    scores = reranker.predict(pairs)

    scored = list(zip(evidence_list, scores))
    scored.sort(key=lambda x: x[1], reverse=True)

    ranked_evidence = []
    for evidence, score in scored:
        score = float(score)
        url = evidence.source_url.lower()

        # Source domain authority heuristic weighting
        if ".gov" in url:
            score += 2.0
        elif "wikipedia.org" in url:
            score += 1.5
        elif "britannica.com" in url:
            score += 1.5
        elif ".edu" in url:
            score += 1.0
        elif "facebook.com" in url:
            score -= 5.0
        elif "instagram.com" in url:
            score -= 5.0
        elif "youtube.com" in url:
            score -= 3.0

        evidence.reranker_score = score
        ranked_evidence.append(evidence)

    # Re-sort ranked_evidence if you want the domain weights to affect final ranking order
    ranked_evidence.sort(key=lambda x: x.reranker_score, reverse=True)

    return ranked_evidence
