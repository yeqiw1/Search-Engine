# stats.py
import os

def count_lines(filepath):
    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        for _ in f:
            count += 1
    return count

def get_file_size_kb(filepath):
    return os.path.getsize(filepath) / 1024

def get_dir_size_kb(dirpath):
    total = 0
    for fname in os.listdir(dirpath):
        path = os.path.join(dirpath, fname)
        if os.path.isfile(path):
            total += os.path.getsize(path)
    return total / 1024

def compute_stats(doc_count, partial_dir, final_index_file):
    unique_tokens = count_lines(final_index_file)
    partial_size = get_dir_size_kb(partial_dir)
    final_size = get_file_size_kb(final_index_file)

    return {
        "documents": doc_count,
        "unique_tokens": unique_tokens,
        "index_size_kb": partial_size + final_size
    }
