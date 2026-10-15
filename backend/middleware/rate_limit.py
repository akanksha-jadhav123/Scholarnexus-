"""
Simple in-memory rate limiter. Prunes empty buckets.
"""
import time
from functools import wraps
from flask import request, jsonify

_requests = {}  # {key: [timestamps]}
WINDOW_SECONDS = 60
_last_prune = time.time()


def _prune_stale(now):
    """Remove keys whose timestamps are all expired."""
    global _last_prune
    if now - _last_prune < 30:  # only every 30s
        return
    _last_prune = now
    stale = []
    for key, times in _requests.items():
        fresh = [t for t in times if now - t < WINDOW_SECONDS]
        if fresh:
            _requests[key] = fresh
        else:
            stale.append(key)
    for key in stale:
        _requests.pop(key, None)


def rate_limit(max_per_minute=10):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Respect proxy headers
            ip = (
                request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
                or request.remote_addr
                or "unknown"
            )
            key = f"{ip}:{request.endpoint}"
            now = time.time()
            _prune_stale(now)

            times = [t for t in _requests.get(key, []) if now - t < WINDOW_SECONDS]
            if len(times) >= max_per_minute:
                return jsonify({
                    "error": f"Rate limit exceeded. Max {max_per_minute} requests/min."
                }), 429

            times.append(now)
            _requests[key] = times
            return fn(*args, **kwargs)
        return wrapper
    return decorator