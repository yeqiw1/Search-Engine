# web_ui.py
from time import perf_counter
from urllib.parse import urlparse

from flask import Flask, render_template_string, request

from search_engine import search, load_scores
from doc_map_loader import load_doc_map
from index_loader import IndexLoader

INDEX_FILE = "../final_index.txt"
LEXICON_FILE = "../lexicon.json"
DOC_MAP_FILE = "../doc_map.json"
PAGERANK_FILE = "../pagerank.json"
TOP_K = 5

app = Flask(__name__)

doc_map = load_doc_map(DOC_MAP_FILE)
TOTAL_DOCS = len(doc_map)
loader = IndexLoader(INDEX_FILE, LEXICON_FILE)
pagerank = load_scores(PAGERANK_FILE)

TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>CS 121 Search Engine</title>
</head>
<body>
    <h2>CS 121 Search Engine</h2>

    <form method="get" action="/">
        <input type="text" name="q" value="{{ query }}" size="40">
        <button type="submit">Search</button>
    </form>

    {% if searched %}
        <p>Query time: {{ elapsed_ms }} ms</p>

        {% if results %}
            <ol>
            {% for r in results %}
                <li><a href="{{ r.url }}" target="_blank">{{ r.url }}</a></li>
            {% endfor %}
            </ol>
        {% else %}
            <p>No results found.</p>
        {% endif %}
    {% endif %}
</body>
</html>
"""


@app.route("/", methods=["GET"])
def index():
    query = request.args.get("q", "").strip()
    results = []
    elapsed_ms = None
    searched = bool(query)

    if query:
        start = perf_counter()
        doc_ids = search(
            query=query,
            loader=loader,
            total_docs=TOTAL_DOCS,
            pagerank=pagerank,
            debug=False,
            top_k=TOP_K,
        )
        elapsed_ms = f"{(perf_counter() - start) * 1000:.2f}"

        for doc_id in doc_ids:
            url = doc_map.get(str(doc_id), f"[Missing URL for doc {doc_id}]")
            results.append({"url": url})

    return render_template_string(
        TEMPLATE,
        query=query,
        results=results,
        elapsed_ms=elapsed_ms,
        searched=searched,
    )


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
