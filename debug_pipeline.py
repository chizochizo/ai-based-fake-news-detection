
# debug_pipeline.py

from orchestrator.pipeline_controller import (
    VerificationPipeline
)

print("\n===================")
print("STARTING TEST")
print("===================\n")

pipeline = VerificationPipeline()

result = pipeline.run(
    "mount saramati is the highest mountain in nagaland"
)

print("\n===================")
print("PIPELINE FINISHED")
print("===================\n")

print("VERDICT:")
print(result.final_verdict)

print("\nCONFIDENCE:")
print(result.confidence_score)

print("\nQUERIES:")
print(result.retrieval_queries)

print("\nEVIDENCE COUNT:")
print(len(result.ranked_evidence))
