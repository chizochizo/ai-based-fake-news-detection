from rapidfuzz import fuzz
from urllib.parse import urlparse


# =====================================================
# URL NORMALIZATION
# =====================================================

def normalize_url(url):

    if not url:

        return ""

    parsed = urlparse(url)

    normalized = (

        parsed.netloc.lower()
        +
        parsed.path.lower()
    )

    normalized = normalized.replace(
        "/",
        ""
    )

    normalized = normalized.replace(
        "-",
        ""
    )

    return normalized


# =====================================================
# TEXT CLEANING
# =====================================================

def clean_text(text):

    if not text:

        return ""

    text = text.lower()

    text = " ".join(
        text.split()
    )

    return text


# =====================================================
# TITLE SIMILARITY
# =====================================================

def title_similarity(
    title_a,
    title_b
):

    return fuzz.token_sort_ratio(

        clean_text(title_a),

        clean_text(title_b)
    )


# =====================================================
# CONTENT SIMILARITY
# =====================================================

def content_similarity(
    text_a,
    text_b
):

    return fuzz.token_set_ratio(

        clean_text(text_a),

        clean_text(text_b)
    )


# =====================================================
# EVENT SIGNATURE
# =====================================================

def build_event_signature(evidence):

    title = clean_text(
        getattr(
            evidence,
            "title",
            ""
        )
    )

    content = clean_text(
        getattr(
            evidence,
            "content",
            ""
        )
    )

    combined = (
        title
        +
        " "
        +
        content
    )

    important_terms = []

    for token in combined.split():

        if len(token) >= 4:

            important_terms.append(
                token
            )

    important_terms = sorted(
        list(set(important_terms))
    )

    signature = " ".join(
        important_terms[:15]
    )

    return signature


# =====================================================
# DUPLICATE CHECK
# =====================================================

def is_duplicate(
    evidence,
    existing,
    threshold
):

    # ==========================================
    # URL SIMILARITY
    # ==========================================

    url_a = normalize_url(
        getattr(
            evidence,
            "source_url",
            ""
        )
    )

    url_b = normalize_url(
        getattr(
            existing,
            "source_url",
            ""
        )
    )

    if url_a and url_b:

        if url_a == url_b:

            return True

        url_similarity = fuzz.ratio(
            url_a,
            url_b
        )

        if url_similarity >= 95:

            return True

    # ==========================================
    # TITLE SIMILARITY
    # ==========================================

    title_score = title_similarity(

        getattr(
            evidence,
            "title",
            ""
        ),

        getattr(
            existing,
            "title",
            ""
        )
    )

    # ==========================================
    # CONTENT SIMILARITY
    # ==========================================

    content_score = content_similarity(

        getattr(
            evidence,
            "content",
            ""
        ),

        getattr(
            existing,
            "content",
            ""
        )
    )

    # ==========================================
    # EVENT SIGNATURE SIMILARITY
    # ==========================================

    signature_a = build_event_signature(
        evidence
    )

    signature_b = build_event_signature(
        existing
    )

    event_similarity = fuzz.token_set_ratio(

        signature_a,

        signature_b
    )

    # ==========================================
    # HARD DUPLICATE
    # ==========================================

    if title_score >= 95:

        return True

    if content_score >= threshold:

        return True

    # ==========================================
    # SAME EVENT DETECTION
    # ==========================================

    if (

        title_score >= 80

        and

        event_similarity >= 85
    ):

        return True

    # ==========================================
    # VERY HIGH SEMANTIC OVERLAP
    # ==========================================

    if (

        content_score >= 88

        and

        event_similarity >= 88
    ):

        return True

    return False


# =====================================================
# BEST EVIDENCE SELECTION
# =====================================================

def choose_better_evidence(
    evidence_a,
    evidence_b
):

    score_a = getattr(
        evidence_a,
        "reranker_score",
        0
    )

    score_b = getattr(
        evidence_b,
        "reranker_score",
        0
    )

    # ==========================================
    # PREFER HIGHER RERANK SCORE
    # ==========================================

    if score_a > score_b:

        return evidence_a

    if score_b > score_a:

        return evidence_b

    # ==========================================
    # PREFER LONGER CONTENT
    # ==========================================

    len_a = len(
        getattr(
            evidence_a,
            "content",
            ""
        )
    )

    len_b = len(
        getattr(
            evidence_b,
            "content",
            ""
        )
    )

    if len_a >= len_b:

        return evidence_a

    return evidence_b


# =====================================================
# MAIN DEDUPLICATION
# =====================================================

def deduplicate_evidence(
    evidence_list,
    threshold=90
):

    unique = []

    for evidence in evidence_list:

        duplicate_found = False

        for idx, existing in enumerate(unique):

            if is_duplicate(

                evidence,
                existing,
                threshold
            ):

                better = choose_better_evidence(

                    evidence,
                    existing
                )

                unique[idx] = better

                duplicate_found = True

                break

        if not duplicate_found:

            unique.append(
                evidence
            )

    return unique
