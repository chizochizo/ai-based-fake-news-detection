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
        "running"
    ],

    "say": [

        "said",
        "says",
        "announce",
        "announced",
        "reported",
        "reports",
        "claimed",
        "claims",
        "stated",
        "states"
    ],

    "win": [

        "won",
        "wins",
        "defeated",
        "beats",
        "beat"
    ],

    "support": [

        "supports",
        "supported",
        "backs",
        "backed",
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
# NORMALIZATION
# =====================================================

def normalize_claim(claim):

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
        # LEMMATIZATION
        # ==========================================

        elif token.pos_ == "VERB":

            normalized_tokens.append(
                token.lemma_.lower()
            )

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
