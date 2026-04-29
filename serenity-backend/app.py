# =====================================================
#  app.py  —  Serenity Backend Entry Point
#  Run:  python app.py
#  Production:  gunicorn app:app
# =====================================================

import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from personalization.user_profiles import PersonalizationEngine
load_dotenv()  # Load .env before anything else

from routes.chat              import chat_bp
from middleware.rate_limiter  import limiter

# ── App Factory ─────────────────────────────────────────────────────────────
def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)
    # Initialize personalization engine
    app.personalization_engine = PersonalizationEngine()
    # ── CORS ─────────────────────────────────────────────────────────────────
    # In production, replace "*" with your actual frontend origin
    CORS(app, resources={
        r"/api/*": {
            "origins": os.getenv("ALLOWED_ORIGINS", "*").split(","),
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })

    # ── Rate Limiter ──────────────────────────────────────────────────────────
    limiter.init_app(app)

    # ── Blueprints ────────────────────────────────────────────────────────────
    app.register_blueprint(chat_bp, url_prefix="/api")

    # ── Health check ──────────────────────────────────────────────────────────
    @app.route("/api/health", methods=["GET"])
    def health():
        """Simple liveness probe."""
        api_key_set = bool(os.getenv("ANTHROPIC_API_KEY"))
        return jsonify({
            "status":      "ok",
            "service":     "Serenity Mental Health API",
            "version":     "1.0.0",
            "api_key_set": api_key_set,
        })

    # ── 404 handler ───────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found"}), 404

    # ── 429 rate limit handler ────────────────────────────────────────────────
    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({
            "error": "Too many requests. Please slow down.",
            "retry_after": str(e.description),
        }), 429

    # ── 500 handler ───────────────────────────────────────────────────────────
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    port  = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    print(f"""
╔══════════════════════════════════════════════════╗
║          🌿  Serenity Backend  v1.0.0            ║
╠══════════════════════════════════════════════════╣
║  Running on : http://localhost:{port}               ║
║  Debug mode : {str(debug):<36}║
║  API key    : {'SET ✓' if os.getenv('ANTHROPIC_API_KEY') else 'NOT SET ✗':<36}║
╠══════════════════════════════════════════════════╣
║  Endpoints:                                      ║
║   GET  /api/health                               ║
║   POST /api/chat                                 ║
║   POST /api/analyse                              ║
║   GET  /api/resources                            ║
╚══════════════════════════════════════════════════╝
    """)

    app.run(host="0.0.0.0", port=port, debug=debug)