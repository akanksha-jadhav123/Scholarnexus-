"""
Simple in-memory rate limiter for expensive endpoints.
Prevents scraping abuse and API hammering.
"""
import time
from functools import wraps
from flask import request, jsonify


_requests = {}  # {key: [timestamps]}
WINDOW_SECONDS = 60


def rate_limit(max_per_minute=10):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = f"{request.remote_addr}:{request.endpoint}"
            now = time.time()

            # Cleanup old
            _requests[key] = [t for t in _requests.get(key, []) if now - t < WINDOW_SECONDS]

            if len(_requests[key]) >= max_per_minute:
                return jsonify({
                    "error": f"Rate limit exceeded. Max {max_per_minute} requests/min."
                }), 429

            _requests[key].append(now)
            return fn(*args, **kwargs)
        return wrapper
    return decorator