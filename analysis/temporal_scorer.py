import re

from datetime import datetime


CURRENT_YEAR = datetime.now().year


# ==========================================
# YEAR EXTRACTION
# ==========================================

def extract_year(text):

    years = re.findall(

        r"\b(?:19|20)\d{2}\b",

        text
    )

    if not years:

        return None

    try:

        return int(years[0])

    except:

        return None


# ==========================================
# TEMPORAL FRESHNESS SCORE
# ==========================================

def compute_temporal_score(content):

    year = extract_year(
        content
    )

    # ==========================================
    # NO YEAR FOUND
    # ==========================================

    if not year:

        return 5

    age = CURRENT_YEAR - year

    # ==========================================
    # VERY RECENT
    # ==========================================

    if age <= 1:

        return 10

    # ==========================================
    # RECENT
    # ==========================================

    if age <= 3:

        return 8

    # ==========================================
    # MODERATE
    # ==========================================

    if age <= 5:

        return 6

    # ==========================================
    # OLD
    # ==========================================

    if age <= 10:

        return 4

    # ==========================================
    # VERY OLD
    # ==========================================

    return 2


# ==========================================
# NUMBER EXTRACTION
# ==========================================

def extract_numbers(text):

    return re.findall(

        r"\b\d+(?:st|nd|rd|th)?\b",

        text.lower()
    )


# ==========================================
# TEMPORAL CONSISTENCY
# ==========================================

def compute_temporal_consistency(
    claim,
    evidence
):

    score = 0

    # ==========================================
    # EXTRACT NUMBERS
    # ==========================================

    claim_numbers = extract_numbers(
        claim
    )

    evidence_numbers = extract_numbers(
        evidence
    )

    # ==========================================
    # NUMBER MATCHING
    # ==========================================

    if claim_numbers:

        matches = 0

        for number in claim_numbers:

            if number in evidence_numbers:

                matches += 1

        ratio = (

            matches
            /
            len(claim_numbers)

        )

        score += ratio * 10

    # ==========================================
    # EXTRACT YEARS
    # ==========================================

    claim_year = extract_year(
        claim
    )

    evidence_year = extract_year(
        evidence
    )

    # ==========================================
    # YEAR MATCHING
    # ==========================================

    if claim_year and evidence_year:

        if claim_year == evidence_year:

            score += 10

        else:

            difference = abs(

                claim_year
                -
                evidence_year
            )

            if difference <= 1:

                score += 5

    return score
