from __future__ import annotations

import math
import re
from typing import Any

PROTECTED_REASON_CODES = {
    "lod0_sha256": "PERF-LOD0-CHANGED",
    "material_slots_sha256": "PERF-MATERIAL-SLOT-CHANGED",
    "transforms_sha256": "PERF-TRANSFORM-CHANGED",
    "collision_sha256": "PERF-COLLISION-REGRESSION",
    "xodr_sha256": "PERF-XODR-REGRESSION",
}
REQUIRED_CONDITIONS = {
    "hardware_id",
    "os",
    "target_profile",
    "resolution",
    "quality",
    "camera_profile_sha256",
    "traffic_profile_sha256",
    "sensor_profile_sha256",
    "warmup_frames",
    "sample_frames",
    "repeats",
    "vsync",
    "fps_cap",
}
CONDITION_HASH_FIELDS = {"camera_profile_sha256", "traffic_profile_sha256", "sensor_profile_sha256"}
CONDITION_TEXT_FIELDS = {"hardware_id", "os", "target_profile", "resolution", "quality"}
_SHA256 = re.compile(r"[0-9a-f]{64}")


def _append_once(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)


def _valid_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0


def _validate_conditions(
    snapshot: dict[str, Any], label: str, reason_codes: list[str], differences: dict[str, Any]
) -> dict[str, Any]:
    conditions = snapshot.get("conditions")
    if not isinstance(conditions, dict):
        _append_once(reason_codes, "PERF-CONDITIONS-INCOMPLETE")
        differences[f"{label}_conditions_missing"] = sorted(REQUIRED_CONDITIONS)
        return {}

    missing = sorted(field for field in REQUIRED_CONDITIONS if field not in conditions or conditions[field] is None)
    if missing:
        _append_once(reason_codes, "PERF-CONDITIONS-INCOMPLETE")
        differences[f"{label}_conditions_missing"] = missing

    invalid: list[str] = []
    invalid.extend(
        field for field in CONDITION_TEXT_FIELDS if field in conditions and not isinstance(conditions[field], str)
    )
    invalid.extend(
        field
        for field in CONDITION_TEXT_FIELDS
        if isinstance(conditions.get(field), str) and not conditions[field].strip()
    )
    invalid.extend(
        field
        for field in CONDITION_HASH_FIELDS
        if field in conditions
        and conditions[field] is not None
        and (not isinstance(conditions[field], str) or _SHA256.fullmatch(conditions[field]) is None)
    )
    invalid.extend(
        field
        for field in ("warmup_frames", "sample_frames", "repeats")
        if field in conditions
        and conditions[field] is not None
        and (
            not isinstance(conditions[field], int)
            or isinstance(conditions[field], bool)
            or conditions[field] < (0 if field == "warmup_frames" else 1)
        )
    )
    if "vsync" in conditions and conditions["vsync"] is not None and not isinstance(conditions["vsync"], bool):
        invalid.append("vsync")
    fps_cap = conditions.get("fps_cap")
    if fps_cap is not None and (
        not isinstance(fps_cap, (int, float)) or isinstance(fps_cap, bool) or not math.isfinite(fps_cap) or fps_cap < 0
    ):
        invalid.append("fps_cap")
    if invalid:
        _append_once(reason_codes, "PERF-CONDITIONS-INVALID")
        differences[f"{label}_conditions_invalid"] = sorted(set(invalid))
    return conditions


def compare_snapshots(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    reason_codes: list[str] = []
    differences: dict[str, Any] = {}
    for label, snapshot in (("baseline", baseline), ("candidate", candidate)):
        invalid_sections = [
            section for section in ("conditions", "metrics", "protected") if not isinstance(snapshot.get(section), dict)
        ]
        if snapshot.get("schema_version") != "1.0.0":
            invalid_sections.append("schema_version")
        if invalid_sections:
            _append_once(reason_codes, "PERF-INPUT-INVALID")
            differences[f"{label}_invalid_sections"] = sorted(invalid_sections)
    _validate_conditions(baseline, "baseline", reason_codes, differences)
    candidate_conditions = _validate_conditions(candidate, "candidate", reason_codes, differences)
    if baseline.get("conditions") != candidate.get("conditions"):
        reason_codes.append("PERF-CONDITIONS-NOT-COMPARABLE")
        differences["conditions"] = {"baseline": baseline.get("conditions"), "candidate": candidate.get("conditions")}
    if candidate_conditions.get("vsync"):
        reason_codes.append("PERF-VSYNC-ENABLED")
    if candidate_conditions.get("fps_cap") not in (None, 0, 0.0):
        reason_codes.append("PERF-FPS-CAPPED")
    baseline_protected = baseline.get("protected") if isinstance(baseline.get("protected"), dict) else {}
    candidate_protected = candidate.get("protected") if isinstance(candidate.get("protected"), dict) else {}
    for field, reason_code in PROTECTED_REASON_CODES.items():
        left = baseline_protected.get(field)
        right = candidate_protected.get(field)
        if not left or not right:
            _append_once(reason_codes, "PERF-PROTECTED-EVIDENCE-MISSING")
            differences[field] = {"baseline": left, "candidate": right}
        elif (
            not isinstance(left, str)
            or not isinstance(right, str)
            or not _SHA256.fullmatch(left)
            or not _SHA256.fullmatch(right)
        ):
            _append_once(reason_codes, "PERF-PROTECTED-EVIDENCE-INVALID")
            differences[field] = {"baseline": left, "candidate": right}
        elif left != right:
            reason_codes.append(reason_code)
            differences[field] = {"baseline": left, "candidate": right}

    baseline_metrics = baseline.get("metrics") if isinstance(baseline.get("metrics"), dict) else {}
    candidate_metrics = candidate.get("metrics") if isinstance(candidate.get("metrics"), dict) else {}
    baseline_median = baseline_metrics.get("median_frame_ms")
    candidate_median = candidate_metrics.get("median_frame_ms")
    improvement = None
    if _valid_positive_number(baseline_median) and _valid_positive_number(candidate_median):
        improvement = round((baseline_median - candidate_median) / baseline_median * 100.0, 6)
        if improvement <= 0:
            reason_codes.append("PERF-NO-MEASURABLE-IMPROVEMENT")
    else:
        reason_codes.append("PERF-METRIC-MISSING")

    baseline_p95 = baseline_metrics.get("p95_frame_ms")
    candidate_p95 = candidate_metrics.get("p95_frame_ms")
    if _valid_positive_number(baseline_p95) and _valid_positive_number(candidate_p95):
        if candidate_p95 > baseline_p95:
            reason_codes.append("PERF-P95-REGRESSION")
            differences["p95_frame_ms"] = {"baseline": baseline_p95, "candidate": candidate_p95}
    elif "PERF-METRIC-MISSING" not in reason_codes:
        reason_codes.append("PERF-METRIC-MISSING")

    hard_failure = any(code not in {"PERF-VSYNC-ENABLED", "PERF-FPS-CAPPED"} for code in reason_codes)
    status = "FAIL" if hard_failure else ("WARN" if reason_codes else "PASS")
    return {
        "schema_version": "1.0.0",
        "status": status,
        "reason_codes": reason_codes,
        "differences": differences,
        "median_frame_time_improvement_percent": improvement,
    }
