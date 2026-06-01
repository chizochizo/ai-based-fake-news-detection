from retrieval.wiki_retriever import retrieve_wikipedia

# ==========================================
# TEST CLAIMS
# ==========================================

claims = [

    "Nagaland University completed Startup Sprint on 22 April",

    "India won the Cricket World Cup in 2011",

    "OpenAI launched ChatGPT",

    "Barack Obama was elected President of the United States"

]

for claim in claims:

    print("\n" + "=" * 80)
    print("CLAIM:", claim)

    results = retrieve_wikipedia(claim)

    print(f"\nRESULTS: {len(results)}")

    for idx, evidence in enumerate(results, start=1):

        print("\n--------------------------------")
        print("RANK:", idx)
        print("TITLE:", evidence.title)
        print("URL:", evidence.source_url)
        print("CONTENT:", evidence.content[:300])
