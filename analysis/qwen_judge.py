import re
import subprocess


# =====================================================
# HELPERS
# =====================================================

def clean_ansi(text):
    """Removes ANSI escape codes (colors, cursor movements) from text."""
    ansi_escape = re.compile(
        r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])'
    )
    return ansi_escape.sub('', text)


# =====================================================
# QWEN JUDGE
# =====================================================

def run_qwen_judge(
    claim,
    system_verdict,
    confidence,
    evidence_list
):
    try:
        # ==========================================
        # BUILD EVIDENCE SUMMARY
        # ==========================================
        evidence_text = ""

        for i, evidence in enumerate(evidence_list[:5], start=1):
            title = getattr(
                evidence,
                "title",
                ""
            )

            content = getattr(
                evidence,
                "content",
                ""
            )

            label = getattr(
                evidence,
                "nli_label",
                "UNKNOWN"
            )

            evidence_text += (
                f"\nEvidence {i}\n"
                f"Title: {title}\n"
                f"Label: {label}\n"
                f"Content: {content[:500]}\n"
            )

        # ==========================================
        # PROMPT
        # ==========================================
        prompt = f"""
You are a fact-checking judge.

Claim:
{claim}

System Verdict:
{system_verdict}

System Confidence:
{confidence}

Evidence:
{evidence_text}

Your task:

1. Review the evidence.
2. Decide whether the claim is:
   SUPPORTED
   REFUTED
   NOT_ENOUGH_INFORMATION

3. Return ONLY valid JSON.

Example:

{{
    "verdict": "SUPPORTED",
    "reason": "Short explanation"
}}
"""

        # ==========================================
        # OLLAMA CALL (With Timeout)
        # ==========================================
        result = subprocess.run(
            [
                "ollama",
                "run",
                "qwen2.5-coder:3b"
            ],
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60
        )

        response = result.stdout.strip()
        response = clean_ansi(response)

        print("\n[QWEN RAW RESPONSE]")
        print(response)

        # ==========================================
        # EXTRACT VERDICT + REASON
        # ==========================================
        verdict_match = re.search(
            r'"verdict"\s*:\s*"([^"]+)"',
            response,
            re.IGNORECASE
        )

        reason_match = re.search(
            r'"reason"\s*:\s*"([\s\S]*?)"',
            response,
            re.IGNORECASE
        )

        if verdict_match:
            verdict = verdict_match.group(1).strip()
            reason = ""

            if reason_match:
                reason = (
                    reason_match
                    .group(1)
                    .replace("\n", " ")
                    .replace("\r", " ")
                    .strip()
                )

            # ==========================================
            # NORMALIZE LABELS
            # ==========================================
            if verdict.upper() == "SUPPORTED":
                verdict = "ENTAILMENT"
            elif verdict.upper() == "REFUTED":
                verdict = "CONTRADICTION"
            elif verdict.upper() == "NOT_ENOUGH_INFORMATION":
                verdict = "NEUTRAL"

            return {
                "verdict": verdict,
                "reason": reason
            }

        # ==========================================
        # FALLBACK
        # ==========================================
        return {
            "verdict": "UNKNOWN",
            "reason": response
        }

    except subprocess.TimeoutExpired:
        print("\n[QWEN ERROR] Request timed out after 60 seconds.")
        return {
            "verdict": "UNKNOWN",
            "reason": "Qwen timeout"
        }

    except Exception as e:
        print("\n[QWEN ERROR]")
        print(e)

        return {
            "verdict": "UNKNOWN",
            "reason": str(e)
        }
