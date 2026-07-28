from collections import defaultdict
from functools import wraps
from time import time

from django.http import JsonResponse


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time()
        cutoff = now - self.window_seconds
        self.requests[key] = [t for t in self.requests[key] if t > cutoff]
        if len(self.requests[key]) >= self.max_requests:
            return False
        self.requests[key].append(now)
        return True


_login_limiter = RateLimiter(max_requests=5, window_seconds=60)
_redeem_limiter = RateLimiter(max_requests=10, window_seconds=60)
_access_code_limiter = RateLimiter(max_requests=10, window_seconds=60)


def rate_limit(limiter: RateLimiter):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            ip = request.META.get("REMOTE_ADDR", "unknown")
            if not limiter.is_allowed(ip):
                return JsonResponse(
                    {"error": "Too many requests. Please try again later."},
                    status=429,
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


login_rate_limit = rate_limit(_login_limiter)
redeem_rate_limit = rate_limit(_redeem_limiter)
access_code_rate_limit = rate_limit(_access_code_limiter)
