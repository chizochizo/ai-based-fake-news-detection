# =====================================================
# REPORT GENERATOR
# =====================================================


def build_report(state):

    lines = []

    # =================================================
    # HEADER
    # =================================================

    lines.append(
        f"Verdict: {state.final_verdict}"
    )

    lines.append(
        f"Confidence: "
        f"{round(state.confidence_score, 3)}"
    )

    lines.append("\nTop Evidence:\n")

    # =================================================
    # QWEN JUDGE (Fixed Indentation & List Integration)
    # =================================================

    lines.append("\n")
    lines.append("============================\n")
    lines.append("QWEN JUDGE\n")
    lines.append("============================\n")

    if hasattr(state, "qwen_judge"):

        lines.append(
            f"Verdict: "
            f"{state.qwen_judge.get('verdict', 'UNKNOWN')}\n"
        )

        lines.append(
            f"Reason: "
            f"{state.qwen_judge.get('reason', '')}\n"
        )

    # =================================================
    # EVIDENCE
    # =================================================

    for evidence in state.nli_results[:3]:

        title = getattr(
            evidence,
            "title",
            "Unknown Title"
        )

        label = getattr(
            evidence,
            "nli_label",
            "NEUTRAL"
        )

        final_score = getattr(
            evidence,
            "final_score",
            0
        )

        source_url = getattr(
            evidence,
            "source_url",
            "Unknown Source"
        )

        lines.append(
            f"- {title}"
        )

        lines.append(
            f"  Label: {label}"
        )

        lines.append(
            f"  Final Score: "
            f"{round(final_score, 3)}"
        )

        lines.append(
            f"  Source: "
            f"{source_url}"
        )

        lines.append("")

    # =================================================
    # RETURN
    # =================================================

    return "\n".join(lines)
