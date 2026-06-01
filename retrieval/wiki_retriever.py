import wikipediaapi

from schemas.evidence_schema import Evidence


wiki = wikipediaapi.Wikipedia(
    user_agent="FactCheckerBot/1.0",
    language="en"
)


def retrieve_wikipedia(
    claim,
    decomposition=None
):

    evidence_list = []

    search_terms = []

    # =====================================
    # ENTITY FIRST
    # =====================================

    if decomposition:

        entities = [
            e["text"]
            for e in decomposition.get(
                "entities",
                []
            )
        ]

        event_phrases = decomposition.get(
            "event_phrases",
            []
        )

        search_terms.extend(
            entities
        )

        search_terms.extend(
            event_phrases
        )
        search_terms.extend(
            decomposition.get(
                "nouns",
                []
            )
        )

    # =====================================
    # FALLBACK
    # =====================================

    if not search_terms:

        search_terms.append(
            claim
        )

    # =====================================
    # PAGE LOOKUP
    # =====================================

    seen = set()
    search_terms = list(
        dict.fromkeys(search_terms)
    )

    for term in search_terms[:5]:

        try:

            page = wiki.page(term)

            if not page.exists():
                continue

            if page.fullurl in seen:
                continue

            seen.add(
                page.fullurl
            )

            evidence = Evidence(

                title=page.title,

                content=page.summary[:2000],

                source_url=page.fullurl
            )

            evidence_list.append(
                evidence
            )

        except Exception:
            continue

    return evidence_list
