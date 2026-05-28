from dataclasses import dataclass


@dataclass
class Evidence:

    title: str

    content: str

    source_url: str

    retrieval_score: float = 0.0

    reranker_score: float = 0.0

    semantic_score: float = 0.0

    nli_label: str = "UNKNOWN"

    nli_confidence: float = 0.0
