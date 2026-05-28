def deduplicate_evidence(evidence_list):

    unique = {}

    for evidence in evidence_list:

        key = evidence.content.strip()

        if key not in unique:

            unique[key] = evidence

    return list(unique.values())
