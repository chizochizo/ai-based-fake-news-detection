import gradio as gr
from orchestrator.pipeline_controller import VerificationPipeline

# =====================================================
# INITIALIZE PIPELINE
# =====================================================

pipeline = VerificationPipeline()


# =====================================================
# MAIN VERIFICATION FUNCTION
# =====================================================

def verify_claim(claim):
    if not claim.strip():
        return (
            "Please enter a claim.",
            "",
            "",
            "",
            "",
            ""
        )

    try:
        result = pipeline.run(claim)

        # ==========================================
        # FINAL VERDICT
        # ==========================================
        verdict = (
            f"### FINAL VERDICT\n\n"
            f"**{result.final_verdict}**\n\n"
            f"Confidence: {round(result.confidence_score, 3)}\n\n"
            f"## Explanation\n\n"
            f"{result.verdict_explanation}"
        )

        # ==========================================
        # REPORT
        # ==========================================
        report = result.final_report

        # ==========================================
        # QUERIES
        # ==========================================
        queries = "\n".join(result.retrieval_queries)

        # ==========================================
        # TOP EVIDENCE
        # ==========================================
        evidence_output = ""
        for idx, evidence in enumerate(result.ranked_evidence[:5], start=1):
            evidence_output += (
                f"## Evidence {idx}\n\n"
                f"### Title\n{evidence.title}\n\n"
                f"### Content\n{evidence.content}\n\n"
                f"### Source\n{evidence.source_url}\n\n"
                f"### Scores\n"
                f"- Reranker: {round(getattr(evidence, 'reranker_score', 0), 3)}\n"
                f"- Alignment: {round(getattr(evidence, 'alignment_score', 0), 3)}\n"
                f"- Fact Score: {round(getattr(evidence, 'fact_score', 0), 3)}\n"
                f"- Final Score: {round(getattr(evidence, 'final_score', 0), 3)}\n\n"
                f"{'-'*60}\n\n"
            )

        # ==========================================
        # NLI ANALYSIS
        # ==========================================
        nli_output = ""
        for idx, evidence in enumerate(result.nli_results[:5], start=1):
            nli_output += (
                f"## NLI Result {idx}\n\n"
                f"### Label\n{evidence.nli_label}\n\n"
                f"### Confidence\n{round(evidence.nli_confidence, 3)}\n\n"
                f"### Alignment\n{round(getattr(evidence, 'alignment_score', 0), 3)}\n\n"
                f"### Fact Score\n{round(getattr(evidence, 'fact_score', 0), 3)}\n\n"
                f"### Final Score\n{round(getattr(evidence, 'final_score', 0), 3)}\n\n"
                f"### Content\n{evidence.content[:500]}\n\n"
                f"{'-'*60}\n\n"
            )

        # ==========================================
        # DEBUG INFO
        # ==========================================
        debug_output = (
            f"## CLAIM FRAME\n\n{result.claim_frame}\n\n"
            f"## DECOMPOSITION\n\n{result.decomposition}\n\n"
            f"## ENTITIES\n\n{result.entities}\n"
        )

        return (
            verdict,
            report,
            queries,
            evidence_output,
            nli_output,
            debug_output
        )

    except Exception as e:
        return (
            f"Error: {str(e)}",
            "",
            "",
            "",
            "",
            ""
        )


# =====================================================
# GRADIO UI
# =====================================================

with gr.Blocks(title="AI Fake News Verification System") as demo:
    gr.Markdown(
        """
        # AI Fake News Verification System
        Advanced Retrieval-Augmented Semantic Fake News Detection & Verification
        """
    )

    with gr.Row():
        claim_input = gr.Textbox(
            label="Enter Claim",
            placeholder="Type a news claim here...",
            lines=4
        )

    with gr.Row():
        verify_button = gr.Button("Chalo")
        clear_button = gr.Button("Hatai Diwi")

    with gr.Tab("Final Verdict"):
        verdict_output = gr.Markdown()

    with gr.Tab("Verification Report"):
        report_output = gr.Markdown()

    with gr.Tab("Generated Queries"):
        queries_output = gr.Textbox(lines=10)

    with gr.Tab("Top Evidence"):
        evidence_output = gr.Markdown()

    with gr.Tab("NLI Analysis"):
        nli_output = gr.Markdown()

    with gr.Tab("Debug Information"):
        debug_output = gr.Markdown()

    # Click interactions mapped cleanly inside the context block
    verify_button.click(
        fn=verify_claim,
        inputs=claim_input,
        outputs=[
            verdict_output,
            report_output,
            queries_output,
            evidence_output,
            nli_output,
            debug_output
        ]
    )

    clear_button.click(
        fn=lambda: ("", "", "", "", "", "", ""),
        inputs=[],
        outputs=[
            claim_input,
            verdict_output,
            report_output,
            queries_output,
            evidence_output,
            nli_output,
            debug_output
        ]
    )


# =====================================================
# LAUNCH
# =====================================================

if __name__ == "__main__":
    demo.launch(share=True)
