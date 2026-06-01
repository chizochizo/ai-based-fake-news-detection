from types import SimpleNamespace
from analysis.report_generator import build_report
from analysis.verdict_aggregator import aggregate_verdicts
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

        print("\n===== EVIDENCE BEFORE AGGREGATOR =====")

        for e in evidence:
            print(
                e.title[:80],
                "| RERANK =", getattr(e, "reranker_score", 0),
                "| NLI =", getattr(e, "nli_label", "NONE")
            )

        # =============================================
        # VERDICT AGGREGATION
        # =============================================

        verdict_result = aggregate_verdicts(claim, evidence)

        # =============================================
        # EXPLANATION FROM BEST MATCHING EVIDENCE
        # =============================================

        best_evidence = None

        for ev in evidence:
            if getattr(ev, "nli_label", None) == verdict_result["verdict"]:
                best_evidence = ev
                break

        if best_evidence:
            content_words = best_evidence.content.split()
            explanation = (
                f"{best_evidence.title}\n\n"
                f"Source: {best_evidence.source_url}\n\n"
                + " ".join(content_words[:300])
            )
        else:
            explanation = "No matching evidence available."

        # =============================================
        # BUILD STATE OBJECT
        # =============================================

        state = SimpleNamespace(
            claim=claim,
            retrieval_queries=queries,
            ranked_evidence=evidence,
            nli_results=evidence,
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
