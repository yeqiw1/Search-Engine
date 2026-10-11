# corpus_reader.py
import os
import json
from urllib.parse import urldefrag, urlparse

def iter_documents(corpus_dir):
    """
    Generator that yields (url, content) from all JSON files
    under corpus_dir.

    URL fragments are removed to satisfy the project requirement
    to ignore the fragment part of a page URL.
    """
    for root, dirs, files in os.walk(corpus_dir):
        for filename in files:
            if filename.endswith(".json"):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        raw_url = data.get("url", "")
                        url, _ = urldefrag(raw_url)

                        path = urlparse(url).path.lower()
                        if path.endswith(".txt"):
                            continue

                        content = data.get("content", "")
                        yield url, content
                except Exception as e:
                    print(f"[ERROR] Failed reading {filepath}: {e}")
