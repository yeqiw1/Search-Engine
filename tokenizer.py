# tokenizer.py
import re

TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]+")

def tokenize(text):
    """
    Split text into alphanumeric lowercase tokens.
    """
    tokens = TOKEN_PATTERN.findall(text.lower())
    return tokens
