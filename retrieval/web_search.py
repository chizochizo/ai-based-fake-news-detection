from ddgs import DDGS

from schemas.evidence_schema import Evidence


def search_web(
    query,
    max_results=5
):

    evidence_list = []

    with DDGS() as ddgs:

        results = ddgs.text(
            query,
            max_results=max_results
        )

        for result in results:

            evidence = Evidence(

                title=result.get(
                    "title",
                    ""
                ),

                content=result.get(
                    "body",
                    ""
                ),

                source_url=result.get(
                    "href",
                    ""
                )
            )

            evidence_list.append(
                evidence
            )

    return evidence_list
