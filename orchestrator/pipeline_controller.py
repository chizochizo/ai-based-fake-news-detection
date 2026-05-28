from orchestrator.execution_state import (
    ExecutionState
)
from understanding.claim_decomposer import (
    decompose_claim
)
from understanding.entity_resolver import (
    resolve_entities
)
from understanding.query_planner import (
    build_search_queries
)
from understanding.claim_classifier import (
    classify_claim
)
from retrieval.hybrid_retriever import (
    retrieve_evidence,
    rerank_evidence_pipeline
)
from analysis.nli_analyzer import (
    analyze_claim_evidence
)
from analysis.verdict_aggregator import (
    aggregate_verdicts
)
from understanding.claim_normalizer import (
    normalize_claim
)
from analysis.evidence_deduplicator import (
    deduplicate_evidence
)


class VerificationPipeline:

    def run(self, claim):

        state = ExecutionState()
        state.claim = claim

        # ==========================================
        # STAGE 1 — UNDERSTANDING
        # ==========================================
        self.claim_understanding(state)

        # ==========================================
        # STAGE 2 — RETRIEVAL
        # ==========================================
        self.retrieve_evidence(state)

        # ==========================================
        # STAGE 3 — ANALYSIS
        # ==========================================
        self.analyze_evidence(state)

        # ==========================================
        # STAGE 4 — REASONING
        # ==========================================
        self.reason_over_evidence(state)

        # ==========================================
        # STAGE 5 — SYNTHESIS
        # ==========================================
        self.generate_final_report(state)

        return state

    # =====================================================
    # STAGES
    # =====================================================

    def claim_understanding(self, state):

        # ==========================================
        # DECOMPOSE CLAIM
        # ==========================================
        decomposition = decompose_claim(
            state.claim
        )
        state.decomposition = decomposition

        # ==========================================
        # RESOLVE ENTITIES
        # ==========================================
        resolved_entities = resolve_entities(
            decomposition
        )
        state.entities = resolved_entities

        # ==========================================
        # BUILD SEARCH QUERIES
        # ==========================================
        queries = build_search_queries(
            state.claim,
            decomposition
        )
        state.retrieval_queries = queries

        # ==========================================
        # CLASSIFY CLAIM
        # ==========================================
        state.decomposition["claim_type"] = classify_claim(
            state.claim
        )

    def retrieve_evidence(self, state):

        # ==========================================
        # RAW RETRIEVAL
        # ==========================================
        evidence = retrieve_evidence(
            state.retrieval_queries
        )
        state.raw_evidence = evidence

        # ==========================================
        # RERANKING
        # ==========================================
        ranked = rerank_evidence_pipeline(
            state.claim,
            evidence
        )
        ranked = deduplicate_evidence(
            ranked
        )
        state.ranked_evidence = ranked

    def analyze_evidence(self, state):

        analyzed = analyze_claim_evidence(
            state.claim,
            state.ranked_evidence[:10]
        )
        state.nli_results = analyzed

        aggregated = aggregate_verdicts(
            state.claim,
            analyzed
        )

        state.final_verdict = (
            aggregated["verdict"]
        )

        state.confidence_score = (
            aggregated["confidence"]
        )

    def reason_over_evidence(self, state):
        pass

    def generate_final_report(self, state):
        pass
