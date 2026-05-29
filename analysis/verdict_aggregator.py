from collections import defaultdict

from analysis.evidence_scorer import (
    compute_evidence_score
)

from analysis.consensus_engine import (
    compute_consensus
)

from analysis.semantic_alignment import (
    compute_alignment_score
)


# =====================================================
# EVIDENCE CLUSTERING
# =====================================================

def cluster_evidence(
    evidence_list,
    threshold=0.72
):

    clusters = []

    used = set()

    for i, evidence_a in enumerate(
        evidence_list
    ):

        if i in used:

            continue

        cluster = [evidence_a]

        used.add(i)

        for j, evidence_b in enumerate(
            evidence_list
        ):

            if j in used:

                continue

            similarity = (
                compute_alignment_score(
                    evidence_a.content,
                    evidence_b.content
                )
            )

            if similarity >= threshold:

                cluster.append(
                    evidence_b
                )

                used.add(j)

        clusters.append(cluster)

    return clusters


# =====================================================
# CLUSTER ANALYSIS
# =====================================================

def analyze_clusters(clusters):

    cluster_data = []

    for cluster in clusters:

        labels = defaultdict(int)

        total_score = 0

        domains = set()

        for evidence in cluster:

            labels[
                evidence.nli_label
            ] += 1

            total_score += (
                evidence.final_score
            )

            domains.add(
                evidence.source_url
            )

        dominant_label = max(
            labels,
            key=labels.get
        )

        cluster_data.append({

            "size":
            len(cluster),

            "label":
            dominant_label,

            "avg_score":
            total_score
            /
            max(len(cluster), 1),

            "unique_sources":
            len(domains),

            "evidence":
            cluster
        })

    return cluster_data


# =====================================================
# MAIN VERDICT AGGREGATION
# =====================================================

def aggregate_verdicts(
    claim,
    evidence_list
):

    scored_evidence = []

    # ==========================================
    # SCORE ALL EVIDENCE
    # ==========================================

    for evidence in evidence_list:

        scored = compute_evidence_score(

            claim,
            evidence,
            evidence_list
        )

        scored_evidence.append(
            scored
        )

    # ==========================================
    # SAFETY CHECK
    # ==========================================

    if not scored_evidence:

        return {

            "verdict": "NEUTRAL",

            "confidence": 0.0,

            "top_evidence": None,

            "margin": 0,

            "cross_contradictions": [],

            "evidence_clusters": []
        }

    # ==========================================
    # SORT BY FINAL SCORE
    # ==========================================

    scored_evidence.sort(

        key=lambda x: x.final_score,

        reverse=True
    )

    # ==========================================
    # EVIDENCE CLUSTERING
    # ==========================================

    clusters = cluster_evidence(
        scored_evidence[:10]
    )

    cluster_analysis = analyze_clusters(
        clusters
    )

    # ==========================================
    # CLUSTER BOOSTS
    # ==========================================

    entailment_cluster_boost = 0

    contradiction_cluster_boost = 0

    neutral_cluster_boost = 0

    for cluster in cluster_analysis:

        # ------------------------------
        # MULTI-SOURCE BONUS
        # ------------------------------

        source_bonus = min(
            cluster["unique_sources"],
            4
        )

        cluster_strength = (

            cluster["size"]
            *
            source_bonus
            *
            1.5
        )

        if cluster["label"] == "ENTAILMENT":

            entailment_cluster_boost += (
                cluster_strength
            )

        elif cluster["label"] == "CONTRADICTION":

            contradiction_cluster_boost += (
                cluster_strength
            )

        else:

            neutral_cluster_boost += (
                cluster_strength
            )

    # ==========================================
    # CROSS-EVIDENCE CONTRADICTION ANALYSIS
    # ==========================================

    contradiction_pairs = []

    contradiction_penalty = 0

    top_window = scored_evidence[:5]

    for i in range(len(top_window)):

        for j in range(i + 1, len(top_window)):

            evidence_a = top_window[i]

            evidence_b = top_window[j]

            conflicts_a = (
                evidence_a.fact_match.get(
                    "conflicts",
                    []
                )
            )

            conflicts_b = (
                evidence_b.fact_match.get(
                    "conflicts",
                    []
                )
            )

            # ----------------------------------
            # OPPOSITE NLI SIGNALS
            # ----------------------------------

            opposite_labels = (

                (
                    evidence_a.nli_label
                    ==
                    "ENTAILMENT"

                    and

                    evidence_b.nli_label
                    ==
                    "CONTRADICTION"
                )

                or

                (
                    evidence_a.nli_label
                    ==
                    "CONTRADICTION"

                    and

                    evidence_b.nli_label
                    ==
                    "ENTAILMENT"
                )
            )

            # ----------------------------------
            # STRONG FACT CONFLICTS
            # ----------------------------------

            strong_conflict = (

                "action_conflict"
                in conflicts_a

                or

                "action_conflict"
                in conflicts_b

                or

                "year_conflict"
                in conflicts_a

                or

                "year_conflict"
                in conflicts_b

                or

                "number_conflict"
                in conflicts_a

                or

                "number_conflict"
                in conflicts_b

                or

                "negation_conflict"
                in conflicts_a

                or

                "negation_conflict"
                in conflicts_b
            )

            # ----------------------------------
            # REGISTER CONTRADICTION
            # ----------------------------------

            if opposite_labels or strong_conflict:

                contradiction_pairs.append({

                    "evidence_a":
                    evidence_a.title,

                    "evidence_b":
                    evidence_b.title,

                    "label_a":
                    evidence_a.nli_label,

                    "label_b":
                    evidence_b.nli_label,

                    "conflicts_a":
                    conflicts_a,

                    "conflicts_b":
                    conflicts_b
                })

                contradiction_penalty += 2

    # ==========================================
    # CONSENSUS ANALYSIS
    # ==========================================

    consensus = compute_consensus(
        scored_evidence[:10]
    )

    # ==========================================
    # TOP EVIDENCE
    # ==========================================

    top = scored_evidence[0]

    # ==========================================
    # LABEL COUNTS
    # ==========================================

    entailment_count = 0

    contradiction_count = 0

    neutral_count = 0

    # ==========================================
    # WEIGHTED LABEL SCORES
    # ==========================================

    entailment_score = 0

    contradiction_score = 0

    neutral_score = 0

    for evidence in scored_evidence[:5]:

        if evidence.nli_label == "ENTAILMENT":

            entailment_count += 1

            entailment_score += (
                evidence.final_score
            )

        elif evidence.nli_label == "CONTRADICTION":

            contradiction_count += 1

            contradiction_score += (
                evidence.final_score
            )

        else:

            neutral_count += 1

            neutral_score += (
                evidence.final_score
            )

    # ==========================================
    # APPLY CLUSTER BOOSTS
    # ==========================================

    entailment_score += (
        entailment_cluster_boost
    )

    contradiction_score += (
        contradiction_cluster_boost
    )

    neutral_score += (
        neutral_cluster_boost
    )

    # ==========================================
    # APPLY CONTRADICTION PENALTY
    # ==========================================

    entailment_score -= contradiction_penalty

    contradiction_score += (
        contradiction_penalty * 0.5
    )

    # ==========================================
    # WEIGHTED VOTING
    # ==========================================

    label_scores = {

        "ENTAILMENT": entailment_score,

        "NEUTRAL": neutral_score,

        "CONTRADICTION": contradiction_score
    }

    weighted_winner = max(

        label_scores,

        key=label_scores.get
    )

    # ==========================================
    # DOMINANCE MARGIN
    # ==========================================

    second_score = 0

    if len(scored_evidence) > 1:

        second_score = (
            scored_evidence[1]
            .final_score
        )

    margin = (
        top.final_score
        -
        second_score
    )

    # ==========================================
    # INITIAL LABEL
    # ==========================================

    verdict = weighted_winner

    # ==========================================
    # STRONG ENTAILMENT OVERRIDE
    # ==========================================

    strong_entailments = [

        e for e in scored_evidence[:5]

        if (

            e.nli_label == "ENTAILMENT"

            and

            e.final_score >= 30

            and

            e.alignment_score >= 0.60

        )
    ]

    if len(strong_entailments) >= 1:

        verdict = "ENTAILMENT"

    # ==========================================
    # STRONG CONTRADICTION OVERRIDE
    # ==========================================

    strong_contradictions = [

        e for e in scored_evidence[:5]

        if (

            e.nli_label == "CONTRADICTION"

            and

            e.final_score >= 30

            and

            e.alignment_score >= 0.60

        )
    ]

    if len(strong_contradictions) >= 1:

        verdict = "CONTRADICTION"

    # ==========================================
    # FALLBACK MAJORITY LOGIC
    # ==========================================

    if verdict == "NEUTRAL":

        if entailment_count >= 2:

            verdict = "ENTAILMENT"

        elif contradiction_count >= 2:

            verdict = "CONTRADICTION"

    # ==========================================
    # STRONG ENTAILMENT RULE
    # ==========================================

    if (

        entailment_count >= 2

        and

        top.alignment_score > 0.60

        and

        top.fact_score > 10

    ):

        verdict = "ENTAILMENT"

    # ==========================================
    # STRONG CONTRADICTION RULE
    # ==========================================

    if (

        contradiction_count >= 2

        and

        top.alignment_score > 0.60

    ):

        verdict = "CONTRADICTION"

    # ==========================================
    # OVERRIDE NEUTRAL
    # ==========================================

    if (

        top.final_score > 25

        and

        top.alignment_score > 0.65

        and

        top.fact_score > 12

    ):

        if top.nli_label == "NEUTRAL":

            verdict = "ENTAILMENT"

    # ==========================================
    # HIGH CONSENSUS OVERRIDE
    # ==========================================

    if (

        entailment_score > neutral_score

        and

        entailment_score > contradiction_score

        and

        entailment_score > 40

    ):

        verdict = "ENTAILMENT"

    # ==========================================
    # CONTRADICTION INSTABILITY CHECK
    # ==========================================

    if (

        len(contradiction_pairs) >= 3

        and

        verdict == "ENTAILMENT"
    ):

        verdict = "NEUTRAL"

    # ==========================================
    # CLUSTER STABILITY CHECK
    # ==========================================

    strong_entailment_clusters = len([

        c for c in cluster_analysis

        if (

            c["label"] == "ENTAILMENT"

            and

            c["size"] >= 2
        )
    ])

    strong_contradiction_clusters = len([

        c for c in cluster_analysis

        if (

            c["label"] == "CONTRADICTION"

            and

            c["size"] >= 2
        )
    ])

    if (

        strong_contradiction_clusters
        >
        strong_entailment_clusters

        and

        verdict == "ENTAILMENT"
    ):

        verdict = "NEUTRAL"

    # ==========================================
    # CONFIDENCE
    # ==========================================

    confidence = min(

        1.0,

        (
            (
                top.final_score
                /
                40
            )
            * 0.5
            +
            consensus["strength"]
            * 0.3
            +
            (
                label_scores.get(
                    verdict,
                    0
                )
                /
                100
            )
            * 0.2
        )
    )

    # ==========================================
    # CONFIDENCE REDUCTION
    # ==========================================

    confidence -= (
        contradiction_penalty * 0.02
    )

    confidence = max(
        confidence,
        0.0
    )

    # ==========================================
    # RETURN
    # ==========================================

    return {

        "verdict": verdict,

        "confidence": confidence,

        "top_evidence": top,

        "margin": margin,

        "consensus": consensus,

        "label_scores": label_scores,

        "cross_contradictions":
        contradiction_pairs,

        "contradiction_penalty":
        contradiction_penalty,

        "evidence_clusters":
        cluster_analysis
    }
