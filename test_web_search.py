
from retrieval.web_search import search_web


print("\n====================")
print("TESTING WEB SEARCH")
print("====================\n")


results = search_web(

    query="mount saramati is the highest mountain in nagaland",

    engine="duckduckgo"
)


print("\nRESULTS:\n")

for item in results:

    print(item)

    print("\n------------------\n")


print("TOTAL:", len(results))
