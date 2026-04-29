# =====================================================
#  middleware/rate_limiter.py
#  Flask-Limiter configuration for API abuse prevention
# =====================================================

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialise without binding to an app (use init_app pattern)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200000 per day", "5000 per hour"],
    storage_uri="memory://",   # In-memory store — use Redis URI in production
)

# Route-specific limit decorators (imported in routes)
CHAT_LIMIT    = "300 per minute"
GENERAL_LIMIT = "600 per minute"