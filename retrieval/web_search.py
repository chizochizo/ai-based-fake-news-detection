import os
import requests
import feedparser
from dotenv import load_dotenv

from ddgs import DDGS

from schemas.evidence_schema import (
    Evidence
)

# =====================================================
# LOAD ENV
# =====================================================

load_dotenv()

# =====================================================
# API KEYS
# =====================================================

TAVILY_API_KEY = os.getenv(
    "TAVILY_API_KEY"
)

SERPER_API_KEY = os.getenv(
    "SERPER_API_KEY"
)

GOOGLE_CSE_ID = os.getenv(
    "GOOGLE_CSE_ID"
)

YOUTUBE_API_KEY = os.getenv(
    "YOUTUBE_API_KEY"
)

# =====================================================
# GOOGLE CSE CONSTANTS
# =====================================================

GOOGLE_CSE_BASE_URL = (
    "https://www.googleapis.com/customsearch/v1"
)

YOUTUBE_SEARCH_URL = (
    "https://www.googleapis.com/youtube/v3/search"
)

# =====================================================
# DUCKDUCKGO SEARCH
# =====================================================


def search_duckduckgo(
    query,
    max_results=5
):

    evidence_list = []

    try:
        print("\n[DDGS SEARCH]")
        print("QUERY:", query)

        with DDGS() as ddgs:

            results = list(
                ddgs.text(
                    query,
                    max_results=max_results
                )
            )

            print(
                "RAW RESULTS:",
                len(results)
            )

            for result in results:

                if isinstance(result, list):
                    for sub_result in result:

                        if not isinstance(
                            sub_result,
                            dict
                        ):
                            continue

                        evidence = Evidence(

                            title=sub_result.get(
                                "title",
                                ""
                            ),

                            content=sub_result.get(
                                "body",
                                ""
                            ),

                            source_url=sub_result.get(
                                "href",
                                ""
                            )
                        )

                        evidence_list.append(
                            evidence
                        )

                elif isinstance(result, dict):
                    evidence = Evidence(
                        title=result.get(
                            "title",
                            ""
                        ),
                        content=result.get(
                            "body",
                            ""
                        ),
                        source_url=result.get(
                            "href",
                            ""
                        )
                    )
                    evidence_list.append(
                        evidence
                    )
    except Exception as e:
        print("\nDDGS ERROR:")
        print(str(e))

        return []
    return evidence_list

# =====================================================
# RSS SEARCH
# =====================================================


RSS_FEEDS = [

    "https://nagalandpost.com/feed/",

    "https://easternmirrornagaland.com/feed/",

    "https://morungexpress.com/feed"
]
RSS_CACHE = {}


def search_rss(
    query,
    max_results=5
):

    evidence_list = []

    query_words = set(
        query.lower().split()
    )

    try:

        for feed_url in RSS_FEEDS:

            if feed_url not in RSS_CACHE:

                RSS_CACHE[feed_url] = feedparser.parse(
                    feed_url
                )
            feed = RSS_CACHE[feed_url]

            for entry in feed.entries:

                title = getattr(
                    entry,
                    "title",
                    ""
                )

                summary = getattr(
                    entry,
                    "summary",
                    ""
                )

                content = (
                    title
                    + " "
                    + summary
                )

                overlap = len(

                    query_words
                    &
                    set(
                        content.lower().split()
                    )
                )

                if overlap == 0:

                    continue

                evidence = Evidence(

                    title=title,

                    content=summary,

                    source_url=getattr(
                        entry,
                        "link",
                        ""
                    )
                )

                evidence_list.append(
                    (
                        overlap,
                        evidence
                    )
                )

        evidence_list.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return [

            evidence

            for _, evidence

            in evidence_list[
                :max_results
            ]
        ]

    except Exception as e:

        print(
            "\nRSS ERROR:"
        )

        print(str(e))

        return []

# =====================================================
# TAVILY SEARCH
# =====================================================


def search_tavily(
    query,
    max_results=5
):

    evidence_list = []

    try:

        response = requests.post(

            "https://api.tavily.com/search",

            json={

                "api_key":
                TAVILY_API_KEY,

                "query":
                query,

                "max_results":
                max_results,

                "search_depth":
                "advanced"
            },

            timeout=5
        )

        data = response.json()

        results = data.get(
            "results",
            []
        )

        for result in results:

            evidence = Evidence(

                title=result.get(
                    "title",
                    ""
                ),

                content=result.get(
                    "content",
                    ""
                ),

                source_url=result.get(
                    "url",
                    ""
                )
            )

            evidence_list.append(
                evidence
            )

    except:

        return []

    return evidence_list


# =====================================================
# SERPER SEARCH
# =====================================================

def search_serper(
    query,
    max_results=5
):

    evidence_list = []

    try:

        response = requests.post(

            "https://google.serper.dev/search",

            headers={

                "X-API-KEY":
                SERPER_API_KEY,

                "Content-Type":
                "application/json"
            },

            json={

                "q": query
            },

            timeout=5
        )

        data = response.json()

        organic = data.get(
            "organic",
            []
        )

        for result in organic[:max_results]:

            evidence = Evidence(

                title=result.get(
                    "title",
                    ""
                ),

                content=result.get(
                    "snippet",
                    ""
                ),

                source_url=result.get(
                    "link",
                    ""
                )
            )

            evidence_list.append(
                evidence
            )

    except:

        return []

    return evidence_list


# =====================================================
# GOOGLE CSE SEARCH
# =====================================================

def search_google_cse(
    query,
    max_results=5
):

    evidence_list = []

    try:

        response = requests.get(

            GOOGLE_CSE_BASE_URL,

            params={

                "key":
                YOUTUBE_API_KEY,

                "cx":
                GOOGLE_CSE_ID,

                "q":
                query,

                "num":
                max_results
            },

            timeout=5
        )

        data = response.json()

        items = data.get(
            "items",
            []
        )

        for item in items:

            evidence = Evidence(

                title=item.get(
                    "title",
                    ""
                ),

                content=item.get(
                    "snippet",
                    ""
                ),

                source_url=item.get(
                    "link",
                    ""
                )
            )

            evidence_list.append(
                evidence
            )

    except Exception as e:
        print("\nGOOGLE CSE ERROR")
        print(str(e))

        return []

    return evidence_list


# =====================================================
# YOUTUBE SEARCH
# =====================================================

def search_youtube(
    query,
    max_results=5
):

    evidence_list = []

    try:

        response = requests.get(

            YOUTUBE_SEARCH_URL,

            params={

                "part":
                "snippet",

                "q":
                query,

                "maxResults":
                max_results,

                "type":
                "video",

                "key":
                YOUTUBE_API_KEY
            },

            timeout=5
        )

        data = response.json()

        items = data.get(
            "items",
            []
        )

        for item in items:

            video_id = item.get(
                "id",
                {}
            ).get(
                "videoId",
                ""
            )

            snippet = item.get(
                "snippet",
                {}
            )

            title = snippet.get(
                "title",
                ""
            )

            description = snippet.get(
                "description",
                ""
            )

            video_url = (
                f"https://www.youtube.com/watch?v={video_id}"
            )

            evidence = Evidence(

                title=title,

                content=description,

                source_url=video_url
            )

            evidence_list.append(
                evidence
            )

    except:

        return []

    return evidence_list


# =====================================================
# ENGINE ROUTER
# =====================================================

def search_web(
    query,
    engine="duckduckgo",
    max_results=5
):

    print("\nSEARCH_WEB CALLED")
    print("ENGINE =", engine)

    if engine == "duckduckgo":

        return search_duckduckgo(

            query=query,

            max_results=max_results
        )

    elif engine == "rss":

        return search_rss(

            query=query,

            max_results=max_results
        )

    elif engine == "tavily":

        return search_tavily(

            query=query,

            max_results=max_results
        )

    elif engine == "serper":

        return search_serper(

            query=query,

            max_results=max_results
        )

    elif engine == "google":
        return search_google_cse(
            query=query,
            max_results=max_results
        )

    elif engine == "google_cse":

        return search_google_cse(

            query=query,

            max_results=max_results
        )

    elif engine == "youtube":

        return search_youtube(

            query=query,

            max_results=max_results
        )

    return []
