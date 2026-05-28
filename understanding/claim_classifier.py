def classify_claim(claim):

    claim = claim.lower()

    if any(
        word in claim

        for word in [
            "fake",
            "hoax",
            "scam",
            "false"
        ]
    ):

        return "misinformation"

    if any(
        word in claim

        for word in [
            "said",
            "announced",
            "reported"
        ]
    ):

        return "statement"

    if any(
        word in claim

        for word in [
            "won",
            "hosted",
            "organized"
        ]
    ):

        return "event"

    return "general"
