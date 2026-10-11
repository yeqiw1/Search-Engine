# main.py
import hashlib
import json
import os
from collections import Counter, defaultdict
from urllib.parse import urldefrag

from corpus_reader import iter_documents
from html_parser import extract_page_data
from tokenizer import tokenize
from stemmer import stem_tokens
from index_builder import build_index_for_doc
from partial_writer import write_partial_index
from index_merger import merge_partials
from stats import compute_stats

CORPUS_DIR = "../DEV"
PARTIAL_DIR = "../partial_indexes"
FINAL_INDEX = "../final_index.txt"
LEXICON_FILE = "../lexicon.json"
DOC_MAP_FILE = "../doc_map.json"
PAGERANK_FILE = "../pagerank.json"
BUILD_REPORT_FILE = "../build_report.json"

BATCH_SIZE = 1000
TEST_LIMIT = None
SIMHASH_THRESHOLD = 3


def stable_hash_64(text):
    return int(hashlib.md5(text.encode("utf-8", errors="ignore")).hexdigest()[:16], 16)


def simhash(tokens):
    counts = Counter(tokens)
    bits = [0] * 64
    for token, weight in counts.items():
        h = stable_hash_64(token)
        for i in range(64):
            if (h >> i) & 1:
                bits[i] += weight
            else:
                bits[i] -= weight
    fp = 0
    for i, value in enumerate(bits):
        if value >= 0:
            fp |= (1 << i)
    return fp


def hamming_distance(a, b):
    return (a ^ b).bit_count()


def is_near_duplicate(fp, buckets, fingerprints):
    candidate_ids = set()
    mask = (1 << 16) - 1
    for chunk in range(4):
        piece = (fp >> (chunk * 16)) & mask
        candidate_ids.update(buckets[(chunk, piece)])

    for candidate_id in candidate_ids:
        if hamming_distance(fp, fingerprints[candidate_id]) <= SIMHASH_THRESHOLD:
            return True
    return False


def add_simhash(fp, doc_id, buckets, fingerprints):
    fingerprints[doc_id] = fp
    mask = (1 << 16) - 1
    for chunk in range(4):
        piece = (fp >> (chunk * 16)) & mask
        buckets[(chunk, piece)].add(doc_id)


def compute_pagerank(graph, num_docs, damping=0.85, iterations=20):
    if num_docs == 0:
        return {}

    scores = {doc_id: 1.0 / num_docs for doc_id in range(1, num_docs + 1)}
    all_docs = set(scores.keys())

    for _ in range(iterations):
        new_scores = {doc_id: (1.0 - damping) / num_docs for doc_id in all_docs}
        sink_score = sum(scores[doc_id] for doc_id in all_docs if not graph.get(doc_id))
        sink_share = damping * sink_score / num_docs

        for doc_id in all_docs:
            new_scores[doc_id] += sink_share

        for src, outlinks in graph.items():
            if not outlinks:
                continue
            share = damping * scores[src] / len(outlinks)
            for dst in outlinks:
                new_scores[dst] += share

        scores = new_scores

    return scores


def main():
    print("Exists?", os.path.exists(CORPUS_DIR))

    doc_id = 0
    partial_id = 0
    index = {}
    doc_map = {}
    url_to_doc_id = {}
    raw_links_by_doc = {}

    exact_hashes = set()
    simhash_buckets = defaultdict(set)
    simhash_fingerprints = {}

    duplicate_stats = {"exact_duplicates": 0, "near_duplicates": 0, "indexed": 0}

    for url, content in iter_documents(CORPUS_DIR):
        page = extract_page_data(content, base_url=url)

        body_tokens = stem_tokens(tokenize(page["body"]))
        if not body_tokens:
            continue

        exact_sig = hashlib.md5(" ".join(body_tokens).encode("utf-8")).hexdigest()
        if exact_sig in exact_hashes:
            duplicate_stats["exact_duplicates"] += 1
            continue

        near_sig = simhash(body_tokens)
        if is_near_duplicate(near_sig, simhash_buckets, simhash_fingerprints):
            duplicate_stats["near_duplicates"] += 1
            continue

        doc_id += 1
        duplicate_stats["indexed"] = doc_id

        exact_hashes.add(exact_sig)
        add_simhash(near_sig, doc_id, simhash_buckets, simhash_fingerprints)

        doc_map[doc_id] = url
        url_to_doc_id[url] = doc_id
        raw_links_by_doc[doc_id] = [urldefrag(link)[0] for link in page["links"]]

        title_tokens = stem_tokens(tokenize(page["title"]))
        h1_tokens = stem_tokens(tokenize(page["h1"]))
        h2_tokens = stem_tokens(tokenize(page["h2"]))
        h3_tokens = stem_tokens(tokenize(page["h3"]))
        bold_tokens = stem_tokens(tokenize(page["bold"]))
        anchor_tokens = stem_tokens(tokenize(page["anchors"]))

        build_index_for_doc(
            doc_id,
            index,
            body_tokens,
            title_tokens,
            h1_tokens,
            h2_tokens,
            h3_tokens,
            bold_tokens,
            anchor_tokens,
        )

        if doc_id % BATCH_SIZE == 0:
            write_partial_index(index, PARTIAL_DIR, partial_id)
            partial_id += 1
            index.clear()

        if doc_id % 1000 == 0:
            print(f"Processed doc {doc_id}")

        if TEST_LIMIT and doc_id >= TEST_LIMIT:
            break

    if index:
        write_partial_index(index, PARTIAL_DIR, partial_id)

    print("[INFO] Partial indexing finished.")

    merge_partials(PARTIAL_DIR, FINAL_INDEX, LEXICON_FILE)

    with open(DOC_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(doc_map, f)

    graph = {}
    for src_doc, urls in raw_links_by_doc.items():
        targets = set()
        for target_url in urls:
            target_doc = url_to_doc_id.get(target_url)
            if target_doc and target_doc != src_doc:
                targets.add(target_doc)
        graph[src_doc] = sorted(targets)

    pagerank = compute_pagerank(graph, doc_id)
    with open(PAGERANK_FILE, "w", encoding="utf-8") as f:
        json.dump(pagerank, f)

    with open(BUILD_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump({"duplicates": duplicate_stats, "documents": doc_id}, f, indent=2)

    stats = compute_stats(doc_count=doc_id, partial_dir=PARTIAL_DIR, final_index_file=FINAL_INDEX)

    print("\n===== INDEX STATISTICS =====")
    print(f"Indexed Documents: {stats['documents']}")
    print(f"Unique Tokens: {stats['unique_tokens']}")
    print(f"Index Size on Disk (KB): {stats['index_size_kb']:.2f}")
    print(f"Exact duplicates skipped: {duplicate_stats['exact_duplicates']}")
    print(f"Near duplicates skipped: {duplicate_stats['near_duplicates']}")
    print("============================")
    print("\n[INFO] Milestone 3 indexing completed successfully.")


if __name__ == "__main__":
    main()
