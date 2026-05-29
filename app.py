import gradio as gr

from orchestrator.pipeline_controller import (
    VerificationPipeline
)


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
            f"Confidence: "
            f"{round(result.confidence_score, 3)}"
        )

        # ==========================================
        # REPORT
        # ==========================================

        report = result.final_report

        # ==========================================
        # QUERIES
        # ==========================================

        queries = "\n".join(
            result.retrieval_queries
        )

        # ==========================================
        # TOP EVIDENCE
        # ==========================================

        evidence_output = ""

        for idx, evidence in enumerate(
            result.ranked_evidence[:5],
            start=1
        ):

            evidence_output += (
                f"## Evidence {idx}\n\n"

                f"### Title\n"
                f"{evidence.title}\n\n"

                f"### Content\n"
                f"{evidence.content}\n\n"

                f"### Source\n"
                f"{evidence.source_url}\n\n"

                f"### Scores\n"
                f"- Reranker: "
                f"{round(getattr(evidence, 'reranker_score', 0), 3)}\n"

                f"- Alignment: "
                f"{round(getattr(evidence, 'alignment_score', 0), 3)}\n"

                f"- Fact Score: "
                f"{round(getattr(evidence, 'fact_score', 0), 3)}\n"

                f"- Final Score: "
                f"{round(getattr(evidence, 'final_score', 0), 3)}\n\n"

                f"{'-'*60}\n\n"
            )

        # ==========================================
        # NLI ANALYSIS
        # ==========================================

        nli_output = ""

        for idx, evidence in enumerate(
            result.nli_results[:5],
            start=1
        ):

            nli_output += (
                f"## NLI Result {idx}\n\n"

                f"### Label\n"
                f"{evidence.nli_label}\n\n"

                f"### Confidence\n"
                f"{round(evidence.nli_confidence, 3)}\n\n"

                f"### Alignment\n"
                f"{round(getattr(evidence, 'alignment_score', 0), 3)}\n\n"

                f"### Fact Score\n"
                f"{round(getattr(evidence, 'fact_score', 0), 3)}\n\n"

                f"### Final Score\n"
                f"{round(getattr(evidence, 'final_score', 0), 3)}\n\n"

                f"### Content\n"
                f"{evidence.content[:500]}\n\n"

                f"{'-'*60}\n\n"
            )

        # ==========================================
        # DEBUG INFO
        # ==========================================

        debug_output = (
            f"## CLAIM FRAME\n\n"
            f"{result.claim_frame}\n\n"

            f"## DECOMPOSITION\n\n"
            f"{result.decomposition}\n\n"

            f"## ENTITIES\n\n"
            f"{result.entities}\n"
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

with gr.Blocks(
    title="AI Fake News Verification System"
) as demo:

    gr.Markdown(
        """
# AI Fake News Verification System

Advanced Retrieval-Augmented Semantic
Fake News Detection & Verification
"""
    )

    with gr.Row():

        claim_input = gr.Textbox(

            label="Enter Claim",

            placeholder=(
                "Type a news claim here..."
            ),

            lines=4
        )

    verify_button = gr.Button(
        "Verify Claim"
    )

    with gr.Tab("Final Verdict"):

        verdict_output = gr.Markdown()

    with gr.Tab("Verification Report"):

        report_output = gr.Markdown()

    with gr.Tab("Generated Queries"):

        queries_output = gr.Textbox(
            lines=10
        )

    with gr.Tab("Top Evidence"):

        evidence_output = gr.Markdown()

    with gr.Tab("NLI Analysis"):

        nli_output = gr.Markdown()

    with gr.Tab("Debug Information"):

        debug_output = gr.Markdown()

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


# =====================================================
# LAUNCH
# =====================================================

if __name__ == "__main__":

    demo.launch(
        share=True
    )
