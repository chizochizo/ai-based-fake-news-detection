import re

import spacy


nlp = spacy.load(
    "en_core_web_sm"
)


def decompose_claim(claim):

    doc = nlp(claim)

    entities = []

    actions = []

    nouns = []

    noun_chunks = []

    numbers = []

    dates = []

    # ==========================================
    # ENTITIES
    # ==========================================

    for ent in doc.ents:

        entities.append({
            "text": ent.text,
            "label": ent.label_
        })

    # ==========================================
    # TOKENS
    # ==========================================

    for token in doc:

        if token.pos_ == "VERB":

            actions.append(token.lemma_)

        if token.pos_ in ["NOUN", "PROPN"]:

            nouns.append(token.text)

        if token.like_num:

            numbers.append(token.text)

    # ==========================================
    # NOUN CHUNKS
    # ==========================================

    for chunk in doc.noun_chunks:

        noun_chunks.append(
            chunk.text
        )

    # ==========================================
    # DATES
    # ==========================================

    date_patterns = re.findall(
        r"\b\d{4}\b",
        claim
    )

    dates.extend(date_patterns)

    return {

        "entities": entities,

        "actions": actions,

        "nouns": nouns,

        "noun_chunks": noun_chunks,

        "numbers": numbers,

        "dates": dates
    }
