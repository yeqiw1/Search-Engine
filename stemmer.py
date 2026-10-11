# stemmer.py
from nltk.stem import PorterStemmer

ps = PorterStemmer()

def stem_tokens(tokens):
    """
    Apply Porter stemming to a list of tokens.
    """
    return [ps.stem(token) for token in tokens]
