import hashlib

from schemas.entity_schema import Entity


def normalize_entity(text):

    return text.lower().strip()


def build_entity_id(text):

    return hashlib.md5(
        text.encode()
    ).hexdigest()


def resolve_entities(decomposition):

    resolved_entities = []

    for entity in decomposition.get(
        "entities",
        []
    ):

        normalized = normalize_entity(
            entity["text"]
        )

        entity_obj = Entity(

            entity_id=build_entity_id(
                normalized
            ),

            canonical_name=entity["text"],

            normalized_name=normalized,

            entity_type=entity["label"],

            aliases=[],

            metadata={}
        )

        resolved_entities.append(
            entity_obj
        )

    return resolved_entities
