import re


# =====================================================
# CLAIM TYPE KEYWORDS
# =====================================================

EVENT_KEYWORDS = {

    "hosted",
    "organized",
    "organised",
    "held",
    "conference",
    "meeting",
    "summit",
    "festival",
    "ceremony",
    "event",
    "workshop",
    "seminar",
    "launch"
}

STATEMENT_KEYWORDS = {

    "said",
    "announced",
    "reported",
    "claimed",
    "stated",
    "according",
    "confirmed",
    "declared"
}

NUMERIC_KEYWORDS = {

    "killed",
    "injured",
    "dead",
    "died",
    "cases",
    "votes",
    "crore",
    "million",
    "billion",
    "percentage",
    "percent",
    "km",
    "tons",
    "rupees",
    "dollars"
}

MISINFORMATION_KEYWORDS = {

    "fake",
    "hoax",
    "scam",
    "false",
    "misleading",
    "propaganda"
}

QUESTION_KEYWORDS = {

    "is it true",
    "did",
    "does",
    "can",
    "was",
    "were"
}

TEMPORAL_KEYWORDS = {

    "today",
    "yesterday",
    "breaking",
    "currently",
    "latest",
    "this year",
    "this month"
}


# =====================================================
# CLAIM TYPE CLASSIFIER
# =====================================================

def classify_claim(claim):

    text = claim.lower()

    claim_types = []

    # ==========================================
    # MISINFORMATION CLAIM
    # ==========================================

    if any(
        word in text
        for word in MISINFORMATION_KEYWORDS
    ):

        claim_types.append(
            "misinformation"
        )

    # ==========================================
    # STATEMENT CLAIM
    # ==========================================

    if any(
        word in text
        for word in STATEMENT_KEYWORDS
    ):

        claim_types.append(
            "statement"
        )

    # ==========================================
    # EVENT CLAIM
    # ==========================================

    if any(
        word in text
        for word in EVENT_KEYWORDS
    ):

        claim_types.append(
            "event"
        )

    # ==========================================
    # NUMERIC CLAIM
    # ==========================================

    if any(
        word in text
        for word in NUMERIC_KEYWORDS
    ):

        claim_types.append(
            "numeric"
        )

    # direct number detection

    if re.search(r"\b\d+\b", text):

        if "numeric" not in claim_types:

            claim_types.append(
                "numeric"
            )

    # ==========================================
    # QUESTION CLAIM
    # ==========================================

    if any(
        phrase in text
        for phrase in QUESTION_KEYWORDS
    ):

        claim_types.append(
            "question"
        )

    # ==========================================
    # TEMPORAL / BREAKING CLAIM
    # ==========================================

    if any(
        word in text
        for word in TEMPORAL_KEYWORDS
    ):

        claim_types.append(
            "breaking_news"
        )

    # ==========================================
    # FALLBACK
    # ==========================================

    if not claim_types:

        claim_types.append(
            "general"
        )

    # ==========================================
    # RETRIEVAL PRIORITY
    # ==========================================

    retrieval_strategy = determine_retrieval_strategy(
        claim_types
    )

    return {

        "claim_types": claim_types,

        "retrieval_strategy":
        retrieval_strategy
    }


# =====================================================
# RETRIEVAL STRATEGY ENGINE
# =====================================================

def determine_retrieval_strategy(
    claim_types
):

    strategy = {

        "use_news_api": False,

        "use_factcheck_api": False,

        "use_rss": False,

        "use_wikidata": False,

        "priority": []
    }

    # ==========================================
    # EVENT CLAIMS
    # ==========================================

    if "event" in claim_types:

        strategy["use_news_api"] = True

        strategy["priority"].append(
            "news_search"
        )

    # ==========================================
    # BREAKING NEWS
    # ==========================================

    if "breaking_news" in claim_types:

        strategy["use_news_api"] = True

        strategy["use_rss"] = True

        strategy["priority"].append(
            "latest_news"
        )

    # ==========================================
    # MISINFORMATION CLAIMS
    # ==========================================

    if "misinformation" in claim_types:

        strategy["use_factcheck_api"] = True

        strategy["priority"].append(
            "factcheck"
        )

    # ==========================================
    # NUMERIC CLAIMS
    # ==========================================

    if "numeric" in claim_types:

        strategy["priority"].append(
            "cross_source_validation"
        )

    # ==========================================
    # STATEMENT CLAIMS
    # ==========================================

    if "statement" in claim_types:

        strategy["use_news_api"] = True

        strategy["priority"].append(
            "official_sources"
        )

    # ==========================================
    # GENERAL CLAIMS
    # ==========================================

    if "general" in claim_types:

        strategy["use_wikidata"] = True

        strategy["priority"].append(
            "knowledge_lookup"
        )

    return strategy
