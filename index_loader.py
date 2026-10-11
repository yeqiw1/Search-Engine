# index_loader.py
import json

class IndexLoader:
    def __init__(self, index_file, lexicon_file):
        self.index_file = index_file
        with open(lexicon_file, "r", encoding="utf-8") as f:
            self.lexicon = json.load(f)
        self.f = open(index_file, "r", encoding="utf-8")

    def get_postings(self, term):
        if term not in self.lexicon:
            return {}

        self.f.seek(self.lexicon[term])
        line = self.f.readline()
        _, postings_json = line.rstrip("\n").split("\t", 1)
        raw = json.loads(postings_json)
        return {int(doc_id): posting for doc_id, posting in raw.items()}
