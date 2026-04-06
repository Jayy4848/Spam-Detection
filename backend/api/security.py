"""
Security utilities — input sanitization, rate limiting, API key auth,
audit logging, and threat detection.
"""

import re
import time
import hashlib
import hmac
import logging
import ipaddress
from functools import wraps
from django.core.cache import cache
from django.conf import settings
from django.http import JsonResponse
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

logger = logging.getLogger('security')
audit_logger = logging.getLogger('audit')


# ─── INPUT SANITIZATION ────────────────────────────────────────────────────────

# Characters that are never valid in an SMS message
_CONTROL_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')
# Null bytes
_NULL_BYTES     = re.compile(r'\x00')
# Script injection patterns
_SCRIPT_PATTERN = re.compile(r'<\s*script', re.IGNORECASE)
# SQL injection keywords (basic guard — ORM handles the rest)
_SQL_PATTERN    = re.compile(
    r'\b(union\s+select|drop\s+table|insert\s+into|delete\s+from|exec\s*\(|xp_cmdshell)\b',
    re.IGNORECASE
)

MAX_MESSAGE_LENGTH = 1000
MIN_MESSAGE_LENGTH = 1


def sanitize_message(text: str) -> tuple[str, list[str]]:
    """
    Sanitize and validate SMS message text.
    Returns (cleaned_text, list_of_warnings).
    Raises ValueError if text is fundamentally invalid.
    """
    if not isinstance(text, str):
        raise ValueError("Message must be a string")

    warnings = []

    # Strip null bytes
    if _NULL_BYTES.search(text):
        warnings.append("null_bytes_removed")
        text = _NULL_BYTES.sub('', text)

    # Strip control characters
    if _CONTROL_CHARS.search(text):
        warnings.append("control_chars_removed")
        text = _CONTROL_CHARS.sub('', text)

    # Normalize whitespace
    text = ' '.join(text.split())

    # Length checks
    if len(text) < MIN_MESSAGE_LENGTH:
        raise ValueError("Message is too short")
    if len(text) > MAX_MESSAGE_LENGTH:
        raise ValueError(f"Message exceeds {MAX_MESSAGE_LENGTH} characters")

    # Detect script injection attempts
    if _SCRIPT_PATTERN.search(text):
        warnings.append("script_tag_detected")
        audit_logger.warning(f"Script injection attempt: {text[:100]}")

    # Detect SQL injection attempts
    if _SQL_PATTERN.search(text):
        warnings.append("sql_pattern_detected")
        audit_logger.warning(f"SQL injection attempt: {text[:100]}")

    return text, warnings


def sanitize_language(lang: str) -> str:
    """Validate language code — only allow known values."""
    allowed = {'en', 'hi', 'mr'}
    lang = str(lang).lower().strip()[:5]
    return lang if lang in allowed else 'en'


# ─── RATE LIMITING ─────────────────────────────────────────────────────────────

class RateLimiter:
    """
    Sliding window rate limiter backed by Django cache.
    More accurate than DRF's built-in throttling.
    """

    def __init__(self, max_requests: int, window_seconds: int, prefix: str = 'rl'):
        self.max_requests   = max_requests
        self.window_seconds = window_seconds
        self.prefix         = prefix

    def get_identifier(self, request) -> str:
        """Get client identifier — prefer real IP over proxy headers."""
        # Check for proxy headers (in order of trust)
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            # Take the first IP (client), not the proxy
            ip = forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')

        # Validate it's actually an IP
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            ip = '0.0.0.0'

        return ip

    def is_allowed(self, identifier: str) -> tuple[bool, dict]:
        """
        Check if request is allowed.
        Returns (allowed, headers_dict).
        """
        key = f"{self.prefix}:{identifier}"
        now = time.time()
        window_start = now - self.window_seconds

        # Get existing request timestamps
        timestamps = cache.get(key, [])

        # Remove expired timestamps
        timestamps = [t for t in timestamps if t > window_start]

        remaining = self.max_requests - len(timestamps)
        reset_time = int(window_start + self.window_seconds)

        headers = {
            'X-RateLimit-Limit':     str(self.max_requests),
            'X-RateLimit-Remaining': str(max(0, remaining - 1)),
            'X-RateLimit-Reset':     str(reset_time),
        }

        if len(timestamps) >= self.max_requests:
            audit_logger.warning(f"Rate limit exceeded: {identifier}")
            return False, headers

        timestamps.append(now)
        cache.set(key, timestamps, timeout=self.window_seconds + 10)
        return True, headers


# Singleton rate limiters
predict_limiter = RateLimiter(max_requests=20,  window_seconds=60,   prefix='rl_predict')
global_limiter  = RateLimiter(max_requests=200, window_seconds=3600, prefix='rl_global')
admin_limiter   = RateLimiter(max_requests=5,   window_seconds=300,  prefix='rl_admin')


# ─── API KEY AUTHENTICATION ────────────────────────────────────────────────────

class ApiKeyAuthentication(BaseAuthentication):
    """
    Optional API key authentication.
    Pass key via header: X-API-Key: <key>
    If no key is provided, request proceeds as anonymous (for public endpoints).
    """

    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None  # Anonymous — let permission classes decide

        # Validate key
        valid_keys = getattr(settings, 'VALID_API_KEYS', [])
        for key_hash in valid_keys:
            if hmac.compare_digest(
                hashlib.sha256(api_key.encode()).hexdigest(),
                key_hash
            ):
                return ('api_key_user', api_key)

        audit_logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
        raise AuthenticationFailed("Invalid API key")


class IsApiKeyOrReadOnly(BasePermission):
    """Allow GET without key, require key for POST/PUT/DELETE."""

    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.auth is not None


# ─── SECURITY MIDDLEWARE ───────────────────────────────────────────────────────

class SecurityHeadersMiddleware:
    """Add comprehensive security headers to every response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'

        # Prevent MIME sniffing
        response['X-Content-Type-Options'] = 'nosniff'

        # XSS protection (legacy browsers)
        response['X-XSS-Protection'] = '1; mode=block'

        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions policy — restrict browser features
        response['Permissions-Policy'] = (
            'camera=(), microphone=(), geolocation=(), '
            'payment=(), usb=(), magnetometer=(), gyroscope=()'
        )

        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

        # Remove server fingerprinting headers
        try:
            del response['Server']
        except KeyError:
            pass
        try:
            del response['X-Powered-By']
        except KeyError:
            pass

        return response


class BruteForceProtectionMiddleware:
    """
    Block IPs that repeatedly hit the API with bad requests.
    Tracks 429/400/401 responses per IP.
    """

    BLOCK_THRESHOLD = 50   # bad requests before block
    BLOCK_DURATION  = 3600  # 1 hour block
    WINDOW          = 600   # 10 minute window

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self._get_ip(request)
        block_key = f"blocked:{ip}"

        # Check if IP is blocked
        if cache.get(block_key):
            audit_logger.warning(f"Blocked IP attempted access: {ip}")
            return JsonResponse(
                {'error': 'Too many failed requests. Try again later.'},
                status=429
            )

        response = self.get_response(request)

        # Track bad responses
        if response.status_code in (400, 401, 403, 429):
            bad_key = f"bad_req:{ip}"
            count = cache.get(bad_key, 0) + 1
            cache.set(bad_key, count, timeout=self.WINDOW)

            if count >= self.BLOCK_THRESHOLD:
                cache.set(block_key, True, timeout=self.BLOCK_DURATION)
                audit_logger.error(f"IP blocked for excessive bad requests: {ip}")

        return response

    def _get_ip(self, request) -> str:
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')


# ─── AUDIT LOGGING ─────────────────────────────────────────────────────────────

def audit_log(event: str, request=None, extra: dict = None):
    """Write a structured audit log entry."""
    entry = {
        'event':     event,
        'timestamp': time.time(),
    }

    if request:
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        entry['ip']         = xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')
        entry['method']     = request.method
        entry['path']       = request.path
        entry['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:200]

    if extra:
        entry.update(extra)

    audit_logger.info(str(entry))
