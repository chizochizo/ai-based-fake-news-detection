import re

# =====================================================
# CLAIM TYPE KEYWORDS
# =====================================================

NEWS_KEYWORDS = {

    "today",
    "yesterday",
    "latest",
    "breaking",
    "currently",
    "reported",
    "announced",
    "confirmed",
    "said",
    "stated",
    "news",
    "update",
    "updates",
    "headline",
    "headlines",
    "developing",
    "report",
    "reports",
    "media",
    "journalist",
    "press",
    "revealed"
}

POLITICAL_KEYWORDS = {

    "government",
    "minister",
    "prime minister",
    "chief minister",
    "cm",
    "mp",
    "mla",
    "parliament",
    "assembly",
    "election",
    "vote",
    "voting",
    "candidate",
    "campaign",
    "political",
    "politics",
    "party",
    "opposition",
    "cabinet",
    "governor",
    "president",
    "vice president",
    "bjp",
    "congress",
    "aap",
    "npp",
    "ndpp",
    "lok sabha",
    "rajya sabha"
}

INSTITUTIONAL_KEYWORDS = {

    "university",
    "college",
    "school",
    "hospital",
    "department",
    "ministry",
    "agency",
    "board",
    "commission",
    "authority",
    "council",
    "organisation",
    "organization",
    "institute",
    "institution",
    "directorate",
    "bureau",
    "mission",
    "corporation",
    "academy",
    "committee",
    "office",
    "secretariat"
}

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
    "launch",
    "inaugurated",
    "celebrated",
    "conducted",
    "competition",
    "program",
    "programme",
    "expo",
    "conclave",
    "session",
    "gathering",
    "rally",
    "march",
    "protest"
}

REGIONAL_KEYWORDS = {

    "nagaland",
    "naga",

    "kohima",
    "dimapur",
    "mokokchung",
    "tuensang",
    "mon",
    "wokha",
    "zunheboto",
    "kiphire",
    "peren",
    "longleng",
    "noklak",
    "pfutsero",
    "jalukie",

    "nagaland university",
    "nsdma",
    "npsc",
    "hornbill festival",

    "ao",
    "angami",
    "sema",
    "sumi",
    "lotha",
    "chang",
    "konyak"
}
CRIME_INCIDENT_KEYWORDS = {

    "killed",
    "injured",
    "dead",
    "died",
    "murdered",
    "shot",
    "stabbed",
    "arrested",
    "detained",
    "kidnapped",
    "abducted",
    "missing",
    "stolen",
    "robbed",
    "theft",
    "fraud",
    "scam",
    "attack",
    "attacked",
    "violence",
    "clash",
    "riot",
    "accident",
    "crash",
    "fire",
    "explosion",
    "blast",
    "earthquake",
    "flood",
    "landslide",
    "cyclone"
}
FACTUAL_KEYWORDS = {

    "killed",
    "injured",
    "died",
    "dead",
    "arrested",
    "missing",
    "hospitalized",
    "hospitalised",
    "confirmed",
    "officially",
    "according"
}

# =====================================================
# CLAIM CLASSIFIER
# =====================================================


def classify_claim(
    claim
):

    text = claim.lower()

    claim_types = []

    # ==========================================
    # REGIONAL
    # ==========================================

    if any(

        keyword in text

        for keyword

        in REGIONAL_KEYWORDS
    ):

        claim_types.append(
            "regional"
        )

    # ==========================================
    # POLITICAL
    # ==========================================

    if any(

        keyword in text

        for keyword

        in POLITICAL_KEYWORDS
    ):

        claim_types.append(
            "political"
        )

    # ==========================================
    # INSTITUTIONAL
    # ==========================================

    if any(

        keyword in text

        for keyword

        in INSTITUTIONAL_KEYWORDS
    ):

        claim_types.append(
            "institutional"
        )

    # ==========================================
    # EVENT
    # ==========================================

    if any(

        keyword in text

        for keyword

        in EVENT_KEYWORDS
    ):

        claim_types.append(
            "event"
        )
    # ==========================================
    # FACTUAL CLAIM
    # ==========================================

    if any(
        word in text
        for word in FACTUAL_KEYWORDS
    ):

        claim_types.append(
            "factual"
        )

    # ==========================================
    # NEWS
    # ==========================================

    if any(

        keyword in text

        for keyword

        in NEWS_KEYWORDS
    ):

        claim_types.append(
            "news"
        )

    # ---
    # CRIME INCIDENT KEYWORDS
    # ----
    if any(
        keyword in text
        for keyword in CRIME_INCIDENT_KEYWORDS
    ):
        if "news" not in claim_types:
            claim_types.append(
                "news"
            )

    # ==========================================
    # NUMBER DETECTION
    # ==========================================

    if re.search(r"\b\d+\b", text):

        if "factual" not in claim_types:

            claim_types.append(
                "factual"
            )

    # ==========================================
    # FACTUAL
    # ==========================================

    if not claim_types:
        claim_types.append(
            "factual"
        )

    # ==========================================
    # RETURN
    # ==========================================

    return {

        "claim_types":
        claim_types
    }
