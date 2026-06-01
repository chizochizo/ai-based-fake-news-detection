from understanding.claim_decomposer import decompose_claim
from understanding.query_planner import build_search_queries
from retrieval.hybrid_retriever import retrieve_evidence

claim = "The capital of Nagaland is Kohima"

decomp = decompose_claim(claim)

queries = build_search_queries(
    claim,
    decomp
)

result = retrieve_evidence(
    claim,
    queries,
    decomp
)

print("\nENGINES USED:")
print(result["engines_used"])

print("\nCLAIM TYPE:")
print(result["claim_type"])

print("\nEVIDENCE COUNT:")
print(len(result["evidence"]))

print("\nTOP EVIDENCE:")
for e in result["evidence"]:
    print("\nTITLE:", e.title)
    print("RERANK:", getattr(e, "reranker_score", None))
    print("URL:", e.source_url)
