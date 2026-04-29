# =====================================================
#  routes/chat.py — Groq API + Real Conversation DB
# =====================================================

from flask import Blueprint, request, jsonify
import os
from groq import Groq

from nlp.sentiment import analyze_sentiment
from nlp.topic_detector import detect_topics
from utils.crisis_check import detect_crisis
from personalization.user_profiles import PersonalizationEngine
from database.conversations import (
    save_conversation,
    update_conversation,
    get_recent_conversations,
    get_conversation,
    delete_conversation,
)

# ── Initialize ──────────────────────────────────────
PERSONALIZATION_ENGINE = PersonalizationEngine()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

chat_bp = Blueprint('chat', __name__)


# ── POST /api/chat ───────────────────────────────────
@chat_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()

        if not data or "message" not in data or "user_id" not in data:
            return jsonify({"error": "Missing required fields: user_id, message"}), 400

        user_id      = data.get("user_id")
        user_name    = data.get("user_name", "Friend")
        user_message = data.get("message", "").strip()
        history      = data.get("history", [])
        conv_id      = data.get("conv_id")   # existing conversation id (optional)

        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        # ── NLP Analysis ────────────────────────────
        sentiment    = analyze_sentiment(user_message)
        topics       = detect_topics(user_message)
        crisis_level = detect_crisis(user_message)

        # ── Personalization ─────────────────────────
        user_profile = PERSONALIZATION_ENGINE.get_or_create_user(user_id, user_name)
        user_profile.add_conversation()
        user_profile.record_sentiment(sentiment["compound"])
        user_profile.record_crisis(crisis_level)

        context = PERSONALIZATION_ENGINE.extract_user_context(
            user_id, user_message, sentiment["compound"], topics
        )

        system_prompt  = PERSONALIZATION_ENGINE.generate_personalized_system_prompt(user_id)
        system_prompt += f"\n\nIMPORTANT: Keep all responses SHORT — maximum 7-9 sentences. Always address the user as '{user_name}' naturally. Be warm, empathetic BUT also gently playful and occasionally humorous. Use relevant emojis naturally throughout your response (1-3 emojis per message) to make it feel warm and friendly. Ask only ONE question at a time. Never write long paragraphs."
        # ── Build messages ──────────────────────────
        messages = list(history) if history else []
        messages.append({"role": "user", "content": user_message})

        # ── Call Groq ───────────────────────────────
        ai_response = None
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=300,
                temperature=0.8,
                messages=[{"role": "system", "content": system_prompt}] + messages
            )
            ai_response = response.choices[0].message.content
        except Exception as e:
            print(f"[Groq Error] {str(e)}")
            ai_response = get_fallback_response(user_name, topics)

        # ── Save to Database ─────────────────────────
        # Add assistant response to messages
        messages.append({"role": "assistant", "content": ai_response})

        # Use first user message as conversation title
        title = user_message[:50]

        if conv_id:
            # Update existing conversation
            update_conversation(user_id, conv_id, messages, title)
        else:
            # Create new conversation
            conv_id = save_conversation(user_id, title, messages)

        # ── Response ────────────────────────────────
        return jsonify({
            "response":        ai_response,
            "user_id":         user_id,
            "conv_id":         conv_id,
            "sentiment":       sentiment,
            "crisis_level":    crisis_level,
            "topics":          topics,
            "personalization": {
                "user_name":           user_name,
                "conversation_number": user_profile.conversation_count,
                "sentiment_trend":     context["recent_trend"],
                "personalized":        True,
                "provider":            "groq"
            }
        }), 200

    except Exception as e:
        print(f"[Chat Error] {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


# ── GET /api/conversations/<user_id> ─────────────────
@chat_bp.route('/conversations/<user_id>', methods=['GET'])
def get_conversations(user_id):
    """Get recent conversations for sidebar."""
    try:
        convs = get_recent_conversations(user_id, limit=10)
        return jsonify({"conversations": convs}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/conversation/<user_id>/<conv_id> ────────
@chat_bp.route('/conversation/<user_id>/<conv_id>', methods=['GET'])
def load_conversation(user_id, conv_id):
    """Load a specific conversation's messages."""
    try:
        conv = get_conversation(user_id, conv_id)
        if not conv:
            return jsonify({"error": "Conversation not found"}), 404
        return jsonify(conv), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── DELETE /api/conversation/<user_id>/<conv_id> ─────
@chat_bp.route('/conversation/<user_id>/<conv_id>', methods=['DELETE'])
def remove_conversation(user_id, conv_id):
    """Delete a conversation."""
    try:
        success = delete_conversation(user_id, conv_id)
        if not success:
            return jsonify({"error": "Conversation not found"}), 404
        return jsonify({"message": "Deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/user-profile/<user_id> ──────────────────
@chat_bp.route('/user-profile/<user_id>', methods=['GET'])
def get_user_profile(user_id):
    try:
        profile  = PERSONALIZATION_ENGINE.get_or_create_user(user_id)
        metadata = PERSONALIZATION_ENGINE.get_personalization_metadata(user_id)
        return jsonify({
            "user_id":                user_id,
            "name":                   profile.name,
            "metadata":               metadata,
            "top_themes":             dict(sorted(profile.conversation_themes.items(), key=lambda x: x[1], reverse=True)[:5]),
            "effective_strategies":   profile.effective_strategies,
            "personal_context":       profile.personal_context,
            "recent_sentiment_trend": profile.get_sentiment_trend(),
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── POST /api/user-preferences/<user_id> ─────────────
@chat_bp.route('/user-preferences/<user_id>', methods=['POST'])
def update_user_preferences(user_id):
    try:
        data    = request.get_json()
        profile = PERSONALIZATION_ENGINE.get_or_create_user(user_id)

        if "name" in data and data["name"]:
            profile.name = data["name"]
        if "preferred_tone" in data:
            profile.personal_context["preferred_tone"] = data["preferred_tone"]
        if "preferred_response_length" in data:
            profile.preferred_response_length = data["preferred_response_length"]

        return jsonify({
            "message":     "Preferences updated successfully",
            "user_id":     user_id,
            "preferences": profile.personal_context
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── GET /api/resources ────────────────────────────────
@chat_bp.route('/resources', methods=['GET'])
def get_resources():
    return jsonify({
        "resources": [
            {"name": "988 Suicide & Crisis Lifeline", "contact": "Call or text 988",   "url": "https://988lifeline.org"},
            {"name": "Crisis Text Line",              "contact": "Text HOME to 741741","url": "https://www.crisistextline.org"},
            {"name": "SAMHSA Helpline",               "contact": "1-800-662-4357",     "url": "https://www.samhsa.gov"},
            {"name": "NAMI Helpline",                 "contact": "1-800-950-NAMI",     "url": "https://www.nami.org"},
        ]
    }), 200


# ── Fallback responses ────────────────────────────────
def get_fallback_response(user_name: str, topics: list) -> str:
    import random
    t = " ".join(topics).lower()

    if "anxiety" in t:
        opts = [
            f"Anxiety really picked the wrong person to mess with today, {user_name} 😄 You've got this — what's been going on?",
            f"Ah {user_name}, anxiety is basically your brain trying to win a worry Olympics 🏅 Let's talk about what's triggering it.",
        ]
    elif "depression" in t or "sadness" in t:
        opts = [
            f"{user_name}, even on the cloudiest days, you reached out — and that takes guts 💙 What's been going on?",
            f"Sadness is visiting you today, {user_name} — but it doesn't get to stay forever 🌿 What's weighing on you?",
        ]
    elif "sleep" in t:
        opts = [
            f"{user_name}, your bed is out here plotting against you and that's not okay 😂🌙 How long has sleep been difficult?",
            f"Sleep deprivation is just your brain's dramatic way of asking for a hug, {user_name} 🌙 What's been keeping you up?",
        ]
    elif "loneliness" in t:
        opts = [
            f"{user_name}, you reached out today — which means you're braver than you think 💚 What's been making you feel this way?",
            f"Loneliness is lying to you, {user_name} — you matter more than it's telling you 🌿 What's going on?",
        ]
    elif "stress" in t:
        opts = [
            f"{user_name}, stress called — I told it you're busy thriving 😄 What's been the biggest thing on your plate?",
            f"Sounds like a lot is going on, {user_name} 🌿 Let's tackle it one thing at a time — what's weighing on you most?",
        ]
    else:
        opts = [
            f"Really glad you're here, {user_name} 🌿 No judgment, no rush — what's on your mind today?",
            f"{user_name}, this is your space 💚 What would feel good to talk about?",
            f"Hey {user_name} 🌸 Whatever brought you here today — I'm glad it did. What's going on?",
        ]

    return random.choice(opts)