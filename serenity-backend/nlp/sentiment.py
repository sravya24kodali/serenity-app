# =====================================================
#  nlp/sentiment.py — Sentiment Analysis Module
#  Uses VADER for sentiment analysis
# =====================================================

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize VADER analyzer
_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment of user message using VADER.
    
    Args:
        text (str): User message to analyze
    
    Returns:
        dict: {
            "compound": float,   # -1.0 to 1.0
            "positive": float,   # 0.0 to 1.0
            "negative": float,   # 0.0 to 1.0
            "neutral": float     # 0.0 to 1.0
        }
    
    Example:
        >>> analyze_sentiment("I feel great today!")
        {'compound': 0.65, 'positive': 0.65, 'negative': 0.0, 'neutral': 0.35}
    """
    try:
        if not text or not isinstance(text, str):
            return {
                "compound": 0.0,
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 1.0
            }
        
        # Get VADER sentiment scores
        scores = _analyzer.polarity_scores(text)
        
        return {
            "compound": scores["compound"],
            "positive": scores["pos"],
            "negative": scores["neg"],
            "neutral": scores["neu"]
        }
    
    except Exception as e:
        print(f"Error in analyze_sentiment: {str(e)}")
        return {
            "compound": 0.0,
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 1.0
        }


def classify_sentiment(compound_score: float) -> str:
    """
    Classify sentiment based on compound score.
    
    Args:
        compound_score (float): Compound sentiment score
    
    Returns:
        str: Sentiment category
    """
    if compound_score >= 0.05:
        return "positive"
    elif compound_score <= -0.05:
        return "negative"
    else:
        return "neutral"