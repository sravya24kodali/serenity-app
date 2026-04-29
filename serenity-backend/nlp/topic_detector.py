# =====================================================
#  nlp/topic_detector.py — Mental Health Topic Detection
#  Detects mental health topics from user messages
# =====================================================


def detect_topics(text: str) -> list:
    """
    Detect mental health topics mentioned in user message.
    
    Args:
        text (str): User message
    
    Returns:
        list: List of detected topics, e.g., ["anxiety", "sleep"]
    
    Example:
        >>> detect_topics("I've been so anxious and can't sleep at night")
        ["anxiety", "sleep"]
    """
    text_lower = text.lower()
    detected = []
    
    # Topic keywords mapping
    topics_keywords = {
        "anxiety": [
            "anxious", "anxiety", "nervous", "panic", "panicking",
            "worried", "worry", "fear", "scared", "terrified",
            "stress", "stressed", "tense", "tension"
        ],
        "depression": [
            "depressed", "depression", "sad", "sadness", "hopeless",
            "hopelessness", "worthless", "empty", "numb", "empty feeling",
            "meaningless", "no point", "why bother", "nothing matters"
        ],
        "sleep": [
            "sleep", "sleeping", "insomnia", "can't sleep", "trouble sleeping",
            "tired", "exhausted", "fatigue", "sleepless", "awake",
            "nighttime", "night", "restless", "toss and turn"
        ],
        "work": [
            "work", "job", "boss", "office", "career", "project",
            "deadline", "coworker", "colleague", "workplace",
            "employment", "professional", "workplace"
        ],
        "relationships": [
            "relationship", "partner", "boyfriend", "girlfriend", "spouse",
            "husband", "wife", "dating", "family", "mother", "father",
            "sibling", "friend", "breakup", "divorce", "argument",
            "conflict", "fighting", "marriage"
        ],
        "self_harm": [
            "self harm", "cutting", "cut myself", "hurt myself", "harm myself",
            "self injury", "self-injury", "scratching", "wound", "scar"
        ],
        "grief": [
            "grief", "grieving", "loss", "died", "death", "lost someone",
            "passed away", "funeral", "mourning", "bereaved", "died",
            "loss of", "miss you", "missing"
        ],
        "anger": [
            "angry", "anger", "rage", "furious", "enraged", "irritated",
            "irritable", "annoyed", "frustrated", "frustrated", "mad",
            "hate", "hateful"
        ],
        "loneliness": [
            "lonely", "loneliness", "alone", "isolated", "isolation",
            "nobody", "no one", "excluded", "left out", "unwanted",
            "disconnected", "separated"
        ],
        "coping": [
            "breathing", "breathing exercise", "meditation", "mindfulness",
            "grounding", "exercise", "gym", "yoga", "walking",
            "journaling", "therapy", "counseling", "help"
        ],
        "suicidal": [
            "suicide", "suicidal", "end it", "take my life", "kill myself",
            "life isn't worth", "should be dead", "better off dead",
            "want to die", "planning to"
        ]
    }
    
    # Detect topics
    for topic, keywords in topics_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                if topic not in detected:
                    detected.append(topic)
                break  # Found this topic, move to next
    
    # If no topics detected, return generic
    if not detected:
        detected = ["general"]
    
    return detected


def get_topic_category(topics: list) -> str:
    """
    Get primary topic category from list of detected topics.
    Useful for prioritizing which topic to focus on.
    
    Args:
        topics (list): List of detected topics
    
    Returns:
        str: Primary topic or "general"
    """
    if not topics:
        return "general"
    
    # Priority order (high severity first)
    priority = [
        "suicidal", "self_harm", "grief", "depression",
        "anxiety", "anger", "loneliness", "sleep",
        "relationships", "work", "coping", "general"
    ]
    
    for p in priority:
        if p in topics:
            return p
    
    return topics[0] if topics else "general"