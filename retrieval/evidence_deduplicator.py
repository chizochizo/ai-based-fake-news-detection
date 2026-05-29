from rapidfuzz import fuzz


def deduplicate_evidence(
    evidence_list,
    threshold=90
):

    unique = []

    seen_urls = set()

    for evidence in evidence_list:

        # ======================================
        # URL DEDUPLICATION
        # ======================================

        if evidence.source_url in seen_urls:
            continue

        # ======================================
        # CONTENT DEDUPLICATION
        # ======================================

        is_duplicate = False

        for existing in unique:

            similarity = fuzz.token_sort_ratio(

                evidence.content,

                existing.content

            )

            if similarity >= threshold:

                is_duplicate = True
                break

        if not is_duplicate:

            unique.append(
                evidence
            )

            seen_urls.add(
                evidence.source_url
            )

    return unique
