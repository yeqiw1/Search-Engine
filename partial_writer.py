# partial_writer.py
import json
import os

def write_partial_index(index, output_dir, partial_id):
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"partial_{partial_id}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        for term in sorted(index.keys()):
            postings_json = json.dumps(index[term], separators=(",", ":"), sort_keys=True)
            f.write(term + "\t" + postings_json + "\n")

    print(f"[INFO] Wrote partial index: {file_path}")
