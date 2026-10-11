# search_main.py
import time

from search_engine import search, load_scores
from doc_map_loader import load_doc_map
from index_loader import IndexLoader

INDEX_FILE = "../final_index.txt"
LEXICON_FILE = "../lexicon.json"
DOC_MAP_FILE = "../doc_map.json"
PAGERANK_FILE = "../pagerank.json"

doc_map = load_doc_map(DOC_MAP_FILE)
TOTAL_DOCS = len(doc_map)

loader = IndexLoader(INDEX_FILE, LEXICON_FILE)
pagerank = load_scores(PAGERANK_FILE)

while True:
    query = input("Enter query (or type exit): ").strip()
    if query.lower() == "exit":
        break

    start = time.perf_counter()

    results = search(
        query,
        loader,
        TOTAL_DOCS,
        pagerank=pagerank,
        debug=False,
        top_k=5,
    )

    elapsed_ms = (time.perf_counter() - start) * 1000

    print(f"\nQuery time: {elapsed_ms:.2f} ms")
    print("\nTop 5 results:\n")

    for doc_id in results:
        print(doc_map.get(str(doc_id), f"[Missing URL for doc {doc_id}]"))

    print("\n-----------------------\n")