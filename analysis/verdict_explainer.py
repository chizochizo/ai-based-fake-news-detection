import ollama


def generate_verdict_explanation(
    claim,
    verdict,
    evidence_list
):

    try:

        evidence_text = "\n\n".join([

            f"Evidence {i+1}: {e.content}"

            for i, e in enumerate(
                evidence_list[:3]
            )
        ])

        prompt = f"""
Claim:
{claim}

Verdict:
{verdict}

Evidence:
{evidence_text}

Explain why this verdict was reached.

Use only the evidence.

Do not determine the verdict yourself.

Keep the explanation under 150 words.
"""

        response = ollama.chat(

            model="qwen2.5-coder:3b",

            options={
                "temperature": 0.1
            },

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]

    except Exception as e:

        print("QWEN ERROR:", e)

        return ""
