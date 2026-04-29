# =====================================================
#  nlp/preprocessor.py
#  Tokenization, cleaning, and stopword removal
#  Uses regex-based tokenizer (no NLTK corpus download needed)
# =====================================================

import re

# Comprehensive English stopword list (embedded — no download required)
STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
    'you', "you're", "you've", "you'll", "you'd", 'your', 'yours',
    'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
    'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its',
    'itself', 'they', 'them', 'their', 'theirs', 'themselves',
    'what', 'which', 'who', 'whom', 'this', 'that', "that'll",
    'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
    'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
    'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
    'with', 'about', 'against', 'between', 'into', 'through',
    'during', 'before', 'after', 'above', 'below', 'to', 'from',
    'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
    'again', 'further', 'then', 'once', 'here', 'there', 'when',
    'where', 'why', 'how', 'all', 'both', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can',
    'will', 'just', 'don', "don't", 'should', "should've", 'now',
    'd', 'll', 'm', 'o', 're', 've', 'y', 'also', 'get', 'got',
    'let', 'like', 'make', 'know', 'think', 'want', 'need', 'go',
    'going', 'come', 'back', 'way', 'even', 'still', 'really',
    'much', 'many', 'well', 'one', 'two', 'would', 'could', 'might',
    'shall', 'may', 'must', 'okay', 'ok', 'yes', 'yeah', 'hi',
    'hello', 'hey', 'please', 'thank', 'thanks', 'sorry', 'oh',
}


def tokenize(text: str) -> list[str]:
    """
    Tokenize text into lowercase word tokens using regex.
    Handles contractions and hyphenated words gracefully.
    """
    if not text or not isinstance(text, str):
        return []
    # Lowercase and extract word tokens (letters + apostrophes)
    tokens = re.findall(r"\b[a-zA-Z']+\b", text.lower())
    # Filter out pure apostrophe artifacts and single chars
    return [t.strip("'") for t in tokens if len(t.strip("'")) > 1]


def remove_stopwords(tokens: list[str]) -> list[str]:
    """Remove common English stopwords from token list."""
    return [t for t in tokens if t not in STOPWORDS]


def extract_sentences(text: str) -> list[str]:
    """
    Split text into sentences using punctuation boundaries.
    Simple regex-based splitter — no NLTK punkt needed.
    """
    if not text:
        return []
    # Split on sentence-ending punctuation followed by whitespace
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def preprocess(text: str) -> dict:
    """
    Full preprocessing pipeline.
    Returns a dict with tokens, filtered tokens, sentences, and word count.
    """
    tokens    = tokenize(text)
    filtered  = remove_stopwords(tokens)
    sentences = extract_sentences(text)

    return {
        "original":       text,
        "tokens":         tokens,
        "filtered_tokens": filtered,
        "sentences":      sentences,
        "word_count":     len(tokens),
        "unique_words":   list(set(filtered)),
    }