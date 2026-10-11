# search_engine.py
import json
import math
import heapq

from tokenizer import tokenize
from stemmer import stem_tokens
from index_loader import IndexLoader
from index_builder import BIGRAM_PREFIX, TRIGRAM_PREFIX, make_ngrams


FIELD_WEIGHTS = {
    "body": 1.0,
    "title": 3.0,
    "h1": 2.0,
    "h2": 1.5,
    "h3": 1.2,
    "bold": 2.0,
    "anchor": 1.8,
}


def load_scores(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return {int(k): float(v) for k, v in json.load(f).items()}
    except Exception:
        return {}


def compute_term_score(posting, idf):
    tf = sum(posting.get(field, 0) * weight for field, weight in FIELD_WEIGHTS.items())
    return tf * idf


def proximity_boost(postings_by_term, doc_id):
    positions_lists = []

    for postings in postings_by_term:
        positions = postings.get(doc_id, {}).get("positions", [])
        if positions:
            positions_lists.append(positions)

    if len(positions_lists) < 2:
        return 0.0

    min_span = float("inf")

    for i in range(len(positions_lists) - 1):
        a = positions_lists[i]
        b = positions_lists[i + 1]
        ia = ib = 0

        while ia < len(a) and ib < len(b):
            span = abs(a[ia] - b[ib])
            if span < min_span:
                min_span = span

            if a[ia] < b[ib]:
                ia += 1
            else:
                ib += 1

    if min_span == float("inf"):
        return 0.0

    return 2.0 / (1.0 + min_span)


def search(query, loader, total_docs, pagerank=None, debug=False, top_k=5):
    tokens = tokenize(query)
    stems = stem_tokens(tokens)

    if not stems:
        return []

    unigram_postings = []
    candidate_docs = set()

    for term in stems:
        postings = loader.get_postings(term)
        unigram_postings.append((term, postings))
        candidate_docs.update(postings.keys())

        if debug:
            print(f"[DEBUG] term '{term}' df={len(postings)}")

    if not candidate_docs:
        return []

    bigram_postings = []
    for gram in make_ngrams(stems, 2):
        bigram_postings.append(loader.get_postings(BIGRAM_PREFIX + gram))

    trigram_postings = []
    for gram in make_ngrams(stems, 3):
        trigram_postings.append(loader.get_postings(TRIGRAM_PREFIX + gram))

    scores = {}
    postings_only = [p for _, p in unigram_postings]
    max_pr = max(pagerank.values()) if pagerank else 1.0
    if max_pr == 0:
        max_pr = 1.0

    for doc in candidate_docs:
        score = 0.0
        matched_terms = 0

        for term, postings in unigram_postings:
            posting = postings.get(doc)
            if not posting:
                continue

            matched_terms += 1
            df = len(postings)
            idf = math.log((1 + total_docs) / (1 + df)) + 1.0
            score += compute_term_score(posting, idf)

        if matched_terms == 0:
            continue

        coverage = matched_terms / len(stems)
        score *= (0.5 + coverage)
        score += 4.0 * proximity_boost(postings_only, doc)

        bigram_hits = sum(1 for p in bigram_postings if doc in p)
        trigram_hits = sum(1 for p in trigram_postings if doc in p)
        score += 2.0 * bigram_hits + 3.5 * trigram_hits

        if pagerank:
            pr = pagerank.get(doc, 0.0) / max_pr
            score += 1.5 * pr

        scores[doc] = score

    top_results = heapq.nlargest(top_k, scores.items(), key=lambda x: x[1])
    return [doc for doc, _ in top_results]