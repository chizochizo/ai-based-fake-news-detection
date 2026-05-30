from understanding.claim_classifier import (
    classify_claim,
    determine_retrieval_strategy
)

from retrieval.evidence_deduplicator import (
    deduplicate_evidence
)

from retrieval.cross_encoder_reranker import (
    rerank_evidence
)

from retrieval.web_search import (
    search_web
)
from retrieval.bm25_retriever import (bm25_rank_evidence)

from analysis.nli_analyzer import (
    analyze_claim_evidence
)

# =====================================================
# CONFIGURATION
# =====================================================

MIN_EVIDENCE_COUNT = 5

MIN_STRONG_MATCHES = 3

MIN_RERANK_SCORE = 0.60

MAX_TOTAL_EVIDENCE = 30

MAX_RESULTS_PER_QUERY = 5

MAX_QUERIES_PER_ENGINE = 3

MAX_EMPTY_ENGINES = 2

MIN_ENGINE_YIELD = 2

SATURATION_LIMIT = 2


# =====================================================
# EVIDENCE SUFFICIENCY CHECK
# =====================================================

def enough_evidence(
    evidence
):

    if len(evidence) >= MIN_EVIDENCE_COUNT:

        strong_matches = [

            item for item in evidence

            if getattr(
                item,
                "reranker_score",
                0
            ) >= MIN_RERANK_SCORE
        ]

        if len(strong_matches) >= MIN_STRONG_MATCHES:

            return True

    return False


# =====================================================
# ENGINE EXECUTION
# =====================================================

def run_engine(
    engine,
    query
):

    try:

        print(f"\n[ENGINE] {engine}")
        print(f"[QUERY] {query}")

        results = search_web(

            query=query,

            engine=engine
        )

        print(
            f"[RESULT COUNT] {len(results)}"
        )

        if not results:

            return []

        return results[
            :MAX_RESULTS_PER_QUERY
        ]

    except Exception as e:

        print("\n[SEARCH ERROR]")
        print(str(e))

        return []


# =====================================================
# QUERY PRIORITIZATION
# =====================================================

def prioritize_queries(
    queries
):

    sorted_queries = sorted(

        queries,

        key=lambda q: len(q.split())
    )

    return sorted_queries[
        :MAX_QUERIES_PER_ENGINE
    ]


# =====================================================
# EARLY RERANK CHECK
# =====================================================

def quick_rerank_check(
    claim,
    evidence
):

    if not evidence:

        return []

    try:

        ranked = rerank_evidence(

            claim,
            evidence
        )

        return ranked

    except Exception:

        return evidence


# =====================================================
# STRONG MATCH EXTRACTION
# =====================================================

def extract_strong_matches(
    evidence
):

    return [

        item for item in evidence

        if getattr(
            item,
            "reranker_score",
            0
        ) >= MIN_RERANK_SCORE
    ]


# =====================================================
# RETRIEVAL SATURATION CHECK
# =====================================================

def retrieval_saturated(
    previous_count,
    current_count
):

    growth = (
        current_count
        -
        previous_count
    )

    if growth <= 2:

        return True

    return False


# =====================================================
# ENGINE SELECTION
# =====================================================

def determine_search_engines(
    strategy
):

    engines = ["google"]

    if strategy.get(
        "use_news_api",
        False
    ):

        engines.append(
            "bing"
        )

    if strategy.get(
        "use_factcheck_api",
        False
    ):

        engines.append(
            "duckduckgo"
        )

    if strategy.get(
        "use_rss",
        False
    ):

        engines.append(
            "google_news"
        )

    return list(set(engines))


# =====================================================
# MAIN RETRIEVAL PIPELINE
# =====================================================

def retrieve_evidence(
    claim,
    queries
):

    # ==========================================
    # CLAIM CLASSIFICATION
    # ==========================================

    claim_info = classify_claim(
        claim
    )

    claim_type = claim_info.get(
        "claim_types",
        ["general"]
    )

    strategy = claim_info.get(
        "retrieval_strategy",
        {}
    )

    # ==========================================
    # ENGINE SELECTION
    # ==========================================

    engines = [
        "duckduckgo"
    ]

    # ==========================================
    # QUERY PRIORITIZATION
    # ==========================================

    prioritized_queries = (
        prioritize_queries(
            queries
        )
    )

    all_evidence = []

    used_engines = []

    stage_logs = []

    empty_engine_count = 0

    saturation_counter = 0

    previous_total = 0

    # ==========================================
    # STAGED RETRIEVAL
    # ==========================================

    for engine in engines:

        engine_results = []

        # --------------------------------------
        # RUN SEARCHES
        # --------------------------------------

        for query in prioritized_queries:

            results = run_engine(

                engine,
                query
            )

            engine_results.extend(
                results
            )

        # --------------------------------------
        # DEDUPLICATION
        # --------------------------------------

        engine_results = (
            deduplicate_evidence(
                engine_results
            )
        )

        # --------------------------------------
        # TRACK SUCCESSFUL ENGINE
        # --------------------------------------

        if engine_results:

            used_engines.append(
                engine
            )

        # --------------------------------------
        # LOW-YIELD ENGINE DETECTION
        # --------------------------------------

        if len(engine_results) < MIN_ENGINE_YIELD:

            empty_engine_count += 1

        # --------------------------------------
        # GLOBAL ADD
        # --------------------------------------

        all_evidence.extend(
            engine_results
        )

        # --------------------------------------
        # GLOBAL DEDUP
        # --------------------------------------

        all_evidence = (
            deduplicate_evidence(
                all_evidence
            )
        )

        # --------------------------------------
        # LIMIT TOTAL EVIDENCE
        # --------------------------------------

        all_evidence = all_evidence[
            :MAX_TOTAL_EVIDENCE
        ]

        # --------------------------------------
        # QUICK RERANK
        # --------------------------------------

        # -----
        # BM25 ranking
        # -----
        bm25_ranked = bm25_rank_evidence(
            claim,
            all_evidence,
            top_k=15
        )
        # ----
        # DENSE rerank
        # ----
        reranked_preview = quick_rerank_check(
            claim,
            bm25_ranked
        )

        # --------------------------------------
        # STRONG MATCHES
        # --------------------------------------

        strong_matches = (
            extract_strong_matches(
                reranked_preview
            )
        )

        # --------------------------------------
        # RETRIEVAL SATURATION
        # --------------------------------------

        current_total = len(
            strong_matches
        )

        if retrieval_saturated(

            previous_total,

            current_total
        ):

            saturation_counter += 1

        else:

            saturation_counter = 0

        previous_total = current_total

        # --------------------------------------
        # STAGE LOGGING
        # --------------------------------------

        stage_logs.append({

            "engine":
            engine,

            "retrieved":
            len(engine_results),

            "total_evidence":
            len(all_evidence),

            "strong_matches":
            len(strong_matches),

            "saturation":
            saturation_counter
        })

        # --------------------------------------
        # EARLY STOP:
        # ENOUGH STRONG EVIDENCE
        # --------------------------------------

        if enough_evidence(
            reranked_preview
        ):

            all_evidence = (
                reranked_preview
            )

            break

        # --------------------------------------
        # EARLY STOP:
        # TOO MANY EMPTY ENGINES
        # --------------------------------------

        if empty_engine_count >= MAX_EMPTY_ENGINES:

            break

        # --------------------------------------
        # EARLY STOP:
        # RETRIEVAL SATURATED
        # --------------------------------------

        if saturation_counter >= SATURATION_LIMIT:

            break

    # ==========================================
    # FINAL RERANK
    # ==========================================

    if all_evidence:

        bm25_final = bm25_rank_evidence(
            claim,
            all_evidence,
            top_k=15
        )
        final_ranked = rerank_evidence(
            claim,
            bm25_final
        )
        final_ranked = analyze_claim_evidence(
            claim,
            final_ranked
        )

    else:

        final_ranked = []

    # ==========================================
    # RETURN
    # ==========================================

    return {

        "evidence": final_ranked,

        "engines_used":
        used_engines,

        "claim_type":
        claim_type,

        "stage_logs":
        stage_logs
    }


# =====================================================
# RERANKING PIPELINE
# =====================================================

def rerank_evidence_pipeline(
    claim,
    evidence
):

    ranked = rerank_evidence(

        claim,
        evidence
    )

    return ranked
