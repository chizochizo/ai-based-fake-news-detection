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


def extract_claim_frame(claim, decomposition):
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
        normalized = normalize_action(action)
        frame["actions"].append(normalized)

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
        for chunk in decomposition["noun_chunks"]
    ]

    # ==========================================
    # EVENT TERMS
    # ==========================================
    important_terms = re.findall(
        r"\b[a-zA-Z]{4,}\b",
        claim.lower()
    )

    stopwords = {
        "this", "that", "with", "from", "have", "were", "their",
        "about", "which", "where", "when", "while", "into",
        "during", "after", "before", "under", "over", "between",
        "among", "through", "within", "without", "program",
        "programme", "event", "social", "parting"
    }

    frame["event_terms"] = [
        t for t in important_terms
        if t not in stopwords
    ]

    # Deduplicate event terms before returning
    frame["event_terms"] = list(
        set(frame["event_terms"])
    )

    return frame
