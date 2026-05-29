import re

import spacy


nlp = spacy.load(
    "en_core_web_sm"
)

# ==========================================
# BAD ENTITY TERMS
# ==========================================

BAD_ENTITY_TERMS = {

    "conduct",
    "conducted",

    "host",
    "hosts",
    "hosted",
    "hosting",

    "organize",
    "organized",
    "organised",

    "hold",
    "holds",
    "held"
}


def clean_entity_text(text):

    text = text.strip().lower()

    tokens = text.split()

    filtered_tokens = [

        token

        for token in tokens

        if token not in BAD_ENTITY_TERMS
    ]

    cleaned = " ".join(
        filtered_tokens
    )

    return cleaned


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

        cleaned_text = clean_entity_text(
            ent.text
        )

        if cleaned_text:

            entities.append({

                "text": cleaned_text,

                "label": ent.label_
            })

    # ==========================================
    # TOKENS
    # ==========================================

    for token in doc:

        # --------------------------------------
        # ACTIONS
        # --------------------------------------

        if token.pos_ in ["VERB", "AUX"]:

            actions.append(
                token.text.lower()
            )

        # --------------------------------------
        # NOUNS
        # --------------------------------------

        if token.pos_ in [

            "NOUN",
            "PROPN"
        ]:

            nouns.append(
                token.text.lower()
            )

        # --------------------------------------
        # NUMBERS
        # --------------------------------------

        if token.like_num:

            numbers.append(
                token.text.lower()
            )

    # ==========================================
    # NOUN CHUNKS
    # ==========================================

    for chunk in doc.noun_chunks:

        cleaned_chunk = chunk.text.lower()

        noun_chunks.append(
            cleaned_chunk
        )

    # ==========================================
    # DATES
    # ==========================================

    date_patterns = re.findall(

        r"\b\d{4}\b",

        claim
    )

    dates.extend(date_patterns)

    # ==========================================
    # REMOVE DUPLICATES
    # ==========================================

    actions = list(set(actions))

    nouns = list(set(nouns))

    numbers = list(set(numbers))

    noun_chunks = list(set(noun_chunks))

    # ==========================================
    # RETURN
    # ==========================================

    return {

        "entities": entities,

        "actions": actions,

        "nouns": nouns,

        "noun_chunks": noun_chunks,

        "numbers": numbers,

        "dates": dates
    }
