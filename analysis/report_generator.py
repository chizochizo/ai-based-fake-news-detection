def build_report(state):

    lines = []

    lines.append(
        f"Verdict: {state.final_verdict}"
    )

    lines.append(
        f"Confidence: {round(state.confidence_score, 3)}"
    )

    lines.append("\nTop Evidence:\n")

    for evidence in state.nli_results[:3]:

        lines.append(
            f"- {evidence.title}"
        )

        lines.append(
            f"  Label: {evidence.nli_label}"
        )

        lines.append(
            f"  Final Score: "
            f"{round(evidence.final_score, 3)}"
        )

        lines.append(
            f"  Source: "
            f"{evidence.source_url}"
        )

        lines.append("")

    return "\n".join(lines)
