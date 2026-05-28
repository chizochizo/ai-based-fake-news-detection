from orchestrator.pipeline_controller import (
    VerificationPipeline
)


def main():

    pipeline = VerificationPipeline()

    claim = input(
        "\nEnter claim: "
    )

    result = pipeline.run(claim)

    # ==========================================
    # DEBUG OUTPUT
    # ==========================================
    print("\nDECOMPOSITION:")
    print(result.decomposition)

    print("\nENTITIES:")
    print(result.entities)

    print("\nQUERIES:")
    print(result.retrieval_queries)

    # ==========================================
    # TOP EVIDENCE
    # ==========================================
    print("\nTOP EVIDENCE:\n")

    for evidence in result.ranked_evidence[:3]:

        print("=" * 50)

        print("TITLE:")
        print(evidence.title)

        print("\nCONTENT:")
        print(evidence.content)

        print("\nRERANK SCORE:")
        print(evidence.reranker_score)

        print("\nSOURCE:")
        print(evidence.source_url)

    # ==========================================
    # NLI ANALYSIS
    # ==========================================
    print("\nNLI ANALYSIS:\n")

    for evidence in result.nli_results[:5]:

        print("=" * 50)

        print("LABEL:")
        print(evidence.nli_label)

        print("\nCONFIDENCE:")
        print(evidence.nli_confidence)

        print("\nCONTENT:")
        print(evidence.content[:300])

        print("\nALIGNMENT:")
        print(evidence.alignment_score)

        print("\nFACT SCORE:")
        print(evidence.fact_score)

        print("\nFINAL SCORE:")
        print(evidence.final_score)

    print("\nAGGREGATED SCORES:")
    print(result.final_verdict)

    print("\nCONFIDENCE:")
    print(result.confidence_score)

    print("\nALIGNMENT:")
    print(evidence.alignment_score)
    # ==========================================
    # FINAL OUTPUT
    # ==========================================
    print("\n==========================")
    print("FINAL VERDICT")
    print("==========================")

    print(result.final_verdict)

    print(
        f"\nConfidence: "
        f"{result.confidence_score}"
    )

    print("\nREPORT:\n")

    print(result.final_report)


if __name__ == "__main__":
    main()
