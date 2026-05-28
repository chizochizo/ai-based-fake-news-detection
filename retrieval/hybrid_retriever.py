from retrieval.web_search import (
    search_web
)

from retrieval.cross_encoder_reranker import (
    rerank_evidence
)

from retrieval.evidence_deduplicator import (
    deduplicate_evidence
)


def retrieve_evidence(
    queries
):

    all_evidence = []

    # ==========================================
    # SEARCH
    # ==========================================

    for query in queries:

        results = search_web(query)

        all_evidence.extend(
            results
        )

    # ==========================================
    # DEDUPLICATION
    # ==========================================

    unique_evidence = (
        deduplicate_evidence(
            all_evidence
        )
    )

    return unique_evidence


def rerank_evidence_pipeline(
    claim,
    evidence
):

    ranked = rerank_evidence(
        claim,
        evidence
    )

    return ranked
