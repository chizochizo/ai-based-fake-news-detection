import re
import spacy

nlp = spacy.load(
    "en_core_web_sm"
)

BAD_ENTITY_TERMS = {
    "conduct",
    "host",
    "organize",
    "hold",
    "run",
    "conducted",
    "conducting",

    "hosts",
    "hosted",
    "hosting",

    "organized",
    "organised",
    "organizing",
    "organising",

    "holds",
    "held",
    "holding",

    "runs",
    "running",
    "ran",

    "event",
    "events",

    "activity",
    "activities",

    "session",
    "sessions",

    "meeting",
    "meetings",

    "function",
    "functions"
}

ACTION_NORMALIZATION = {
    "host": "conduct",
    "conduct": "conduct",
    "organize": "conduct",
    "hold": "conduct",
    "run": "conduct",

    "launch": "launch",

    "announce": "announce",

    "report": "report",

    "claim": "report",

    "say": "report",

    "state": "report",

    "complete": "complete",

    "win": "win",

    "support": "support",

    "elect": "elect",

    "arrest": "arrest",

    "kill": "kill",
    "celebrate": "conduct",
    "observe": "conduct",
    "commemorate": "conduct",
    "facilitate": "conduct",
    "coordinate": "conduct",
    "sponsor": "conduct",
    "arrange": "conduct",
    "manage": "conduct",
    "execute": "conduct",
    "mention": "report",
    "disclose": "report",
    "reveal": "report",
    "confirm": "report",
    "deny": "report",
    "assert": "report",
    "allege": "report",
    "achieve": "complete",
    "finish": "complete",
    "graduate": "complete"
}

# ==========================================
# NEGATION WORDS
# ==========================================

NEGATION_WORDS = {
    "not",
    "never",
    "no",
    "none",
    "neither",
    "nor",
    "without",
    "n't"
}

EVENT_NOUNS = {
    "sprint", "conference", "workshop", "seminar",
    "festival", "summit", "ceremony", "event",
    "program", "programme", "competition",
    "hackathon", "mission", "launch",
    "election", "protest", "rally",
    "earthquake", "flood", "cyclone", "landslide",
    "accident", "crash", "explosion", "blast",
    "attack", "riot", "murder", "arrest",
    "outbreak", "award", "training",
    "orientation",
    "awareness",
    "internship",
    "fellowship",
    "summit",
    "bootcamp",
    "sprint",
    "webinar",
    "symposium",
    "lecture",
    "dialogue",
    "conclave",
    "exhibition",
    "expo",
    "farewell",
    "freshers",
    "convocation",
    "graduation"
}

DATE_CHUNK_PATTERN = re.compile(
    r"^\d{1,2}\s+(january|february|march|april|may|june|july|august|september|october|november|december)$",
    re.I
)

# ==========================================
# ACTION NORMALIZATION
# ==========================================


def normalize_action(action):
    action = action.lower().strip()
    return ACTION_NORMALIZATION.get(
        action,
        action
    )


# ==========================================
# ENTITY CLEANING
# ==========================================

def clean_entity_text(text):
    text = text.strip().lower()
    tokens = text.split()

    filtered_tokens = [
        token
        for token in tokens
        if (
            token not in BAD_ENTITY_TERMS
            and
            len(token) > 1
        )
    ]

    cleaned = " ".join(
        filtered_tokens
    )

    return cleaned.strip()


# ==========================================
# CLAIM DECOMPOSITION
# ==========================================

def decompose_claim(claim):
    doc = nlp(claim)

    entities = []
    actions = []
    nouns = []
    noun_chunks = []
    event_terms = []
    event_phrases = []
    numbers = []
    dates = []
    negations = []

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
        token_text = token.text.lower()

        # --------------------------------------
        # ACTIONS
        # --------------------------------------

        if token.pos_ == "VERB":
            if (
                token.is_alpha
                and
                len(token.lemma_) > 2
            ):
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
            if len(token_text) > 2:
                nouns.append(
                    token_text
                )
                if token_text in EVENT_NOUNS:
                    event_terms.append(token_text)

        # --------------------------------------
        # NUMBERS
        # --------------------------------------

        if token.like_num:
            numbers.append(
                token_text
            )

        # --------------------------------------
        # NEGATIONS
        # --------------------------------------

        if token_text in NEGATION_WORDS:
            negations.append(
                token_text
            )

    # ==========================================
    # NOUN CHUNKS
    # ==========================================

    for chunk in doc.noun_chunks:
        cleaned_chunk = (
            chunk.text
            .strip()
            .lower()
        )

        if DATE_CHUNK_PATTERN.match(cleaned_chunk):
            continue

        if (
            len(cleaned_chunk) > 2
            and
            not cleaned_chunk.isnumeric()
        ):
            noun_chunks.append(cleaned_chunk)
            chunk_words = set(cleaned_chunk.split())
            if chunk_words & EVENT_NOUNS:
                event_phrases.append(cleaned_chunk)
                event_phrases.append(
                    cleaned_chunk
                )

    # ==========================================
    # DATE EXTRACTION
    # ==========================================

    date_patterns = re.findall(
        r"\b(?:19|20)\d{2}\b",
        claim
    )
    dates.extend(date_patterns)

    # ==========================================
    # DEDUPLICATION
    # ==========================================

    entities = list({
        (
            e["text"],
            e["label"]
        ): e
        for e in entities
    }.values())

    actions = list(set(actions))
    event_terms = list(set(event_terms))
    event_phrases = list(set(event_phrases))
    nouns = list(set(nouns))
    noun_chunks = list(set(noun_chunks))
    numbers = list(set(numbers))
    dates = list(set(dates))
    negations = list(set(negations))

    # ==========================================
    # CLAIM TYPE DETECTION
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

    # EVENT CLAIM VIA EVENT TERMS

    elif event_terms:
        claim_type = "event"

    # NUMERIC CLAIM

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
        "negations": negations,
        "claim_type": claim_type,
        "event_terms": event_terms,
        "event_phrases": event_phrases,
    }
