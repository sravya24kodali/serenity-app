# =====================================================
#  utils/crisis_check.py — Crisis Detection Module
#  3-tier crisis severity detection
# =====================================================


def detect_crisis(text: str) -> int:
    """
    Detect crisis signals in user message.
    3-tier severity system.
    
    Args:
        text (str): User message to analyze
    
    Returns:
        int: Crisis level
            - 0: No crisis indicators
            - 1: Tier 3 (Concerning) - warning signs
            - 2: Tier 2 (Serious) - significant risk
            - 3: Tier 1 (Immediate) - highest risk
    
    Example:
        >>> detect_crisis("I want to kill myself")
        3
        >>> detect_crisis("I feel hopeless")
        2
        >>> detect_crisis("I'm having a rough day")
        0
    """
    text_lower = text.lower()
    
    # ─────────────────────────────────────────────────────────────
    # TIER 1: IMMEDIATE RISK (Highest Priority)
    # ─────────────────────────────────────────────────────────────
    tier1_keywords = [
        # Suicidal ideation (direct)
        "suicide", "suicidal", "kill myself", "kill myself",
        "i want to die", "i'm going to die", "end it",
        
        # Methods
        "overdose", "take pills", "hang myself", "hang myself",
        "jump off", "shoot myself", "slit my wrist",
        "knife myself", "cut my wrist", "drown myself",
        
        # Intent statements
        "plan to kill", "planning to kill", "going to kill myself",
        "tonight i", "tomorrow i", "method",
        
        # Finality statements
        "this is my last", "final message", "goodbye",
        "i'm leaving", "i won't be here", "see you never",
        "should be dead", "deserve to die", "better off dead"
    ]
    
    # ─────────────────────────────────────────────────────────────
    # TIER 2: SERIOUS RISK (Significant Concern)
    # ─────────────────────────────────────────────────────────────
    tier2_keywords = [
        # Hopelessness
        "hopeless", "hopelessness", "no hope", "without hope",
        "can't go on", "can't keep going", "can't do this",
        "want to die", "wish i was dead", "wish i was dead",
        
        # Meaninglessness
        "no point", "pointless", "what's the point",
        "nothing matters", "why bother", "no reason",
        "doesn't matter", "meaningless", "empty",
        
        # Self-worth
        "worthless", "worthless", "not worth", "burden",
        "burden on everyone", "better off without me",
        "world would be better", "mistake", "failure"
    ]
    
    # ─────────────────────────────────────────────────────────────
    # TIER 3: CONCERNING (Warning Signs)
    # ─────────────────────────────────────────────────────────────
    tier3_keywords = [
        # Self-harm urges
        "hurt myself", "harm myself", "cut", "scratch",
        "wound", "scar", "pain myself",
        
        # Dark thoughts
        "dark thoughts", "dark place", "darkness", "shadow",
        "nightmare", "hell", "trapped",
        
        # Emotional pain
        "can't take it", "too much", "unbearable", "pain",
        "agony", "suffering", "torture", "anguish",
        
        # Risk behaviors
        "reckless", "dangerous", "don't care", "not safe",
        "driving fast", "taking risks", "careless",
        
        # Isolation urges
        "go away", "disappear", "run away", "escape",
        "nobody cares", "no one loves", "alone", "isolated"
    ]
    
    # ─────────────────────────────────────────────────────────────
    # CHECK TIERS (Highest severity first)
    # ─────────────────────────────────────────────────────────────
    
    # Check Tier 1 (Immediate Risk)
    for keyword in tier1_keywords:
        if keyword in text_lower:
            return 3
    
    # Check Tier 2 (Serious Risk)
    for keyword in tier2_keywords:
        if keyword in text_lower:
            return 2
    
    # Check Tier 3 (Concerning)
    for keyword in tier3_keywords:
        if keyword in text_lower:
            return 1
    
    # No crisis indicators
    return 0


def get_crisis_severity_name(level: int) -> str:
    """
    Get human-readable crisis severity name.
    
    Args:
        level (int): Crisis level (0-3)
    
    Returns:
        str: Severity name
    """
    severity_map = {
        0: "No Crisis",
        1: "Concerning",
        2: "Serious",
        3: "Immediate"
    }
    return severity_map.get(level, "Unknown")


def get_crisis_resources() -> dict:
    """
    Get crisis resources and hotline information.
    
    Returns:
        dict: Crisis resources with numbers and websites
    """
    return {
        "988_lifeline": {
            "name": "988 Suicide & Crisis Lifeline",
            "phone": "988",
            "sms": "Text 988",
            "url": "https://988lifeline.org",
            "available": "24/7",
            "description": "Free, confidential support for anyone in suicidal crisis"
        },
        "crisis_text_line": {
            "name": "Crisis Text Line",
            "sms": "Text HOME to 741741",
            "url": "https://www.crisistextline.org",
            "available": "24/7",
            "description": "Text-based crisis support"
        },
        "samhsa_helpline": {
            "name": "SAMHSA National Helpline",
            "phone": "1-800-662-4357",
            "available": "24/7",
            "url": "https://www.samhsa.gov",
            "description": "Mental health & substance abuse support"
        },
        "nami_helpline": {
            "name": "NAMI Helpline",
            "phone": "1-800-950-NAMI",
            "url": "https://www.nami.org",
            "available": "Mon-Fri 10am-10pm ET",
            "description": "National Alliance on Mental Illness support"
        },
        "emergency": {
            "name": "Emergency Services",
            "phone": "911",
            "description": "Call 911 for immediate life-threatening emergency"
        }
    }