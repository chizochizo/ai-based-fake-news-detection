from urllib.parse import urlparse


SOURCE_WEIGHTS = {

    # ==========================================
    # HIGH TRUST
    # ==========================================

    "gov": 10,

    "edu": 9,

    "reuters.com": 9,

    "apnews.com": 9,

    "bbc.com": 8,

    "nytimes.com": 8,

    # ==========================================
    # MEDIUM TRUST
    # ==========================================

    "wikipedia.org": 5,

    "medium.com": 4,

    # ==========================================
    # LOW TRUST
    # ==========================================

    "facebook.com": 2,

    "instagram.com": 2,

    "twitter.com": 2,

    "x.com": 2
}


def get_domain(url):

    try:

        domain = urlparse(
            url
        ).netloc.lower()

        domain = domain.replace(
            "www.",
            ""
        )

        return domain

    except:

        return ""


def compute_source_score(url):

    domain = get_domain(url)

    # ==========================================
    # EXACT MATCH
    # ==========================================

    if domain in SOURCE_WEIGHTS:

        return SOURCE_WEIGHTS[domain]

    # ==========================================
    # DOMAIN SUFFIX MATCH
    # ==========================================

    for key in SOURCE_WEIGHTS:

        if domain.endswith(key):

            return SOURCE_WEIGHTS[key]

    # ==========================================
    # DEFAULT
    # ==========================================

    return 5
