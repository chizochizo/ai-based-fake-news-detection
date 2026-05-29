
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
