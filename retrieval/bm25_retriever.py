import re
from rank_bm25 import BM25Okapi

STOPWORDS = {
    "the", "a", "an", "is", "was", "were",
    "be", "been", "being",
    "has", "have", "had",
    "do", "does", "did",
    "of", "in", "on", "at",
    "for", "to", "from",
    "by", "with", "and", "or", "but"
}

# =====================================================
# TOKENIZER
# =====================================================


def tokenize(text):

    if not text:

        return []

    text = text.lower()

    tokens = re.findall(

        r"\b\w+\b",

        text
    )
    tokens = [
        token
        for token in tokens
        if token not in STOPWORDS
    ]

    return tokens


# =====================================================
# BM25 RETRIEVAL
# =====================================================

def bm25_rank_evidence(
    claim,
    evidence_list,
    top_k=10
):

    if not evidence_list:

        return []

    corpus = []

    for evidence in evidence_list:

        combined = (

            f"{evidence.title} "
            f"{evidence.content}"

        )

        tokens = tokenize(
            combined
        )

        corpus.append(tokens)

    bm25 = BM25Okapi(
        corpus
    )

    query_tokens = tokenize(
        claim
    )

    scores = bm25.get_scores(
        query_tokens
    )

    scored = []

    for evidence, score in zip(
        evidence_list,
        scores
    ):

        evidence.retrieval_score = float(
            score
        )

        scored.append(
            evidence
        )

    scored.sort(

        key=lambda x: x.retrieval_score,

        reverse=True
    )

    return scored[:top_k]
