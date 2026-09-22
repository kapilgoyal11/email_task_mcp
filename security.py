"""
Security helpers for the email_task_mcp server:
- sanitize_header(): blocks email header injection (CWE-93)
- RateLimiter: simple in-memory sliding-window limiter
"""
import time


class HeaderInjectionError(ValueError):
    """Raised when a field meant for an email header contains
    characters that could inject extra headers."""


def sanitize_header(value: str, field_name: str) -> str:
    """Reject a header-bound value containing CR/LF, which could be
    used to inject extra email headers (e.g. a hidden Bcc:).

    Raises:
        HeaderInjectionError: if value contains \\r or \\n.
    """
    if "\r" in value or "\n" in value:
        raise HeaderInjectionError(
            f"Invalid characters in {field_name}: header injection attempt blocked."
        )
    return value


class RateLimiter:
    """Simple in-memory sliding-window rate limiter.

    Not for production/multi-process use (state is per-process,
    in-memory only) but sufficient to demonstrate the pattern for
    this assignment.
    """

    def __init__(self, max_calls: int, window_seconds: float):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._call_times: list[float] = []

    def allow(self) -> bool:
        now = time.monotonic()
        # Drop timestamps outside the current window
        self._call_times = [t for t in self._call_times if now - t < self.window_seconds]
        if len(self._call_times) >= self.max_calls:
            return False
        self._call_times.append(now)
        return True