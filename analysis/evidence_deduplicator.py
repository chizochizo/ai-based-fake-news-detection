from rapidfuzz import fuzz


def deduplicate_evidence(
    evidence_list,
    threshold=90
):

    unique = []

    for evidence in evidence_list:

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

    return unique
