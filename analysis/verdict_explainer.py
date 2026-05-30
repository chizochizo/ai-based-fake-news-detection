import ollama


def generate_verdict_explanation(
    claim,
    verdict,
    evidence_list
):

    try:

        top_evidence = evidence_list[0]

        evidence_text = f"""
Title:
{top_evidence.title}

Content:
{top_evidence.content[:300]}
"""
        prompt = f"""
Claim: 
{claim}

Verdict:
{verdict}

Evidence:
{evidence_text}

Explain why this verdict was reached.

Requirements:
- Use only the primary evidence.
- Do not discuss other evidence.
- Do not repeat the verdict.
- Do not start with "Therefore", "Thus", or "In conclusion".
- Describe the facts reported in the evidence or summarize the key details from the article that support the verdict.
- Do not write a conclusion paragraph.
- Do not repeat yourself.
- Max 200 words
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
