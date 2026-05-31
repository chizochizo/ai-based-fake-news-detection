from types import SimpleNamespace
from analysis.verdict_aggregator import aggregate_verdicts

claim = "Germany won the 2018 FIFA World Cup"

evidence = [

    SimpleNamespace(
        title="Wikipedia",
        content="Germany were eliminated in the group stage.",
        nli_label="CONTRADICTION",
        nli_confidence=0.99,
        reranker_score=5,
        source_url="https://wikipedia.org"
    ),

    SimpleNamespace(
        title="France Winner",
        content="France won the 2018 FIFA World Cup.",
        nli_label="CONTRADICTION",
        nli_confidence=0.98,
        reranker_score=5,
        source_url="https://fifa.com"
    ),

    SimpleNamespace(
        title="Germany Sweden",
        content="Germany beat Sweden.",
        nli_label="NEUTRAL",
        nli_confidence=0.90,
        reranker_score=3,
        source_url="https://bbc.com"
    )

]

result = aggregate_verdicts(
    claim,
    evidence
)

print(result)
