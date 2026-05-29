# analysis/wikidata_utils.py

from functools import lru_cache

from rapidfuzz import fuzz


# =====================================================
# KNOWN ENTITY ALIASES
# =====================================================

ENTITY_ALIASES = {

    "who": "world health organization",

    "bjp": "bharatiya janata party",

    "congress": "indian national congress",

    "aiims": "all india institute of medical sciences",

    "un": "united nations",

    "us": "united states",

    "usa": "united states",

    "uk": "united kingdom",

    "nasa": "national aeronautics and space administration",

    "isro": "indian space research organisation",

    "pm modi": "narendra modi",

    "cm": "chief minister"
}


# =====================================================
# NORMALIZE ENTITY
# =====================================================

@lru_cache(maxsize=2048)
def normalize_entity(entity):

    if not entity:

        return ""

    entity = entity.lower().strip()

    entity = entity.replace(".", "")

    entity = entity.replace(",", "")

    entity = entity.replace("-", " ")

    entity = " ".join(entity.split())

    # alias expansion

    if entity in ENTITY_ALIASES:

        return ENTITY_ALIASES[entity]

    return entity


# =====================================================
# ENTITY SIMILARITY
# =====================================================

def entity_similarity(entity_a, entity_b):

    entity_a = normalize_entity(entity_a)

    entity_b = normalize_entity(entity_b)

    if not entity_a or not entity_b:

        return 0

    return fuzz.token_sort_ratio(

        entity_a,

        entity_b

    ) / 100.0


# =====================================================
# ENTITY MATCH
# =====================================================

def entities_match(

    entity_a,

    entity_b,

    threshold=0.85
):

    similarity = entity_similarity(

        entity_a,

        entity_b
    )

    return similarity >= threshold
