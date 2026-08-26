from __future__ import annotations

import re
from collections.abc import Iterable

_EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
_LOCAL_PATH = re.compile(r"(?<!\w)/(?:home|Users|root|mnt|media|opt|srv|workspace|data|tmp|var)/[^\s\"']+")
_ASSET_PATH = re.compile(r"(?<!\w)/Game/[^\s\"']+")
_SECRET_ASSIGNMENT = re.compile(r"(?i)\b(token|api[_-]?key|password|secret)\s*[:=]\s*([^\s,;]+)")


def redact_text(value: str, *, sensitive_terms: Iterable[str] = ()) -> str:
    """Redact common sensitive strings and caller-supplied private identifiers."""

    result = value
    terms = sorted({term.strip() for term in sensitive_terms if term.strip()}, key=len, reverse=True)
    for term in terms:
        result = re.sub(re.escape(term), "[REDACTED_IDENTIFIER]", result, flags=re.IGNORECASE)
    result = _EMAIL.sub("[REDACTED_EMAIL]", result)
    result = _IPV4.sub("[REDACTED_NETWORK]", result)
    result = _ASSET_PATH.sub("[REDACTED_ASSET_PATH]", result)
    result = _LOCAL_PATH.sub("[REDACTED_LOCAL_PATH]", result)
    result = _SECRET_ASSIGNMENT.sub(lambda match: f"{match.group(1)}=[REDACTED_SECRET]", result)
    return result
