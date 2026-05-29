from understanding.query_planner import (
    build_search_queries
)
from retrieval.hybrid_retriever import (
    retrieve_evidence
)
from analysis.verdict_aggregator import (
    aggregate_verdicts
)
from analysis.report_generator import (
    build_report
)
from types import SimpleNamespace


# =====================================================
# MAIN VERIFICATION PIPELINE
# =====================================================

class VerificationPipeline:

    def __init__(self):

        pass

    # =================================================
    # RUN PIPELINE
    # =================================================

    def run(
        self,
        claim
    ):

        # =============================================
        # BASIC DECOMPOSITION PLACEHOLDER
        # =============================================

        decomposition = {

            "entities": [],

            "noun_chunks": [],

            "actions": []
        }

        # =============================================
        # QUERY GENERATION
        # =============================================

        queries = build_search_queries(

            claim,

            decomposition
        )

        # =============================================
        # RETRIEVAL
        # =============================================

        retrieval_result = retrieve_evidence(

            claim=claim,

            queries=queries
        )

        evidence = retrieval_result.get(
            "evidence",
            []
        )

        # =============================================
        # VERDICT AGGREGATION
        # =============================================

        verdict_result = aggregate_verdicts(

            claim,

            evidence
        )

        # =============================================
        # BUILD STATE OBJECT
        # =============================================

        state = SimpleNamespace(

            claim=claim,

            retrieval_queries=queries,

            ranked_evidence=evidence,

            nli_results=evidence,

            final_verdict=verdict_result.get(
                "verdict",
                "NEUTRAL"
            ),

            confidence_score=verdict_result.get(
                "confidence",
                0.0
            ),

            decomposition=decomposition,

            claim_frame=None,

            entities=decomposition.get(
                "entities",
                []
            ),

            stage_logs=retrieval_result.get(
                "stage_logs",
                []
            ),

            engines_used=retrieval_result.get(
                "engines_used",
                []
            ),

            consensus=verdict_result.get(
                "consensus",
                {}
            )
        )

        # =============================================
        # REPORT GENERATION
        # =============================================

        report = build_report(
            state
        )

        state.final_report = report

        # =============================================
        # RETURN
        # =============================================

        return state
