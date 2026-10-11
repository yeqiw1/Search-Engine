# index_builder.py
from collections import Counter, defaultdict

BIGRAM_PREFIX = "__bi__:"
TRIGRAM_PREFIX = "__tri__:"

def make_ngrams(tokens, n):
    if len(tokens) < n:
        return []
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def _positions(tokens):
    result = defaultdict(list)
    for i, term in enumerate(tokens):
        result[term].append(i)
    return result


def _add_posting(index, term, doc_id, posting):
    if term not in index:
        index[term] = {}
    index[term][str(doc_id)] = posting


def build_index_for_doc(
    doc_id,
    index,
    body_tokens,
    title_tokens,
    h1_tokens,
    h2_tokens,
    h3_tokens,
    bold_tokens,
    anchor_tokens,
):
    """
    Posting structure per term/doc:
    {
      body, title, h1, h2, h3, bold, anchor,
      positions: [body term positions]
    }

    Also indexes bigrams and trigrams using prefixed synthetic terms.
    """
    body_tf = Counter(body_tokens)
    title_tf = Counter(title_tokens)
    h1_tf = Counter(h1_tokens)
    h2_tf = Counter(h2_tokens)
    h3_tf = Counter(h3_tokens)
    bold_tf = Counter(bold_tokens)
    anchor_tf = Counter(anchor_tokens)
    body_positions = _positions(body_tokens)

    all_terms = set(
        body_tf.keys()
        | title_tf.keys()
        | h1_tf.keys()
        | h2_tf.keys()
        | h3_tf.keys()
        | bold_tf.keys()
        | anchor_tf.keys()
    )

    for term in all_terms:
        posting = {
            "body": body_tf.get(term, 0),
            "title": title_tf.get(term, 0),
            "h1": h1_tf.get(term, 0),
            "h2": h2_tf.get(term, 0),
            "h3": h3_tf.get(term, 0),
            "bold": bold_tf.get(term, 0),
            "anchor": anchor_tf.get(term, 0),
            "positions": body_positions.get(term, []),
        }
        _add_posting(index, term, doc_id, posting)

    for gram in make_ngrams(body_tokens, 2):
        _add_posting(
            index,
            BIGRAM_PREFIX + gram,
            doc_id,
            {"body": 1, "title": 0, "h1": 0, "h2": 0, "h3": 0, "bold": 0, "anchor": 0, "positions": []},
        )

    for gram in make_ngrams(body_tokens, 3):
        _add_posting(
            index,
            TRIGRAM_PREFIX + gram,
            doc_id,
            {"body": 1, "title": 0, "h1": 0, "h2": 0, "h3": 0, "bold": 0, "anchor": 0, "positions": []},
        )
