from retrieval.hybrid_retriever import retrieve_evidence

claim = "Nagaland University hosted Startup Sprint on 22 April"

queries = [
    claim,
    "Nagaland University Startup Sprint",
    "Startup Sprint Nagaland University April"
]

result = retrieve_evidence(
    claim,
    queries
)

print("\nENGINES USED:")
print(result["engines_used"])

print("\nCLAIM TYPE:")
print(result["claim_type"])

print("\nEVIDENCE COUNT:")
print(len(result["evidence"]))
