from understanding.claim_classifier import classify_claim
from retrieval.evidence_deduplicator import deduplicate_evidence
from retrieval.cross_encoder_reranker import rerank_evidence
from retrieval.web_search import search_web
from retrieval.bm25_retriever import bm25_rank_evidence
from analysis.nli_analyzer import analyze_claim_evidence
from retrieval.wiki_retriever import retrieve_wikipedia

# =====================================================
# CONFIGURATION
# =====================================================

MIN_EVIDENCE_COUNT = 5
MIN_STRONG_MATCHES = 3
MIN_RERANK_SCORE = 3.0
VERY_STRONG_SCORE = 0.80
MAX_TOTAL_EVIDENCE = 40
MIN_STRONG_RERANK_SCORE = 5.0
MAX_RESULTS_PER_QUERY = 3
MAX_QUERIES_PER_ENGINE = 3
MAX_EMPTY_ENGINES = 2
MIN_ENGINE_YIELD = 2
SATURATION_LIMIT = 2


# =====================================================
# EVIDENCE SUFFICIENCY CHECK
# =====================================================

def enough_evidence(evidence):
    if len(evidence) >= MIN_EVIDENCE_COUNT:
        strong_matches = [
            item for item in evidence
            if getattr(item, "reranker_score", 0) >= MIN_STRONG_RERANK_SCORE
        ]
        if len(strong_matches) >= MIN_STRONG_MATCHES:
            return True
    return False


# =====================================================
# ENGINE EXECUTION
# =====================================================

def run_engine(engine, query):
    try:
        print(f"\n[ENGINE] {engine}")
        print(f"[QUERY] {query}")

        results = search_web(query=query, engine=engine)
        print(f"[RESULT COUNT] {len(results)}")

        if not results:
            return []

        return results[:MAX_RESULTS_PER_QUERY]
    except Exception as e:
        return []


# =====================================================
# QUERY PRIORITIZATION
# =====================================================

def prioritize_queries(queries):

    scored = []

    for q in queries:

        score = len(q.split())

        scored.append(
            (score, q)
        )

    scored.sort(
        reverse=True
    )

    return [
        q
        for score, q
        in scored[:MAX_QUERIES_PER_ENGINE]
    ]


# =====================================================
# EARLY RERANK CHECK
# =====================================================

def quick_rerank_check(claim, evidence):
    if not evidence:
        return []
    try:
        ranked = rerank_evidence(claim, evidence)
        return ranked
    except Exception:
        return evidence


# =====================================================
# STRONG MATCH EXTRACTION
# =====================================================

def extract_strong_matches(evidence):
    return [
        item for item in evidence
        if getattr(item, "reranker_score", 0) >= MIN_RERANK_SCORE
    ]


# =====================================================
# VERY STRONG MATCH CHECK
# =====================================================

def has_very_strong_match(evidence):
    for item in evidence:
        if getattr(item, "reranker_score", 0) >= VERY_STRONG_SCORE:
            return True
    return False


# =====================================================
# RETRIEVAL SATURATION CHECK
# =====================================================

def retrieval_saturated(previous_count, current_count):
    growth = current_count - previous_count
    if growth <= 0:
        return True
    return False


# =====================================================
# ENGINE SELECTION
# =====================================================

def determine_search_engines(claim_type):
    claim_type = str(claim_type).lower()

    if claim_type == "factual":
        return ["tavily", "serper", "duckduckgo"]
    elif claim_type == "news":
        return ["serper", "tavily", "duckduckgo"]
    elif claim_type == "political":
        return ["serper", "tavily", "duckduckgo"]
    elif claim_type == "institutional":
        return ["tavily", "serper", "duckduckgo"]
    elif claim_type == "event":
        return ["serper", "tavily", "duckduckgo"]
    elif claim_type == "regional":
        return ["serper", "duckduckgo", "youtube"]

    return ["tavily", "serper", "duckduckgo"]


# =====================================================
# MAIN RETRIEVAL PIPELINE
# =====================================================

def retrieve_evidence(claim, queries, decomposition=None):
    # ==========================================
    # CLAIM CLASSIFICATION
    # ==========================================
    claim_info = classify_claim(claim)
    print(claim_info)

    claim_type = claim_info.get("claim_types", ["general"])

    # ==========================================
    # ENGINE SELECTION
    # ==========================================
    claim_types_lower = [str(t).lower() for t in claim_type]

    if "institutional" in claim_types_lower:
        primary_type = "institutional"
    elif "political" in claim_types_lower:
        primary_type = "political"
    elif "event" in claim_types_lower:
        primary_type = "event"
    elif "news" in claim_types_lower:
        primary_type = "news"
    elif "regional" in claim_types_lower:
        primary_type = "regional"
    elif "factual" in claim_types_lower:
        primary_type = "factual"
    else:
        primary_type = "factual"

    engines = determine_search_engines(primary_type)
    print("\nCLAIM TYPES:", claim_type)
    print("PRIMARY TYPE:", primary_type)
    print("ENGINES:", engines)

    # ==========================================
    # QUERY PRIORITIZATION
    # ==========================================
    prioritized_queries = prioritize_queries(queries)
    print("\n[QUERIES PASSED TO RETRIEVER]")
    for q in queries:
        print(q)

    all_evidence = []

    # ==========================================
    # WIKIPEDIA RETRIEVAL
    # ==========================================

    wiki_results = retrieve_wikipedia(
        claim,
        decomposition
    )

    all_evidence.extend(
        wiki_results
    )
    all_evidence = deduplicate_evidence(
        all_evidence
    )

    print(
        f"\n[WIKIPEDIA] {len(wiki_results)} results"
    )

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
            results = run_engine(engine, query)
            engine_results.extend(results)

        # --------------------------------------
        # DEDUPLICATION
        # --------------------------------------
        engine_results = deduplicate_evidence(engine_results)
        print("\n[ENGINE RESULTS]")

        for e in engine_results[:10]:

            print(
                e.title
            )

        # --------------------------------------
        # TRACK SUCCESSFUL ENGINE
        # --------------------------------------
        if engine_results:
            used_engines.append(engine)

        # --------------------------------------
        # LOW-YIELD ENGINE DETECTION
        # --------------------------------------
        if len(engine_results) < MIN_ENGINE_YIELD:
            empty_engine_count += 1

        # --------------------------------------
        # GLOBAL ADD
        # --------------------------------------
        all_evidence.extend(engine_results)

        # --------------------------------------
        # GLOBAL DEDUP
        # --------------------------------------
        all_evidence = deduplicate_evidence(all_evidence)

        # --------------------------------------
        # LIMIT TOTAL EVIDENCE
        # --------------------------------------
        all_evidence = all_evidence[:MAX_TOTAL_EVIDENCE]

        # --------------------------------------
        # QUICK RERANK
        # --------------------------------------
        # -----
        # BM25 ranking
        # -----
        bm25_ranked = bm25_rank_evidence(claim, all_evidence, top_k=20)

        # ----
        # DENSE rerank
        # ----
        reranked_preview = quick_rerank_check(claim, bm25_ranked)

        # if has_very_strong_match(reranked_preview):
        #   all_evidence = reranked_preview
        #  break

        # --------------------------------------
        # STRONG MATCHES
        # --------------------------------------
        strong_matches = extract_strong_matches(reranked_preview)

        # --------------------------------------
        # RETRIEVAL SATURATION
        # --------------------------------------
        current_total = len(strong_matches)

        if retrieval_saturated(previous_total, current_total):
            saturation_counter += 1
        else:
            saturation_counter = 0

        previous_total = current_total

        # --------------------------------------
        # STAGE LOGGING
        # --------------------------------------
        stage_logs.append({
            "engine": engine,
            "retrieved": len(engine_results),
            "total_evidence": len(all_evidence),
            "strong_matches": len(strong_matches),
            "saturation": saturation_counter
        })

        print("\n[EARLY STOP CHECK]")

        for e in reranked_preview:
            print(
                e.title[:60],
                getattr(e, "reranker_score", 0)
            )

        # --------------------------------------
        # EARLY STOP: ENOUGH STRONG EVIDENCE
        # --------------------------------------
        if enough_evidence(reranked_preview):
            all_evidence = reranked_preview
            break

        # --------------------------------------
        # EARLY STOP: TOO MANY EMPTY ENGINES
        # --------------------------------------
        if empty_engine_count >= MAX_EMPTY_ENGINES:
            break

        # --------------------------------------
        # EARLY STOP: RETRIEVAL SATURATED
        # --------------------------------------
        if saturation_counter >= SATURATION_LIMIT:
            break

    # ==========================================
    # FINAL RERANK
    # ==========================================
    if all_evidence:
        bm25_final = bm25_rank_evidence(claim, all_evidence, top_k=20)
        final_ranked = rerank_evidence(claim, bm25_final)
        final_ranked = final_ranked[:5]
        print("\n[NLI EVIDENCE COUNT]", len(final_ranked))
        final_ranked = analyze_claim_evidence(claim, final_ranked)
    else:
        final_ranked = []

    # ==========================================
    # RETURN
    # ==========================================
    return {
        "evidence": final_ranked,
        "engines_used": used_engines,
        "claim_type": claim_type,
        "stage_logs": stage_logs
    }


# =====================================================
# RERANKING PIPELINE
# =====================================================

def rerank_evidence_pipeline(claim, evidence):
    ranked = rerank_evidence(claim, evidence)
    return ranked
