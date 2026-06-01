import re
from datetime import datetime

CURRENT_YEAR = datetime.now().year


# =====================================================
# CLEANER
# =====================================================

def clean_text(text):
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text


# =====================================================
# QUERY BUILDER
# =====================================================

def build_search_queries(claim, decomposition):

    claim = clean_text(claim)

    queries = []

    # ==========================================
    # 1. ORIGINAL CLAIM
    # ==========================================

    queries.append(claim)

    # ==========================================
    # 2. CLAIM + YEAR
    # ==========================================

    queries.append(
        f"{claim} {CURRENT_YEAR}"
    )

    # ==========================================
    # 3. ENTITY EXTRACTION
    # ==========================================

    entities = [

        clean_text(ent["text"])

        for ent in decomposition.get(
            "entities",
            []
        )
    ]

    entity_string = " ".join(
        entities
    )

    # ==========================================
    # 4. RELATION EXTRACTION
    # ==========================================

    relations = []

    lower_claim = claim.lower()

    relation_patterns = [

        "capital of",

        "chief minister of",

        "president of",

        "founder of",

        "located in",

        "part of",

        "member of",

        "headquarters of",

        "representing",

        "winner of",

        "startup sprint",

        "startup program",

        "startup programme",

        "completed startup sprint"
    ]

    for pattern in relation_patterns:

        if pattern in lower_claim:

            relations.append(
                pattern
            )

    # ==========================================
    # 5. RELATIONAL QUERY
    # ==========================================

    for relation in relations:

        if entities:

            queries.append(
                f'{entity_string} "{relation}"'
            )

            queries.append(
                f'"{relation}" {entity_string}'
            )

    # ==========================================
    # 6. QUOTED CLAIM FRAGMENT
    # ==========================================

    if len(claim.split()) >= 4:

        queries.append(
            f'"{claim}"'
        )

    # ==========================================
    # 7. OFFICIAL SOURCE QUERY
    # ==========================================

    if entities:

        queries.append(
            f'site:gov {entity_string}'
        )

    # ==========================================
    # 8. FACT VERIFICATION QUERY
    # ==========================================

    if entities and relations:

        for relation in relations:

            queries.append(
                f'"{relation}" {entity_string} {CURRENT_YEAR}'
            )

    # ==========================================
    # DEDUPLICATE
    # ==========================================

    seen = set()

    final_queries = []

    for q in queries:

        q = clean_text(q)

        if q not in seen:

            seen.add(q)

            final_queries.append(q)

    print("\n[TOP QUERIES]")

    for q in final_queries:

        print(q)

    return final_queries
