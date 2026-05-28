from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class ExecutionState:

    # =====================================================
    # INPUT
    # =====================================================

    claim: str = ""

    # =====================================================
    # UNDERSTANDING
    # =====================================================

    decomposition: Dict[str, Any] = field(
        default_factory=dict
    )

    entities: List[Dict] = field(
        default_factory=list
    )

    retrieval_queries: List[str] = field(
        default_factory=list
    )

    # =====================================================
    # RETRIEVAL
    # =====================================================

    raw_evidence: List[Dict] = field(
        default_factory=list
    )

    ranked_evidence: List[Dict] = field(
        default_factory=list
    )

    # =====================================================
    # ANALYSIS
    # =====================================================

    semantic_results: List[Dict] = field(
        default_factory=list
    )

    nli_results: List[Dict] = field(
        default_factory=list
    )

    contradiction_results: Dict = field(
        default_factory=dict
    )

    consensus_results: Dict = field(
        default_factory=dict
    )

    forensic_results: Dict = field(
        default_factory=dict
    )

    temporal_results: Dict = field(
        default_factory=dict
    )

    # =====================================================
    # REASONING
    # =====================================================

    judge_results: Dict = field(
        default_factory=dict
    )

    calibrated_results: Dict = field(
        default_factory=dict
    )

    # =====================================================
    # FINAL OUTPUT
    # =====================================================

    final_verdict: str = "UNKNOWN"

    confidence_score: float = 0.0

    final_report: str = ""
