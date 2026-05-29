
# retrieval/web_search.py

from types import SimpleNamespace


# =====================================================
# SIMPLE TEST SEARCH ENGINE
# =====================================================

def search_web(
    query,
    engine="google"
):

    print("\n======================")
    print("SEARCH WEB CALLED")
    print("======================")

    print("ENGINE:", engine)
    print("QUERY:", query)

    # =================================================
    # MOCK EVIDENCE
    # =================================================

    results = [

        SimpleNamespace(

            title="Wikipedia - Mount Saramati",

            content=(
                "Mount Saramati is the highest "
                "mountain peak in Nagaland "
                "with an elevation of "
                "3841 metres."
            ),

            source_url=(
                "https://en.wikipedia.org/"
                "wiki/Mount_Saramati"
            ),

            reranker_score=0.0
        ),

        SimpleNamespace(

            title="Nagaland Tourism",

            content=(
                "Mount Saramati is located "
                "on the border of Nagaland "
                "and Myanmar."
            ),

            source_url=(
                "https://tourism.nagaland.gov.in"
            ),

            reranker_score=0.0
        )
    ]

    print("\nRETURNING:", len(results))

    return results
