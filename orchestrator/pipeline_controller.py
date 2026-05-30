from types import SimpleNamespace
from analysis.qwen_judge import run_qwen_judge
from analysis.report_generator import build_report
from analysis.verdict_aggregator import aggregate_verdicts
from analysis.verdict_explainer import generate_verdict_explanation
from retrieval.hybrid_retriever import retrieve_evidence
from understanding.claim_decomposer import decompose_claim
from understanding.query_planner import build_search_queries

# =====================================================
# MAIN VERIFICATION PIPELINE
# =====================================================


class VerificationPipeline:

    def __init__(self):
        pass

    # =================================================
    # RUN PIPELINE
    # =================================================

    def run(self, claim):

        # =============================================
        # BASIC DECOMPOSITION PLACEHOLDER
        # =============================================

        decomposition = decompose_claim(claim)

        # =============================================
        # QUERY GENERATION
        # =============================================

        queries = build_search_queries(claim, decomposition)

        # =============================================
        # RETRIEVAL
        # =============================================

        retrieval_result = retrieve_evidence(claim=claim, queries=queries)

        evidence = retrieval_result.get("evidence", [])

        # =============================================
        # VERDICT AGGREGATION
        # =============================================

        verdict_result = aggregate_verdicts(claim, evidence)

        # =============================================
        # QWEN JUDGE (Fixed Indentation)
        # =============================================

        qwen_result = run_qwen_judge(
            claim=claim,
            system_verdict=verdict_result.get("verdict", "NEUTRAL"),
            confidence=verdict_result.get("confidence", 0.0),
            evidence_list=evidence,
        )

        print("\n[QWEN JUDGE]")
        print(qwen_result)

        explanation = generate_verdict_explanation(
            claim=claim,
            verdict=verdict_result.get("verdict", "NEUTRAL"),
            evidence_list=evidence,
        )

        # =============================================
        # BUILD STATE OBJECT
        # =============================================

        state = SimpleNamespace(
            claim=claim,
            retrieval_queries=queries,
            ranked_evidence=evidence,
            nli_results=evidence,
            qwen_judge=qwen_result,
            final_verdict=verdict_result.get("verdict", "NEUTRAL"),
            confidence_score=verdict_result.get("confidence", 0.0),
            verdict_explanation=explanation,
            decomposition=decomposition,
            claim_frame=None,
            entities=decomposition.get("entities", []),
            stage_logs=retrieval_result.get("stage_logs", []),
            engines_used=retrieval_result.get("engines_used", []),
            consensus=verdict_result.get("consensus", {}),
        )

        # =============================================
        # REPORT GENERATION
        # =============================================

        report = build_report(state)

        state.final_report = report

        # =============================================
        # RETURN
        # =============================================

        return state
