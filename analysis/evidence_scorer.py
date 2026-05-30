from analysis.semantic_alignment import (
    compute_alignment_score
)

from analysis.source_scorer import (
    compute_source_score
)

from analysis.fact_matcher import (
    compare_fact_structure
)

from analysis.temporal_scorer import (
    compute_temporal_score
)

from urllib.parse import urlparse
from collections import Counter


# =====================================================
# DOMAIN EXTRACTION
# =====================================================

def extract_domain(url):

    try:

        parsed = urlparse(url)

        domain = parsed.netloc.lower()

        domain = domain.replace(
            "www.",
            ""
        )

        return domain

    except:

        return "unknown"


# =====================================================
# PROVENANCE SCORE
# =====================================================

def compute_provenance_score(
    evidence,
    evidence_list=None
):

    if not evidence_list:

        return 0

    domains = []

    for item in evidence_list:

        domain = extract_domain(
            item.source_url
        )

        domains.append(domain)

    domain_counts = Counter(
        domains
    )

    current_domain = extract_domain(
        evidence.source_url
    )

    count = domain_counts.get(
        current_domain,
        1
    )

    # ==========================================
    # INDEPENDENT SOURCE
    # ==========================================

    if count == 1:

        return 2.5

    # ==========================================
    # LIGHT DUPLICATION
    # ==========================================

    elif count <= 3:

        return 0.5

    # ==========================================
    # HEAVY SOURCE DOMINANCE
    # ==========================================

    return -3.0


# =====================================================
# MAIN SCORER
# =====================================================

def compute_evidence_score(
    claim,
    evidence,
    evidence_list=None
):

    # ==========================================
    # RERANK SCORE
    # ==========================================

    rerank_score = max(
        evidence.reranker_score,
        0
    )

    # ==========================================
    # NLI CONFIDENCE
    # ==========================================

    nli_score = (
        evidence.nli_confidence
    )

    # ==========================================
    # SEMANTIC ALIGNMENT
    # ==========================================

    alignment = (
        compute_alignment_score(
            claim,
            evidence.content
        )
    )

    # ==========================================
    # FACT STRUCTURE MATCHING
    # ==========================================

    fact_match = compare_fact_structure(

        claim,

        evidence.content
    )
    print("\n[FACT MATCH DEBUG]")
    print("CLAIM:", claim)
    print("TITLE:", evidence.title)
    print("CONFLICTS:",
          fact_match.get("conflicts", []))

    print("MATCHES:",
          fact_match.get("matches", []))

    print("EXTRACTED:",
          fact_match)

    fact_score = fact_match["score"]

    # ==========================================
    # SOURCE TRUST SCORE
    # ==========================================

    source_score = compute_source_score(
        evidence.source_url
    )

    # ==========================================
    # TEMPORAL SCORE
    # ==========================================

    temporal_score = compute_temporal_score(
        evidence.content
    )

    # ==========================================
    # PROVENANCE SCORE
    # ==========================================

    provenance_score = (
        compute_provenance_score(
            evidence,
            evidence_list
        )
    )

    # ==========================================
    # LABEL BONUS
    # ==========================================

    label_bonus = 0

    if evidence.nli_label == "ENTAILMENT":

        label_bonus = 2.0

    elif evidence.nli_label == "CONTRADICTION":

        label_bonus = -1.5

    # ==========================================
    # CONFLICT PENALTY
    # ==========================================

    conflict_penalty = (

        fact_match["conflict_count"]
        * 1.5
    )

    # ==========================================
    # FINAL COMBINED SCORE
    # ==========================================

    combined = (

        rerank_score * 0.30

        +

        nli_score * 0.20

        +

        alignment * 3.0

        +

        fact_score * 1.5

        +

        source_score

        +

        provenance_score

        +

        temporal_score

        +

        label_bonus

        -

        conflict_penalty
    )

    # ==========================================
    # STORE SCORES
    # ==========================================

    evidence.final_score = combined

    evidence.alignment_score = (
        alignment
    )

    evidence.fact_score = (
        fact_score
    )

    evidence.fact_match = (
        fact_match
    )

    evidence.source_score = (
        source_score
    )

    evidence.temporal_score = (
        temporal_score
    )

    evidence.provenance_score = (
        provenance_score
    )

    evidence.conflict_penalty = (
        conflict_penalty
    )

    return evidence
