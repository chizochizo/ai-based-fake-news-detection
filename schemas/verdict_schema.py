from dataclasses import dataclass


@dataclass
class Verdict:

    label: str

    confidence: float

    reasoning: str
