import re


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


# =====================================================
# FRAME EXTRACTION
# =====================================================

def extract_claim_frame(
    claim,
    decomposition
):

    frame = {

        "entities": [],

        "actions": [],

        "numbers": [],

        "event_terms": [],

        "noun_chunks": []
    }

    # ==========================================
    # ENTITIES
    # ==========================================

    for entity in decomposition["entities"]:

        frame["entities"].append(

            entity["text"].lower()
        )

    # ==========================================
    # ACTIONS
    # ==========================================

    for action in decomposition["actions"]:

        normalized = normalize_action(
            action
        )

        frame["actions"].append(
            normalized
        )

    # ==========================================
    # NUMBERS
    # ==========================================

    frame["numbers"] = [

        n.lower()

        for n in decomposition["numbers"]
    ]

    # ==========================================
    # NOUN CHUNKS
    # ==========================================

    frame["noun_chunks"] = [

        chunk.lower()

        for chunk in decomposition[
            "noun_chunks"
        ]
    ]

    # ==========================================
    # EVENT TERMS
    # ==========================================

    important_terms = re.findall(

        r"\b[a-zA-Z]{4,}\b",

        claim.lower()
    )

    stopwords = {

        "this",
        "that",
        "with",
        "from",
        "have",
        "were",
        "their",
        "about",
        "which",
        "where",
        "when",
        "while",
        "into",
        "during",
        "after",
        "before",
        "under",
        "over",
        "between",
        "among",
        "through",
        "within",
        "without",

        "program",
        "programme",
        "event",
        "social",
        "parting"
    }

    frame["event_terms"] = [

        t for t in important_terms

        if t not in stopwords
    ]

    # ==========================================
    # REMOVE DUPLICATES
    # ==========================================

    frame["entities"] = list(
        set(frame["entities"])
    )

    frame["actions"] = list(
        set(frame["actions"])
    )

    frame["numbers"] = list(
        set(frame["numbers"])
    )

    frame["noun_chunks"] = list(
        set(frame["noun_chunks"])
    )

    frame["event_terms"] = list(
        set(frame["event_terms"])
    )

    return frame


# =====================================================
# EVENT MATCHING
# =====================================================

def overlap_score(a, b):

    if not a or not b:

        return 0

    a = set(a)

    b = set(b)

    overlap = a.intersection(b)

    return len(overlap) / max(

        len(a),

        1
    )


def compute_event_match(

    claim_frame,

    evidence_frame
):

    # ==========================================
    # ENTITY MATCH
    # ==========================================

    entity_score = overlap_score(

        claim_frame["entities"],

        evidence_frame["entities"]
    )

    # ==========================================
    # ACTION MATCH
    # ==========================================

    action_score = overlap_score(

        claim_frame["actions"],

        evidence_frame["actions"]
    )

    # ==========================================
    # NUMBER MATCH
    # ==========================================

    number_score = overlap_score(

        claim_frame["numbers"],

        evidence_frame["numbers"]
    )

    # ==========================================
    # EVENT TERM MATCH
    # ==========================================

    term_score = overlap_score(

        claim_frame["event_terms"],

        evidence_frame["event_terms"]
    )

    # ==========================================
    # FINAL SCORE
    # ==========================================

    final_score = (

        entity_score * 0.40

        +

        action_score * 0.25

        +

        number_score * 0.20

        +

        term_score * 0.15
    )

    return {

        "entity_score": entity_score,

        "action_score": action_score,

        "number_score": number_score,

        "term_score": term_score,

        "final_score": final_score
    }
