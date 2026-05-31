import re
import subprocess
from understanding.claim_normalizer import normalize_claim

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
    normalized_claim = normalize_claim(claim)
    if not evidence_list:
        return {
            "verdict": "UNKNOWN",
            "reason": "No evidence provided"
        }
    try:
        # ==========================================
        # BUILD EVIDENCE SUMMARY
        # ==========================================
        evidence_text = ""

        for i, evidence in enumerate(evidence_list[:1], start=1):
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

            evidence_text += (
                f"\nEvidence {i}\n"
                f"Title: {title}\n"
                f"Content: {content[:700]}\n"

            )

        # ==========================================
        # PROMPT
        # ==========================================
        prompt = f"""
You are a fact-checking judge.

Claim:
{normalized_claim}

System Verdict:
{system_verdict}

System Confidence:
{confidence}

Primary Evidence:
{evidence_text}

Your task:

1. Review the evidence.
2. Decide whether the claim is:
   SUPPORTED
   REFUTED
   NOT_ENOUGH_INFORMATION

Rules:

- Use only the evidence provided.
- Do not infer missing facts.
- Do not assume that:
  - organizing an event means completing it
  - announcing something means it happened
  - planning something means it occurred
  - discussing something means it was achieved
- If any important part of the claim is not explicitly stated in the evidence,
  return NOT_ENOUGH_INFORMATION.
- Focus on what the evidence directly reports.

After deciding the verdict, write a factual explanation.

Explanation requirements:

- Use only the primary evidence.
- Do not repeat the verdict label.
- Do not start with "Therefore", "Thus", or "In conclusion".
- Describe the facts reported in the evidence.
- Summarize the article's key details.
- Do not add facts not present in the evidence.
- Do not speculate.
- Do not write a conclusion paragraph.
- Maximum 300 words.

Return ONLY valid JSON.

Example:

{{
    "verdict": "SUPPORTED",
    "reason": "Factual summary of the evidence."
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
