# test_conflicts.py

from analysis.fact_matcher import (
    extract_fact_structure,
    detect_conflicts
)

claim = "Germany won the 2018 FIFA World Cup"

evidence = "Germany were eliminated in the group stage."

claim_struct = extract_fact_structure(claim)
evidence_struct = extract_fact_structure(evidence)

print("\nCLAIM STRUCT")
print(claim_struct)

print("\nEVIDENCE STRUCT")
print(evidence_struct)

conflicts = detect_conflicts(
    claim_struct,
    evidence_struct
)

print("\nCONFLICTS")
print(conflicts)
