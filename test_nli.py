from analysis.nli_analyzer import analyze_claim_evidence


class MockEvidence:

    def __init__(self, content):

        self.content = content

        self.title = "Test Evidence"

        self.alignment_score = 0.0

        self.fact_score = 0.0


claim = "Germany won the 2018 FIFA World Cup"

evidence_list = [

    MockEvidence(
        "Germany were eliminated in the group stage of the 2018 FIFA World Cup."
    ),

    MockEvidence(
        "France won the 2018 FIFA World Cup."
    ),

    MockEvidence(
        "Germany defeated Sweden during the tournament."
    )

]

results = analyze_claim_evidence(
    claim,
    evidence_list
)

print("\nFINAL RESULTS\n")

for item in results:

    print(
        item.nli_label,
        "|",
        round(item.nli_confidence, 3)
    )

    print(item.content)

    print("-" * 50)
