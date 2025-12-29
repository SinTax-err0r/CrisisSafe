from duckduckgo_search import DDGS
import json

def test_search(query):
    print(f"Testing query: {query}")
    with DDGS() as ddgs:
        # Current implementation
        results = list(ddgs.text(query, region="us-en", max_results=5, backend="lite"))
        for r in results:
            try:
                print(f"Title: {r.get('title').encode('utf-8', 'replace').decode('utf-8')}")
                print(f"URL: {r.get('href')}")
            except Exception:
                pass
            print("-" * 20)

if __name__ == "__main__":
    test_search("China economy news")
    test_search("Latest technology news")
