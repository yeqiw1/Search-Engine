# doc_map_loader.py
import json

def load_doc_map(path):
    with open(path, "r") as f:
        return json.load(f)