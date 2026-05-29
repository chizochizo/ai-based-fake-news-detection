import re
from datetime import datetime

CURRENT_YEAR = datetime.now().year

# =====================================================
# STOPWORDS
# =====================================================
STOPWORDS = {
    "the", "a", "an", "is", "was", "were", "be", "been", "being",
    "has", "have", "had", "do", "does", "did", "of", "in", "on",
    "at", "for", "to", "from", "by", "with", "and", "or", "but"
}

# =====================================================
# ABBREVIATIONS
# =====================================================
ABBREVIATIONS = {
    "nagaland university": "NU",
    "indian institute of technology": "IIT",
    "all india institute of medical sciences": "AIIMS"
}


# =====================================================
# TEXT CLEANER
# =====================================================
def clean_text(text):
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


# =====================================================
# QUERY BUILDER
# =====================================================
def build_search_queries(claim, decomposition):
    queries = set()
    claim = clean_text(claim)

    # ==========================================
    # ORIGINAL CLAIM
    # ==========================================
    queries.add(claim)

    # ==========================================
    # ENTITY EXTRACTION
    # ==========================================
    entity_names = [
        clean_text(ent["text"])
        for ent in decomposition.get("entities", [])
    ]

    # ==========================================
    # NOUN CHUNKS
    # ==========================================
    noun_chunks = [
        clean_text(chunk)
        for chunk in decomposition.get("noun_chunks", [])
    ]

    # ==========================================
    # ACTIONS
    # ==========================================
    actions = decomposition.get("actions", [])

    # ==========================================
    # ENTITY QUERIES
    # ==========================================
    if entity_names:
        # Exact quoted
        quoted_entities = " ".join([f'"{e}"' for e in entity_names])
        queries.add(quoted_entities)

        # Relaxed entity query
        relaxed_entities = " ".join(entity_names)
        queries.add(relaxed_entities)

    # ==========================================
    # NOUN CHUNK QUERIES
    # ==========================================
    for chunk in noun_chunks:
        if len(chunk.split()) >= 2:
            # Exact noun chunk
            queries.add(f'"{chunk}"')
            # Relaxed noun chunk
            queries.add(chunk)

    # ==========================================
    # ENTITY + ACTION QUERY
    # ==========================================
    if entity_names and actions:
        event_query = f'{" ".join(entity_names)} {" ".join(actions)}'
        queries.add(event_query)

    # ==========================================
    # ENTITY + NOUN MIX
    # ==========================================
    if entity_names and noun_chunks:
        for entity in entity_names[:2]:
            for chunk in noun_chunks[:3]:
                mixed_query = f"{entity} {chunk}"
                queries.add(mixed_query)

    # ==========================================
    # COMPACT QUERY
    # ==========================================
    compact_words = [
        word for word in claim.split()
        if word.lower() not in STOPWORDS
    ]
    compact_query = " ".join(compact_words)
    if compact_query:
        queries.add(compact_query)

    # ==========================================
    # DATE VARIANTS
    # ==========================================
    queries.add(f"{claim} {CURRENT_YEAR}")

    # ==========================================
    # ABBREVIATION VARIANTS
    # ==========================================
    for full_name, short_name in ABBREVIATIONS.items():
        if full_name in claim:
            abbreviated = claim.replace(full_name, short_name)
            queries.add(abbreviated)

    # ==========================================
    # EDUCATIONAL / OFFICIAL SOURCES
    # ==========================================
    if entity_names:
        official_query = f'site:edu {" ".join(entity_names)}'
        queries.add(official_query)

        official_query_2 = f'site:ac.in {" ".join(entity_names)}'
        queries.add(official_query_2)

    # ==========================================
    # SEMANTIC EVENT VARIANTS
    # ==========================================
    EVENT_VARIANTS = {
        "parting": ["farewell", "sendoff"],
        "programme": ["event", "ceremony"],
        "social": ["gathering", "celebration"]
    }

    for original, variants in EVENT_VARIANTS.items():
        if original in claim:
            for variant in variants:
                semantic_variant = claim.replace(original, variant)
                queries.add(semantic_variant)

    # ---
    # NEWS style queries
    # --
    if entity_names:
        for entity in entity_names:
            queries.add(f"{entity} press release")
            queries.add(f"{entity} official statement")
            queries.add(f"{entity} announcement")
            queries.add(f"{entity} event")

    # ---
    # TEMPORAL queries
    # ---
    queries.add(f"{claim} this week")
    queries.add(f"{claim} this month")
    queries.add(f"{claim} this year")

    # ==========================================
    # CLEANUP
    # ==========================================
    clean_queries = []
    seen = set()

    for query in queries:
        query = clean_text(query)
        if len(query) > 3 and query not in seen:
            clean_queries.append(query)
            seen.add(query)

    # ==========================================
    # PRIORITIZE SHORTER QUERIES
    # ==========================================
    clean_queries = sorted(
        clean_queries,
        key=lambda q: (
            -len(q.split()),
            q.count("")
        )
    )
    return clean_queries[:15]
