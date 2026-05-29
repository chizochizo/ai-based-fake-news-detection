import re

import spacy


nlp = spacy.load(
    "en_core_web_sm"
)


# =====================================================
# CANONICAL ACTION MAP
# =====================================================

ACTION_GROUPS = {

    "conduct": [

        "host",
        "hosts",
        "hosted",
        "hosting",

        "organize",
        "organizes",
        "organized",
        "organised",
        "organising",

        "hold",
        "holds",
        "held",
        "holding",

        "conduct",
        "conducted",
        "conducting",

        "run",
        "ran",
        "running",

        "complete",
        "completed",
        "completes",
        "completion",

        "launch",
        "launched",
        "launches",

        "execute",
        "executed",

        "perform",
        "performed",

        "carry",
        "carried"
    ],

    "say": [

        "said",
        "says",

        "announce",
        "announced",
        "announcing",

        "report",
        "reported",
        "reports",

        "claim",
        "claimed",
        "claims",

        "state",
        "stated",
        "states"
    ],

    "win": [

        "won",
        "wins",

        "defeat",
        "defeated",

        "beat",
        "beats"
    ],

    "support": [

        "support",
        "supports",
        "supported",

        "back",
        "backs",
        "backed",

        "endorse",
        "endorsed"
    ]
}


# =====================================================
# BUILD REVERSE LOOKUP
# =====================================================

NORMALIZATION_MAP = {}

for canonical, variants in (
    ACTION_GROUPS.items()
):

    for variant in variants:

        NORMALIZATION_MAP[
            variant
        ] = canonical


# =====================================================
# PHRASE NORMALIZATION
# =====================================================

PHRASE_NORMALIZATION = {

    "start up": "startup",

    "parting social": "farewell event",

    "social parting": "farewell event",

    "programme": "program"
}


# =====================================================
# TEXT CLEANER
# =====================================================

def clean_text(text):

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =====================================================
# NORMALIZATION
# =====================================================

def normalize_claim(claim):

    claim = clean_text(
        claim
    )

    # ==========================================
    # PHRASE NORMALIZATION
    # ==========================================

    for old, new in (
        PHRASE_NORMALIZATION.items()
    ):

        claim = claim.replace(
            old,
            new
        )

    # ==========================================
    # NLP PIPELINE
    # ==========================================

    doc = nlp(claim)

    normalized_tokens = []

    for token in doc:

        word = token.text.lower()

        # ==========================================
        # ACTION NORMALIZATION
        # ==========================================

        if word in NORMALIZATION_MAP:

            normalized = (
                NORMALIZATION_MAP[word]
            )

            normalized_tokens.append(
                normalized
            )

        # ==========================================
        # VERB LEMMATIZATION
        # ==========================================

        elif token.pos_ == "VERB":

            normalized_tokens.append(
                token.lemma_.lower()
            )

        # ==========================================
        # DEFAULT TOKEN
        # ==========================================

        else:

            normalized_tokens.append(
                word
            )

    normalized = " ".join(
        normalized_tokens
    )

    # ==========================================
    # CLEANUP
    # ==========================================

    normalized = re.sub(
        r"\s+",
        " ",
        normalized
    ).strip()

    return normalized
