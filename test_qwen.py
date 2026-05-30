from analysis.qwen_judge import run_qwen_judge


class DummyEvidence:

    def __init__(self, title, content, label):

        self.title = title
        self.content = content
        self.nli_label = label


evidence = [

    DummyEvidence(

        title="FIFA World Cup 2018",

        content="""
France won the 2018 FIFA World Cup by defeating Croatia
4-2 in the final held in Moscow.
""",

        label="ENTAILMENT"
    ),

    DummyEvidence(

        title="Germany Eliminated",

        content="""
Germany were eliminated in the group stage of the
2018 FIFA World Cup.
""",

        label="ENTAILMENT"
    )
]


result = run_qwen_judge(

    claim="Germany won the 2018 FIFA World Cup",

    system_verdict="CONTRADICTION",

    confidence=0.91,

    evidence_list=evidence
)

print("\nFINAL RESULT\n")
print(result)
