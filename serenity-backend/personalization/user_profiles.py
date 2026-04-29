# =====================================================
#  Serenity — User Personalization System
#  Tracks user profiles and generates personalized responses
# =====================================================

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib

class UserProfile:
    """
    Represents a user's persistent profile and conversation history.
    Stores contextual information for personalized response generation.
    """
    
    def __init__(self, user_id: str, name: str = "Friend"):
        self.user_id = user_id
        self.name = name
        self.created_at = datetime.now().isoformat()
        self.last_seen = datetime.now().isoformat()
        
        # Conversation context
        self.conversation_count = 0
        self.total_messages = 0
        self.conversation_themes: Dict[str, int] = {}  # themes mentioned
        self.mentioned_topics: List[str] = []
        
        # Emotional state tracking (without mood journal)
        self.recent_sentiments: List[float] = []  # compound scores
        self.crisis_history: List[Tuple[str, int]] = []  # (timestamp, severity)
        
        # Personal context (user volunteer information)
        self.personal_context = {
            "age_range": None,  # "18-25", "26-35", etc.
            "location": None,
            "occupation": None,
            "relationship_status": None,
            "languages": ["English"],
            "preferred_tone": "warm",  # warm, clinical, casual, spiritual
            "cultural_background": None,
        }
        
        # Coping strategies they've responded to
        self.effective_strategies: List[str] = []  # breathing, grounding, etc.
        self.mentioned_challenges: List[str] = []  # sleep, work stress, etc.
        
        # Conversation style preferences
        self.preferred_response_length = "medium"  # short, medium, long
        self.response_frequency = 0  # how often they check in
        
    def update_last_seen(self):
        self.last_seen = datetime.now().isoformat()
    
    def add_conversation(self):
        self.conversation_count += 1
        self.update_last_seen()
    
    def add_message(self):
        self.total_messages += 1
    
    def record_sentiment(self, compound_score: float):
        """Track sentiment to understand emotional trajectory."""
        self.recent_sentiments.append(compound_score)
        # Keep only last 20 sentiments
        if len(self.recent_sentiments) > 20:
            self.recent_sentiments.pop(0)
    
    def record_crisis(self, severity: int):
        """Log crisis event (0=none, 1=tier3, 2=tier2, 3=tier1)."""
        if severity > 0:
            self.crisis_history.append((datetime.now().isoformat(), severity))
    
    def get_sentiment_trend(self) -> str:
        """Determine if emotional state is improving or declining."""
        if len(self.recent_sentiments) < 2:
            return "unknown"
        
        recent = self.recent_sentiments[-5:]  # last 5
        avg_recent = sum(recent) / len(recent)
        
        older = self.recent_sentiments[-10:-5] if len(self.recent_sentiments) >= 10 else recent
        avg_older = sum(older) / len(older) if older else avg_recent
        
        if avg_recent > avg_older + 0.1:
            return "improving"
        elif avg_recent < avg_older - 0.1:
            return "declining"
        else:
            return "stable"
    
    def to_dict(self) -> dict:
        """Serialize profile to JSON-compatible dict."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "created_at": self.created_at,
            "last_seen": self.last_seen,
            "conversation_count": self.conversation_count,
            "total_messages": self.total_messages,
            "conversation_themes": self.conversation_themes,
            "mentioned_topics": self.mentioned_topics,
            "recent_sentiments": self.recent_sentiments,
            "crisis_history": self.crisis_history,
            "personal_context": self.personal_context,
            "effective_strategies": self.effective_strategies,
            "mentioned_challenges": self.mentioned_challenges,
            "preferred_response_length": self.preferred_response_length,
            "response_frequency": self.response_frequency,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        """Deserialize profile from dict."""
        profile = cls(data["user_id"], data.get("name", "Friend"))
        profile.created_at = data.get("created_at", profile.created_at)
        profile.last_seen = data.get("last_seen", profile.last_seen)
        profile.conversation_count = data.get("conversation_count", 0)
        profile.total_messages = data.get("total_messages", 0)
        profile.conversation_themes = data.get("conversation_themes", {})
        profile.mentioned_topics = data.get("mentioned_topics", [])
        profile.recent_sentiments = data.get("recent_sentiments", [])
        profile.crisis_history = data.get("crisis_history", [])
        profile.personal_context = data.get("personal_context", profile.personal_context)
        profile.effective_strategies = data.get("effective_strategies", [])
        profile.mentioned_challenges = data.get("mentioned_challenges", [])
        profile.preferred_response_length = data.get("preferred_response_length", "medium")
        profile.response_frequency = data.get("response_frequency", 0)
        return profile


class PersonalizationEngine:
    """
    Generates personalized system prompts and context for each user.
    Creates unique conversation styles based on user profile.
    """
    
    def __init__(self):
        self.users: Dict[str, UserProfile] = {}
    
    def get_or_create_user(self, user_id: str, name: str = "Friend") -> UserProfile:
        """Get existing user profile or create new one."""
        if user_id not in self.users:
            self.users[user_id] = UserProfile(user_id, name)
        return self.users[user_id]
    
    def generate_personalized_system_prompt(self, user_id: str) -> str:
        """
        Generate a unique system prompt tailored to the user.
        This becomes the foundation for all responses.
        """
        profile = self.get_or_create_user(user_id)
        
        base_prompt = """You are Serenity, a compassionate and empathetic AI mental wellness companion."""
        
        # Personalization layer 1: User's name and context
        if profile.name and profile.name != "Friend":
            base_prompt += f"\n\nYou know {profile.name} and have spoken with them {profile.conversation_count} times before."
        
        # Personalization layer 2: Emotional trajectory
        trend = profile.get_sentiment_trend()
        if trend == "improving":
            base_prompt += "\n\n{}'s emotional state has been improving recently. Acknowledge their progress gently and build on positive momentum.".format(profile.name)
        elif trend == "declining":
            base_prompt += "\n\n{}'s recent conversations suggest they may be struggling more. Be extra gentle, validating, and encourage professional support if needed.".format(profile.name)
        
        # Personalization layer 3: Recurring themes
        if profile.conversation_themes:
            top_themes = sorted(profile.conversation_themes.items(), key=lambda x: x[1], reverse=True)[:3]
            themes_str = ", ".join([t[0] for t in top_themes])
            base_prompt += f"\n\nCommon themes in {profile.name}'s conversations: {themes_str}. Remember these context clues when relevant."
        
        # Personalization layer 4: Effective coping strategies
        if profile.effective_strategies:
            strategies_str = ", ".join(profile.effective_strategies[:3])
            base_prompt += f"\n\n{profile.name} has found these helpful before: {strategies_str}. Feel free to reference them if appropriate."
        
        # Personalization layer 5: Communication preferences
        tone_guidance = {
            "warm": "Use a warm, gentle, nurturing tone with plenty of validation.",
            "clinical": "Use clear, practical language with evidence-based guidance.",
            "casual": "Keep a friendly, conversational tone—be like a supportive friend.",
            "spiritual": "Honor spiritual/philosophical perspectives; reference meaning and resilience.",
        }
        preferred_tone = profile.personal_context.get("preferred_tone", "warm")
        base_prompt += f"\n\n{tone_guidance.get(preferred_tone, tone_guidance['warm'])}"
        
        # Personalization layer 6: Response length preference
        if profile.preferred_response_length == "short":
            base_prompt += "\n\nKeep responses concise (2-3 sentences). Respect their preference for brevity."
        elif profile.preferred_response_length == "long":
            base_prompt += "\n\nFeel free to write longer, more detailed responses (4-5 paragraphs). They appreciate depth."
        else:
            base_prompt += "\n\nAim for medium-length responses (2-4 paragraphs) that are both substantive and digestible."
        
        # Core responsibilities (always included)
        base_prompt += """

Your core responsibilities:
1. Listen deeply and validate their feelings without judgment
2. Ask thoughtful, open-ended questions tailored to their context
3. Offer evidence-based coping strategies
4. Recognize crisis signals and provide emergency resources
5. Create a safe, non-judgmental space for honest conversation

Remember: You are not a replacement for professional mental health care. If they mention suicidal ideation, always include the 988 Lifeline.

Tone: Warm, gentle, unhurried, conversational, and deeply empathetic to THEIR specific situation.
"""
        return base_prompt
    
    def extract_user_context(self, user_id: str, user_message: str, 
                            sentiment: float, detected_topics: List[str]) -> Dict:
        """
        Extract and update user profile based on their message.
        Learn about them over time.
        """
        profile = self.get_or_create_user(user_id)
        profile.add_message()
        profile.record_sentiment(sentiment)
        
        # Track mentioned topics
        for topic in detected_topics:
            if topic not in profile.mentioned_topics:
                profile.mentioned_topics.append(topic)
            profile.conversation_themes[topic] = profile.conversation_themes.get(topic, 0) + 1
        
        # Extract possible personal context from message
        context_clues = self._extract_context_clues(user_message)
        for key, value in context_clues.items():
            if value and profile.personal_context.get(key) is None:
                profile.personal_context[key] = value
        
        return {
            "user_name": profile.name,
            "conversation_number": profile.conversation_count,
            "message_count": profile.total_messages,
            "recent_trend": profile.get_sentiment_trend(),
            "top_themes": list(sorted(profile.conversation_themes.items(), 
                                     key=lambda x: x[1], reverse=True)[:3]),
            "personal_context": profile.personal_context,
        }
    
    def _extract_context_clues(self, message: str) -> Dict[str, Optional[str]]:
        """
        Simple heuristic extraction of personal context from user message.
        Could be enhanced with NLP.
        """
        clues = {
            "occupation": None,
            "relationship_status": None,
            "location": None,
        }
        
        message_lower = message.lower()
        
        # Occupation hints
        if any(word in message_lower for word in ["work", "job", "office", "boss", "colleague"]):
            if "teacher" in message_lower:
                clues["occupation"] = "education"
            elif "doctor" in message_lower or "hospital" in message_lower:
                clues["occupation"] = "healthcare"
            elif "engineer" in message_lower or "coding" in message_lower:
                clues["occupation"] = "tech"
            else:
                clues["occupation"] = "employed"
        
        # Relationship hints
        if "partner" in message_lower or "spouse" in message_lower:
            clues["relationship_status"] = "partnered"
        elif "boyfriend" in message_lower or "girlfriend" in message_lower:
            clues["relationship_status"] = "dating"
        elif "single" in message_lower:
            clues["relationship_status"] = "single"
        
        return clues
    
    def get_personalization_metadata(self, user_id: str) -> Dict:
        """Return metadata about user for debugging/analytics."""
        profile = self.get_or_create_user(user_id)
        return {
            "user_id": user_id,
            "name": profile.name,
            "conversations": profile.conversation_count,
            "total_messages": profile.total_messages,
            "sentiment_trend": profile.get_sentiment_trend(),
            "days_active": self._days_since(profile.created_at),
            "last_seen": profile.last_seen,
            "crisis_incidents": len(profile.crisis_history),
        }
    
    @staticmethod
    def _days_since(iso_timestamp: str) -> int:
        """Calculate days since timestamp."""
        try:
            created = datetime.fromisoformat(iso_timestamp)
            delta = datetime.now() - created
            return delta.days
        except:
            return 0


# =====================================================
#  Usage Example
# =====================================================

if __name__ == "__main__":
    engine = PersonalizationEngine()
    
    # Create two different users
    user1 = engine.get_or_create_user("user_001", "Alex")
    user2 = engine.get_or_create_user("user_002", "Jordan")
    
    # Simulate user1's conversations
    user1.add_conversation()
    user1.record_sentiment(0.3)  # slightly positive
    engine.extract_user_context("user_001", "I've been anxious about work lately", 0.3, ["anxiety", "work"])
    
    user1.add_conversation()
    user1.record_sentiment(0.5)  # more positive
    engine.extract_user_context("user_001", "The breathing exercises you taught me really help", 0.5, ["anxiety", "coping"])
    user1.effective_strategies.append("breathing exercises")
    
    # Simulate user2's conversations
    user2.add_conversation()
    user2.record_sentiment(-0.6)  # very negative
    engine.extract_user_context("user_002", "I feel hopeless, nothing matters", -0.6, ["depression", "hopelessness"])
    
    # Generate personalized prompts
    prompt1 = engine.generate_personalized_system_prompt("user_001")
    prompt2 = engine.generate_personalized_system_prompt("user_002")
    
    print("=" * 70)
    print("PERSONALIZED SYSTEM PROMPT FOR ALEX")
    print("=" * 70)
    print(prompt1)
    print("\n" + "=" * 70)
    print("PERSONALIZED SYSTEM PROMPT FOR JORDAN")
    print("=" * 70)
    print(prompt2)
    print("\n" + "=" * 70)
    print("USER METADATA")
    print("=" * 70)
    print(json.dumps(engine.get_personalization_metadata("user_001"), indent=2))
    print(json.dumps(engine.get_personalization_metadata("user_002"), indent=2))