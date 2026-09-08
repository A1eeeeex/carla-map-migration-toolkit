from __future__ import annotations

import math
from typing import Any

from cmtk.core.errors import CmtkError

STATISTICS = ("mean", "median", "p95", "p99", "max")
DEFAULT_HIGHER_IS_BETTER = {"FPS", "fps", "mean_fps", "average_fps"}


def _valid_counter(value: Any) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def compare_metrics(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    *,
    statistic: str = "mean",
    metrics: list[str] | None = None,
    higher_is_better: list[str] | None = None,
) -> dict[str, Any]:
    """Report counter deltas without conferring optimization acceptance."""
    if statistic not in STATISTICS:
        raise CmtkError("PERF-INPUT-INVALID", "Unknown metric statistic.")
    left = baseline.get("metrics", baseline)
    right = candidate.get("metrics", candidate)
    if not isinstance(left, dict) or not isinstance(right, dict):
        raise CmtkError("PERF-INPUT-INVALID", "Metric reports must contain objects.")
    requested = sorted(set(left) | set(right)) if metrics is None else list(dict.fromkeys(metrics))
    higher = DEFAULT_HIGHER_IS_BETTER | set(higher_is_better or [])
    rows = []
    missing = []
    invalid = []
    for name in requested:
        values = []
        for source in (left, right):
            value = source.get(name)
            values.append(value.get(statistic) if isinstance(value, dict) else value)
        if any(value is not None and not _valid_counter(value) for value in values):
            invalid.append(name)
            continue
        if any(value is None for value in values):
            missing.append(name)
            continue
        before, after = values
        delta = after - before
        benefit = delta if name in higher else -delta
        improvement = benefit / before * 100 if before else None
        if improvement is not None and not math.isfinite(improvement):
            improvement = None
        rows.append(
            {
                "metric": name,
                "before": before,
                "after": after,
                "improvement_percent": improvement,
                "direction": "higher_is_better" if name in higher else "lower_is_better",
                "change": "improved" if benefit > 0 else ("regressed" if benefit < 0 else "unchanged"),
            }
        )
    regressions = [row["metric"] for row in rows if row["change"] == "regressed"]
    reasons = []
    if missing or not rows:
        reasons.append("PERF-METRIC-MISSING")
    if invalid:
        reasons.append("PERF-INPUT-INVALID")
    if regressions:
        reasons.append("PERF-SECONDARY-REGRESSION")
    conditions = baseline.get("conditions")
    conditions_match = (
        conditions == candidate.get("conditions")
        if isinstance(conditions, dict) and conditions and isinstance(candidate.get("conditions"), dict)
        else None
    )
    # Even matching arbitrary dictionaries are not a validated performance contract.
    return {
        "schema_version": "1.0.0",
        "report_type": "metric-deltas",
        "execution_context": "host-cpython",
        "status": "FAIL" if invalid or not rows else "WARN",
        "statistic": statistic,
        "rows": rows,
        "regressions": regressions,
        "missing_metrics": missing,
        "invalid_metrics": invalid,
        "reason_codes": reasons,
        "supplied_conditions_equal": conditions_match,
        "optimization_acceptance": "NOT_RUN",
        "limitations": [
            "Numeric deltas are diagnostic only. Use compare-performance with matched conditions "
            "and protected hashes for acceptance."
        ],
    }
