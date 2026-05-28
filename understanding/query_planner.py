def build_search_queries(
    claim,
    decomposition
):

    queries = set()

    # ==========================================
    # ORIGINAL CLAIM
    # ==========================================

    queries.add(claim)

    # ==========================================
    # ENTITY QUERIES
    # ==========================================

    entity_names = [

        ent["text"]

        for ent in decomposition.get(
            "entities",
            []
        )
    ]

    if entity_names:

        quoted_entities = " ".join([
            f'"{e}"'
            for e in entity_names
        ])

        queries.add(
            quoted_entities
        )

    # ==========================================
    # NOUN CHUNK QUERIES
    # ==========================================

    noun_chunks = decomposition.get(
        "noun_chunks",
        []
    )

    for chunk in noun_chunks:

        if len(chunk.split()) >= 2:

            queries.add(
                f'"{chunk}"'
            )

    # ==========================================
    # EVENT STYLE QUERY
    # ==========================================

    actions = decomposition.get(
        "actions",
        []
    )

    if entity_names and actions:

        event_query = (
            f'"{" ".join(entity_names)}" '
            f'{" ".join(actions)}'
        )

        queries.add(event_query)

    # ==========================================
    # EDUCATIONAL / OFFICIAL SOURCES
    # ==========================================

    if entity_names:

        official_query = (
            f'site:edu '
            f'"{" ".join(entity_names)}"'
        )

        queries.add(
            official_query
        )

    # ==========================================
    # CLEANUP
    # ==========================================

    clean_queries = []

    for query in queries:

        query = query.strip()

        if len(query) > 3:

            clean_queries.append(
                query
            )

    return clean_queries
