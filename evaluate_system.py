import pandas as pd

from orchestrator.pipeline_controller import (
    VerificationPipeline
)

# ==========================================
# INIT PIPELINE
# ==========================================

pipeline = VerificationPipeline()

# ==========================================
# LOAD TEST FILE
# ==========================================

df = pd.read_csv(
    "evaluation_claim.csv"
)

results = []

print("\nSTARTING BENCHMARK\n")

# ==========================================
# RUN ALL CLAIMS
# ==========================================

for index, row in df.iterrows():

    claim = row["claim"]
    expected = row["expected"]

    print("\n===================================")
    print(f"TEST {index+1}/{len(df)}")
    print("CLAIM:", claim)
    print("EXPECTED:", expected)

    try:

        state = pipeline.run(
            claim
        )

        predicted = state.final_verdict

        confidence = (
            state.confidence_score
        )

        top_title = ""

        if state.ranked_evidence:

            top_title = getattr(

                state.ranked_evidence[0],

                "title",

                ""
            )

        results.append({

            "claim": claim,

            "expected": expected,

            "predicted": predicted,

            "confidence": confidence,

            "top_evidence": top_title
        })

        print(
            "PREDICTED:",
            predicted
        )

    except Exception as e:

        print("ERROR:", e)

        results.append({

            "claim": claim,

            "expected": expected,

            "predicted": "ERROR",

            "confidence": 0,

            "top_evidence": ""
        })

# ==========================================
# SAVE RESULTS
# ==========================================

results_df = pd.DataFrame(
    results
)

results_df.to_csv(

    "evaluation_results.csv",

    index=False
)

# ==========================================
# ACCURACY
# ==========================================

correct = len(

    results_df[
        results_df["expected"]
        ==
        results_df["predicted"]
    ]
)

accuracy = (

    correct
    /
    len(results_df)
)

print("\n===================================")
print("CORRECT:", correct)
print("TOTAL:", len(results_df))
print(
    "ACCURACY:",
    round(
        accuracy * 100,
        2
    ),
    "%"
)
print("===================================")
