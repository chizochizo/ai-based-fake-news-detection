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

from understanding.claim_normalizer import (
    normalize_claim
)

from analysis.claim_frame_extractor import (
    extract_claim_frame
)

from retrieval.hybrid_retriever import (
    retrieve_evidence,
    rerank_evidence_pipeline
)

from analysis.evidence_deduplicator import (
    deduplicate_evidence
)

from analysis.nli_analyzer import (
    analyze_claim_evidence
)

from analysis.verdict_aggregator import (
    aggregate_verdicts
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
        # STAGE 3 — SCORING
        # ==========================================
        self.score_evidence(state)

        # ==========================================
        # STAGE 4 — ANALYSIS
        # ==========================================
        self.analyze_evidence(state)

        # ==========================================
        # STAGE 5 — REASONING
        # ==========================================
        self.reason_over_evidence(state)

        # ==========================================
        # STAGE 6 — SYNTHESIS
        # ==========================================
        self.generate_final_report(state)

        return state

    # =====================================================
    # STAGE 1 — CLAIM UNDERSTANDING
    # =====================================================

    def claim_understanding(self, state):

        # ==========================================
        # NORMALIZE CLAIM
        # ==========================================
        state.normalized_claim = normalize_claim(
            state.claim
        )

        # ==========================================
        # DECOMPOSE CLAIM
        # ==========================================
        decomposition = decompose_claim(
            state.normalized_claim
        )

        state.decomposition = decomposition

        # ==========================================
        # CLAIM FRAME EXTRACTION
        # ==========================================
        state.claim_frame = extract_claim_frame(
            state.normalized_claim,
            state.decomposition
        )

        # ==========================================
        # ENTITY RESOLUTION
        # ==========================================
        resolved_entities = resolve_entities(
            decomposition
        )

        state.entities = resolved_entities

        # ==========================================
        # QUERY PLANNING
        # ==========================================
        queries = build_search_queries(
            state.normalized_claim,
            decomposition
        )

        state.retrieval_queries = queries

        # ==========================================
        # CLAIM CLASSIFICATION
        # ==========================================
        state.decomposition["claim_type"] = classify_claim(
            state.normalized_claim
        )

    # =====================================================
    # STAGE 2 — RETRIEVAL
    # =====================================================

    def retrieve_evidence(self, state):

        # ==========================================
        # RAW RETRIEVAL
        # ==========================================
        evidence = retrieve_evidence(
            state.retrieval_queries
        )

        state.raw_evidence = evidence

        # ==========================================
        # CROSS-ENCODER RERANKING
        # ==========================================
        ranked = rerank_evidence_pipeline(
            state.normalized_claim,
            evidence
        )

        # ==========================================
        # DEDUPLICATION
        # ==========================================
        ranked = deduplicate_evidence(
            ranked
        )

        state.ranked_evidence = ranked

    # =====================================================
    # STAGE 3 — EVIDENCE SCORING
    # =====================================================

    def score_evidence(self, state):

        from analysis.evidence_scorer import (
            compute_evidence_score
        )

        scored = []

        for evidence in state.ranked_evidence:

            scored_evidence = compute_evidence_score(

                state.normalized_claim,

                evidence
            )

            scored.append(
                scored_evidence
            )

        # ==========================================
        # SORT BY FINAL SCORE
        # ==========================================
        scored = sorted(

            scored,

            key=lambda x: x.final_score,

            reverse=True
        )

        state.ranked_evidence = scored

    # =====================================================
    # STAGE 4 — NLI ANALYSIS
    # =====================================================

    def analyze_evidence(self, state):

        analyzed = analyze_claim_evidence(

            state.normalized_claim,

            state.ranked_evidence[:10]
        )

        state.nli_results = analyzed

    # =====================================================
    # STAGE 5 — REASONING
    # =====================================================

    def reason_over_evidence(self, state):

        aggregated = aggregate_verdicts(

            state.normalized_claim,

            state.nli_results
        )

        state.final_verdict = (
            aggregated["verdict"]
        )

        state.confidence_score = (
            aggregated["confidence"]
        )

    # =====================================================
    # STAGE 6 — REPORT SYNTHESIS
    # =====================================================

    def generate_final_report(self, state):

        from analysis.report_generator import (
            build_report
        )

        state.final_report = build_report(
            state
        )
