from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .status import aggregate_status


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def check(
    check_id: str,
    status: str,
    message: str,
    *,
    category: str,
    severity: str = "error",
    confidence: str = "deterministic",
    reason_code: str | None = None,
    evidence: list[Any] | None = None,
    remediation: list[str] | None = None,
    source: str = "cmtk",
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "id": check_id,
        "category": category,
        "severity": severity,
        "status": status,
        "confidence": confidence,
        "message": message,
        "evidence": evidence or [],
        "remediation": remediation or [],
        "source": source,
    }
    if reason_code:
        value["reason_code"] = reason_code
    return value


def stage_result(
    *,
    route: str,
    stage: str,
    checks: list[dict[str, Any]],
    execution_type: str = "AUTO",
    execution_context: str = "host-cpython",
    actions: list[str] | None = None,
    inputs: list[dict[str, Any]] | None = None,
    changes: list[dict[str, Any]] | None = None,
    artifacts: list[dict[str, Any]] | None = None,
    metrics: list[dict[str, Any]] | None = None,
    next_allowed_stages: list[str] | None = None,
) -> dict[str, Any]:
    timestamp = utc_now()
    status = aggregate_status(item["status"] for item in checks)
    return {
        "schema_version": "1.0.0",
        "run_id": f"inspect-{route}",
        "route": route,
        "stage": stage,
        "status": status,
        "execution_type": execution_type,
        "execution_context": execution_context,
        "started_at": timestamp,
        "finished_at": timestamp,
        "inputs": inputs or [],
        "actions": actions or [],
        "changes": changes or [],
        "checks": checks,
        "metrics": metrics or [],
        "artifacts": artifacts or [],
        "warnings": [item["message"] for item in checks if item["status"] == "WARN"],
        "failures": [item["message"] for item in checks if item["status"] in {"FAIL", "BLOCKED"}],
        "rollback": {},
        "next_allowed_stages": next_allowed_stages or [],
    }
