from functools import wraps
from flask import request, jsonify, current_app


def admin_required(fn):
    """Protect write endpoints with an X-Admin-Key header."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.headers.get("X-Admin-Key") != current_app.config["ADMIN_KEY"]:
            return jsonify(error="Admin key required"), 401
        return fn(*args, **kwargs)

    return wrapper
