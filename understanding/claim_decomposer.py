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

# ==========================================
# ACTION NORMALIZATION
# ==========================================

ACTION_NORMALIZATION = {

    "hosts": "conduct",
    "hosted": "conduct",
    "hosting": "conduct",

    "conducted": "conduct",

    "organized": "conduct",
    "organised": "conduct",

    "holds": "conduct",
    "held": "conduct",

    "launched": "launch",

    "announced": "announce",

    "reported": "report"
}


def normalize_action(action):

    action = action.lower()

    return ACTION_NORMALIZATION.get(
        action,
        action
    )


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

        if (

            token.pos_ in ["VERB", "AUX"]

            or

            (
                token.dep_ == "ROOT"
                and
                token.pos_ in ["NOUN", "PROPN"]
            )

        ):

            if token.is_alpha:

                normalized = normalize_action(
                    token.lemma_.lower()
                )

                actions.append(
                    normalized
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
    # CLAIM TYPE
    # ==========================================

    claim_lower = claim.lower()

    claim_type = "general"

    # ------------------------------------------
    # STATEMENT CLAIM
    # ------------------------------------------

    if any(word in claim_lower for word in [

        "said",
        "announced",
        "reported",
        "claims",
        "claim",
        "stated",
        "according to"

    ]):

        claim_type = "statement"

    # ------------------------------------------
    # EVENT CLAIM
    # ------------------------------------------

    elif any(word in claim_lower for word in [

        "won",
        "hosted",
        "conducted",
        "held",
        "launched",
        "organized",
        "organised",
        "performed",
        "celebrated"

    ]):

        claim_type = "event"

    # ------------------------------------------
    # NUMERIC CLAIM
    # ------------------------------------------

    elif any(char.isdigit() for char in claim):

        claim_type = "numeric"

    # ------------------------------------------
    # COMPARISON CLAIM
    # ------------------------------------------

    elif any(word in claim_lower for word in [

        "better",
        "worse",
        "higher",
        "lower",
        "more than",
        "less than",
        "largest",
        "smallest",
        "biggest"

    ]):

        claim_type = "comparison"

    # ------------------------------------------
    # TEMPORAL CLAIM
    # ------------------------------------------

    elif any(word in claim_lower for word in [

        "today",
        "yesterday",
        "tomorrow",
        "currently",
        "recently",
        "in 2024",
        "in 2025",
        "in 2026"

    ]):

        claim_type = "temporal"

    # ------------------------------------------
    # CAUSAL CLAIM
    # ------------------------------------------

    elif any(word in claim_lower for word in [

        "because",
        "due to",
        "caused",
        "resulted in",
        "led to"

    ]):

        claim_type = "causal"

    # ==========================================
    # RETURN
    # ==========================================

    return {

        "entities": entities,

        "actions": actions,

        "nouns": nouns,

        "noun_chunks": noun_chunks,

        "numbers": numbers,

        "dates": dates,

        "claim_type": claim_type
    }
