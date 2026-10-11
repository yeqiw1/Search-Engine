# index_merger.py
import heapq
import json
import os

def merge_partials(partial_dir, final_index_file, lexicon_file="../lexicon.json"):
    partial_files = [
        os.path.join(partial_dir, f)
        for f in os.listdir(partial_dir)
        if f.startswith("partial_")
    ]
    partial_files.sort()

    streams = [open(p, "r", encoding="utf-8") for p in partial_files]
    heap = []

    for i, s in enumerate(streams):
        line = s.readline()
        if line:
            term, postings_json = line.rstrip("\n").split("\t", 1)
            heapq.heappush(heap, (term, postings_json, i))

    lexicon = {}

    with open(final_index_file, "w", encoding="utf-8") as out:
        while heap:
            term, postings_json, file_idx = heapq.heappop(heap)
            merged = json.loads(postings_json)

            next_line = streams[file_idx].readline()
            if next_line:
                t, pj = next_line.rstrip("\n").split("\t", 1)
                heapq.heappush(heap, (t, pj, file_idx))

            while heap and heap[0][0] == term:
                _, same_json, same_idx = heapq.heappop(heap)
                merged.update(json.loads(same_json))

                next_line = streams[same_idx].readline()
                if next_line:
                    t, pj = next_line.rstrip("\n").split("\t", 1)
                    heapq.heappush(heap, (t, pj, same_idx))

            offset = out.tell()
            out.write(term + "\t" + json.dumps(merged, separators=(",", ":"), sort_keys=True) + "\n")
            lexicon[term] = offset

    for s in streams:
        s.close()

    with open(lexicon_file, "w", encoding="utf-8") as f:
        json.dump(lexicon, f)

    print("[INFO] Merge finished.")
    print("[INFO] Lexicon generated.")
