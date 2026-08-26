from __future__ import annotations

from collections.abc import Iterable

from .errors import CmtkError

STATUSES = {"PASS", "WARN", "FAIL", "NOT_RUN", "NOT_APPLICABLE", "BLOCKED"}


def aggregate_status(statuses: Iterable[str]) -> str:
    values = list(statuses)
    unknown = sorted(set(values) - STATUSES)
    if unknown:
        raise CmtkError("STATUS-INVALID", "Unknown status value.", details={"values": unknown})
    if not values:
        return "NOT_RUN"
    if "BLOCKED" in values:
        return "BLOCKED"
    if "FAIL" in values:
        return "FAIL"
    if "NOT_RUN" in values:
        return "NOT_RUN"
    if "WARN" in values:
        return "WARN"
    if all(value == "NOT_APPLICABLE" for value in values):
        return "NOT_APPLICABLE"
    return "PASS"
