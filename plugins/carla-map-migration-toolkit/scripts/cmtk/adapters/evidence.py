from __future__ import annotations

import importlib
import os
import re
import shutil
import tempfile
from datetime import datetime
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Any

import jsonschema

from cmtk.core.context import current_context, require_context
from cmtk.core.errors import CmtkError
from cmtk.core.evidence import check, stage_result
from cmtk.core.hashing import sha256_file, sha256_json
from cmtk.core.jsonio import load_json, render_json, write_json_atomic
from cmtk.core.paths import require_within_roots
from cmtk.core.plans import verify_input_fingerprints, verify_plan, verify_workspace_fingerprint
from cmtk.core.redaction import redact_text
from cmtk.routes.catalog import (
    OPTIONAL_STAGE_CHECK_EVIDENCE_TYPES,
    OPTIONAL_STAGE_CHECK_STAGES,
    REQUIRED_CHECK_EVIDENCE_TYPES,
    REQUIRED_CHECK_STAGES,
)

_SCHEMA_ROOT = Path(__file__).resolve().parents[3] / "schemas"
_CONTEXT_RECEIPT_ADAPTER = Path(__file__).resolve().parents[2] / "context_receipt.py"
_EXTERNAL_CONTEXTS = {
    "source-unreal-python",
    "ue427-unreal-python",
    "carla-client-python",
    "shell-build",
}
_VERSION_TRIPLET = re.compile(r"\d+\.\d+\.\d+")
MAX_PUBLIC_EVIDENCE_BYTES = 64 * 1024 * 1024


@lru_cache(maxsize=None)
def _schema(name: str) -> dict[str, Any]:
    value = load_json(_SCHEMA_ROOT / f"{name}.schema.json")
    if not isinstance(value, dict):
        raise CmtkError("ADAPTER-EVIDENCE-INVALID", "Evidence schema must be a JSON object.")
    return value


def _validate(value: dict[str, Any], schema_name: str, reason_code: str, label: str) -> None:
    errors = sorted(
        jsonschema.Draft202012Validator(_schema(schema_name)).iter_errors(value),
        key=lambda error: list(error.path),
    )
    if errors:
        first = errors[0]
        raise CmtkError(
            reason_code,
            f"{label} does not satisfy its schema.",
            details={"schema_path": list(first.schema_path), "validation_message": first.message},
        )


def _repository_relative(value: str, *, label: str) -> str:
    if not value or "\\" in value:
        raise CmtkError("ADAPTER-PUBLIC-PATH-INVALID", f"{label} must be a repository-relative POSIX path.")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or ".." in path.parts
        or path.as_posix() != value
        or path.parts[0] != "evidence"
    ):
        raise CmtkError("ADAPTER-PUBLIC-PATH-INVALID", f"{label} must be under the public evidence directory.")
    return value


def _sensitive_terms(path: str, allowed_roots: list[str]) -> tuple[str, ...]:
    terms_path = require_within_roots(path, allowed_roots)
    if not terms_path.is_file() or terms_path.is_symlink():
        raise CmtkError(
            "ADAPTER-SENSITIVE-TERMS-REQUIRED",
            "A regular private sensitive-term file is required before evidence can be recorded.",
        )
    try:
        terms = tuple(
            sorted(
                {
                    line.strip()
                    for line in terms_path.read_text(encoding="utf-8").splitlines()
                    if line.strip() and not line.lstrip().startswith("#")
                }
            )
        )
    except (OSError, UnicodeDecodeError) as error:
        raise CmtkError(
            "ADAPTER-SENSITIVE-TERMS-REQUIRED",
            "The private sensitive-term file must be readable UTF-8 text.",
        ) from error
    if not terms:
        raise CmtkError(
            "ADAPTER-SENSITIVE-TERMS-REQUIRED",
            "The private sensitive-term file must contain at least one reviewed literal.",
        )
    return terms


def _require_public_safe(text: str, terms: tuple[str, ...], *, label: str) -> None:
    if redact_text(text, sensitive_terms=terms) != text:
        raise CmtkError(
            "ADAPTER-SENSITIVE-DATA-DETECTED",
            f"{label} contains a private or non-public-safe literal.",
        )


def _require_utc_timestamp(value: str, *, label: str) -> None:
    if not isinstance(value, str) or "T" not in value or not value.endswith("Z"):
        raise CmtkError("ADAPTER-RECEIPT-INVALID", f"{label} must be a valid UTC timestamp.")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise CmtkError(
            "ADAPTER-RECEIPT-INVALID",
            f"{label} must be a valid UTC timestamp.",
        ) from error


def _safe_file_record(
    record: dict[str, Any],
    allowed_roots: list[str],
    terms: tuple[str, ...],
    *,
    label: str,
    allowed_kinds: set[str] | None = None,
) -> dict[str, Any]:
    if allowed_kinds is not None and record["kind"] not in allowed_kinds:
        raise CmtkError(
            "ADAPTER-EVIDENCE-INVALID",
            f"{label} kind is not accepted for public evidence.",
        )
    raw_path = Path(record["local_path"])
    if raw_path.is_symlink():
        raise CmtkError("ADAPTER-EVIDENCE-INVALID", f"{label} must not be a symbolic link.")
    path = require_within_roots(raw_path, allowed_roots)
    if not path.is_file():
        raise CmtkError("ADAPTER-EVIDENCE-INVALID", f"{label} must be an existing regular file.")
    if path.stat().st_size > MAX_PUBLIC_EVIDENCE_BYTES:
        raise CmtkError(
            "ADAPTER-EVIDENCE-INVALID",
            f"{label} exceeds the public evidence size limit.",
        )
    actual_sha256 = sha256_file(path)
    if actual_sha256 != record["sha256"]:
        raise CmtkError(
            "ADAPTER-EVIDENCE-INVALID",
            f"{label} SHA-256 does not match the receipt.",
            details={"expected": record["sha256"], "actual": actual_sha256},
        )
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise CmtkError(
            "ADAPTER-EVIDENCE-INVALID",
            f"{label} must be readable UTF-8 text before it can enter public evidence.",
        ) from error
    _require_public_safe(content, terms, label=label)
    return {
        "path": _repository_relative(record["public_path"], label=f"{label} public path"),
        "sha256": actual_sha256,
        "kind": record["kind"],
    }


def _version_triplet(value: str) -> str | None:
    match = _VERSION_TRIPLET.search(value)
    return match.group(0) if match else None


def _require_value(label: str, actual: Any, expected: Any) -> None:
    if not isinstance(actual, str) or not actual or actual != expected:
        raise CmtkError(
            "ADAPTER-ENVIRONMENT-MISMATCH",
            f"{label} does not match the fingerprinted workspace.",
            details={"expected": expected, "actual": actual},
        )


def _verify_unreal_boundary(environment: dict[str, Any], configured_version: str) -> None:
    try:
        unreal = importlib.import_module("unreal")
        runtime_version = str(unreal.SystemLibrary.get_engine_version())
    except (ImportError, AttributeError, RuntimeError) as error:
        raise CmtkError(
            "ADAPTER-API-UNAVAILABLE",
            "The Unreal Python API and engine-version probe are required in this execution context.",
        ) from error
    _require_value("Runtime Unreal version", environment.get("runtime_engine_version"), runtime_version)
    if _version_triplet(runtime_version) != _version_triplet(configured_version):
        raise CmtkError(
            "ADAPTER-ENVIRONMENT-MISMATCH",
            "The runtime Unreal version does not match the configured engine line.",
            details={"configured": configured_version, "runtime": runtime_version},
        )


def _verify_declared_environment(workspace: dict[str, Any], receipt: dict[str, Any]) -> str:
    context = receipt["execution_context"]
    environment = receipt["environment"]
    source = workspace["source_carla"]
    if context == "source-unreal-python":
        _require_value("Execution platform", environment.get("platform"), source["platform"])
        _require_value("Source CARLA version", environment.get("source_carla_version"), source["version"])
        _require_value("Source Unreal version", environment.get("source_ue_version"), source["engine_version"])
        runtime_triplet = _version_triplet(environment.get("runtime_engine_version", ""))
        if runtime_triplet != _version_triplet(source["engine_version"]):
            raise CmtkError("ADAPTER-ENVIRONMENT-MISMATCH", "Source Unreal runtime engine line does not match.")
        return source["engine_version"]
    if context == "ue427-unreal-python":
        target = workspace.get("ue427", {})
        _require_value("Execution platform", environment.get("platform"), source["platform"])
        _require_value("Target Unreal version", environment.get("target_ue_version"), target.get("engine_version"))
        runtime_triplet = _version_triplet(environment.get("runtime_engine_version", ""))
        if runtime_triplet != _version_triplet(target["engine_version"]):
            raise CmtkError("ADAPTER-ENVIRONMENT-MISMATCH", "Target Unreal runtime engine line does not match.")
        return target["engine_version"]
    if context == "carla-client-python":
        expected = (
            workspace["package_carla"]["version"]
            if receipt["route"] == "source-carla-to-package-carla"
            else source["version"]
        )
        expected_platform = (
            workspace["package_carla"]["platform"]
            if receipt["route"] == "source-carla-to-package-carla"
            else source["platform"]
        )
        _require_value("Execution platform", environment.get("platform"), expected_platform)
        _require_value("CARLA client version", environment.get("carla_client_version"), expected)
        _require_value("CARLA server version", environment.get("carla_server_version"), expected)
        return expected
    if context == "shell-build":
        operation = receipt["operation"]
        if "command_sha256" not in operation or "return_code" not in operation:
            raise CmtkError(
                "ADAPTER-EVIDENCE-INVALID",
                "Shell-build evidence requires a command hash and return code.",
            )
        if any(item["status"] == "PASS" for item in receipt["checks"]) and operation["return_code"] != 0:
            raise CmtkError(
                "ADAPTER-EVIDENCE-INVALID",
                "A non-zero shell-build return code cannot support a PASS check.",
            )
        _require_value("Source CARLA version", environment.get("source_carla_version"), source["version"])
        package = workspace.get("package_carla", {})
        _require_value("Execution platform", environment.get("platform"), package.get("platform"))
        _require_value("Target CARLA version", environment.get("target_carla_version"), package.get("version"))
        return package["version"]
    raise CmtkError("ADAPTER-RECEIPT-INVALID", "Receipt execution context is not an external adapter context.")


def _verify_live_api(receipt: dict[str, Any], configured_version: str) -> None:
    context = receipt["execution_context"]
    if context in {"source-unreal-python", "ue427-unreal-python"}:
        _verify_unreal_boundary(receipt["environment"], configured_version)
        return
    if context == "carla-client-python":
        try:
            carla = importlib.import_module("carla")
            client = carla.Client
        except (ImportError, AttributeError) as error:
            raise CmtkError(
                "ADAPTER-API-UNAVAILABLE",
                "The CARLA client Python API is required in this execution context.",
            ) from error
        if client is None:
            raise CmtkError("ADAPTER-API-UNAVAILABLE", "The CARLA client class is unavailable.")


def _verify_finalized_boundary(receipt: dict[str, Any]) -> None:
    boundary = receipt.get("boundary")
    if not isinstance(boundary, dict):
        raise CmtkError(
            "ENV-EXECUTION-CONTEXT-MISMATCH",
            "Host recording requires a receipt finalized by the external context adapter.",
        )
    _require_utc_timestamp(boundary.get("finalized_at"), label="Boundary finalized_at")
    draft = dict(receipt)
    draft.pop("boundary")
    expected_api = {
        "source-unreal-python": receipt["environment"].get("runtime_engine_version"),
        "ue427-unreal-python": receipt["environment"].get("runtime_engine_version"),
        "carla-client-python": f"carla-client-server-{receipt['environment'].get('carla_server_version')}",
        "shell-build": "shell-build-command-receipt",
    }[receipt["execution_context"]]
    if (
        boundary.get("adapter") != "cmtk-context-receipt"
        or boundary.get("adapter_sha256") != sha256_file(_CONTEXT_RECEIPT_ADAPTER)
        or boundary.get("draft_sha256") != sha256_json(draft)
        or boundary.get("observed_context") != receipt["execution_context"]
        or boundary.get("observed_api_version") != expected_api
    ):
        raise CmtkError(
            "ADAPTER-RECEIPT-INVALID",
            "External context boundary proof does not match the receipt or installed adapter.",
        )


def _verify_environment(workspace: dict[str, Any], receipt: dict[str, Any]) -> None:
    configured_version = _verify_declared_environment(workspace, receipt)
    actual_context = current_context()
    if actual_context == receipt["execution_context"]:
        _verify_live_api(receipt, configured_version)
        return
    if actual_context == "host-cpython":
        _verify_finalized_boundary(receipt)
        return
    require_context(receipt["execution_context"])


def _find_step(plan: dict[str, Any], receipt: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    matching = [step for step in plan["steps"] if step["step_id"] == receipt["stage"]]
    if len(matching) != 1:
        raise CmtkError("ADAPTER-RECEIPT-INVALID", "Receipt stage is not present exactly once in the sealed plan.")
    step = matching[0]
    if step["execution_context"] != receipt["execution_context"]:
        raise CmtkError(
            "ENV-EXECUTION-CONTEXT-MISMATCH",
            "Receipt execution context does not match the planned stage.",
            details={"expected": step["execution_context"], "actual": receipt["execution_context"]},
        )
    stage_ids = [item["step_id"] for item in plan["steps"]]
    index = stage_ids.index(receipt["stage"])
    return step, stage_ids[index + 1 : index + 2]


def _verify_operation(step: dict[str, Any], receipt: dict[str, Any]) -> None:
    operation = receipt["operation"]
    rollback = receipt["rollback"]
    if not step["write_paths"]:
        if operation["mode"] != "AUDIT" or receipt["changes"]:
            raise CmtkError(
                "ADAPTER-ROLLBACK-INCOMPLETE",
                "Read-only stages must use AUDIT mode and declare no changes.",
            )
        if rollback["status"] != "NOT_APPLICABLE":
            raise CmtkError(
                "ADAPTER-ROLLBACK-INCOMPLETE",
                "Read-only stages must mark rollback NOT_APPLICABLE.",
            )
        return
    if operation["mode"] not in {"APPLY_SAFE", "APPLY_PLAN"}:
        raise CmtkError(
            "ADAPTER-ROLLBACK-INCOMPLETE",
            "A planned write stage requires explicit apply mode.",
        )
    if rollback["status"] not in {"READY", "VERIFIED"} or not rollback["steps"]:
        raise CmtkError(
            "ADAPTER-ROLLBACK-INCOMPLETE",
            "A planned write stage requires rollback steps and READY or VERIFIED status.",
        )
    if step["backup"].get("required") and "backup_manifest" not in rollback:
        raise CmtkError(
            "ADAPTER-ROLLBACK-INCOMPLETE",
            "A planned write stage requires a hashed backup manifest.",
        )


def _build_records(
    receipt: dict[str, Any],
    step: dict[str, Any],
    next_stages: list[str],
    allowed_roots: list[str],
    evidence_prefix: str,
    terms: tuple[str, ...],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    route = receipt["route"]
    stage = receipt["stage"]
    expected_checks = REQUIRED_CHECK_STAGES[route]
    expected_types = REQUIRED_CHECK_EVIDENCE_TYPES[route]
    optional_checks = OPTIONAL_STAGE_CHECK_STAGES[route]
    optional_types = OPTIONAL_STAGE_CHECK_EVIDENCE_TYPES[route]
    required_for_stage = {check_id for check_id, stages in expected_checks.items() if stage in stages}
    seen: set[str] = set()
    check_records: dict[str, dict[str, Any]] = {}
    stage_checks: list[dict[str, Any]] = []
    for item in receipt["checks"]:
        check_id = item["check_id"]
        contracted_stages = expected_checks.get(check_id, optional_checks.get(check_id, ()))
        contracted_type = expected_types.get(check_id, optional_types.get(check_id))
        if check_id in seen or stage not in contracted_stages:
            raise CmtkError(
                "ADAPTER-EVIDENCE-INVALID",
                "Receipt check is duplicated or not bound to the declared route stage.",
                details={"check_id": check_id, "stage": stage},
            )
        if item["evidence_type"] != contracted_type:
            raise CmtkError(
                "ADAPTER-EVIDENCE-INVALID",
                "Receipt evidence type does not match the required check contract.",
                details={"check_id": check_id, "expected": contracted_type},
            )
        observation_values: dict[str, list[Any]] = {}
        for observation in item["observations"]:
            observation_values.setdefault(observation["name"], []).append(observation["value"])
        acceptance_values = observation_values.get("acceptance", [])
        expected_acceptance = item["status"] == "PASS"
        if (
            len(acceptance_values) != 1
            or not isinstance(acceptance_values[0], bool)
            or acceptance_values[0] is not expected_acceptance
        ):
            raise CmtkError(
                "ADAPTER-EVIDENCE-INVALID",
                "Receipt check status must match one explicit boolean acceptance observation.",
                details={"check_id": check_id, "status": item["status"]},
            )
        if item["status"] == "PASS" and check_id in optional_checks:
            required_observations = (
                {"detect", "evidence", "plan", "apply", "verify", "rollback"}
                if check_id == "repair_contract_complete"
                else {"functional_baseline", "protected_properties_unchanged", "rollback"}
            )
            if any(
                len(observation_values.get(name, [])) != 1 or observation_values[name][0] is not True
                for name in required_observations
            ):
                raise CmtkError(
                    "ADAPTER-EVIDENCE-INVALID",
                    "Optional repair or optimization PASS lacks its complete safety observations.",
                    details={"check_id": check_id, "required_observations": sorted(required_observations)},
                )
        seen.add(check_id)
        public_path = f"{evidence_prefix}/checks/{check_id}.json"
        record = {
            "schema_version": "1.1.0",
            "run_id": receipt["run_id"],
            "route": route,
            "stage": stage,
            "check_id": check_id,
            "status": item["status"],
            "evidence_type": item["evidence_type"],
            "summary": item["summary"],
            "observations": item["observations"],
        }
        _validate(record, "check-evidence", "ADAPTER-EVIDENCE-INVALID", "Check evidence")
        check_records[check_id] = record
        stage_checks.append(
            check(
                check_id,
                item["status"],
                item["summary"],
                category="acceptance",
                confidence="sampled" if item["evidence_type"] == "runtime-measurement" else "deterministic",
                evidence=[public_path],
                source=receipt["operation"]["collector"],
            )
        )

    missing_checks = sorted(required_for_stage - seen)
    if missing_checks:
        raise CmtkError(
            "ADAPTER-EVIDENCE-INVALID",
            "Receipt is missing required checks for the declared route stage.",
            details={"stage": stage, "missing_check_ids": missing_checks},
        )

    inputs = [
        {"kind": "route-plan", "sha256": receipt["plan_sha256"]},
        *[
            _safe_file_record(item, allowed_roots, terms, label="Receipt input")
            for item in receipt["inputs"]
        ],
    ]
    artifacts = [
        _safe_file_record(
            item,
            allowed_roots,
            terms,
            label="Receipt artifact",
            allowed_kinds={"supporting"},
        )
        for item in receipt["artifacts"]
    ]
    rollback = dict(receipt["rollback"])
    backup = rollback.get("backup_manifest")
    if backup is not None:
        rollback["backup_manifest"] = _safe_file_record(
            backup,
            allowed_roots,
            terms,
            label="Backup manifest",
            allowed_kinds={"supporting"},
        )
    public_paths = [
        f"{evidence_prefix}/stage-result.json",
        *[item["path"] for item in inputs if "path" in item],
        *[item["path"] for item in artifacts],
        *[f"{evidence_prefix}/checks/{check_id}.json" for check_id in check_records],
    ]
    if isinstance(rollback.get("backup_manifest"), dict):
        public_paths.append(rollback["backup_manifest"]["path"])
    if len(public_paths) != len(set(public_paths)):
        raise CmtkError(
            "ADAPTER-EVIDENCE-INVALID",
            "Stage result, receipt input, artifact, backup and check public paths must be unique.",
        )
    result = stage_result(
        run_id=receipt["run_id"],
        route=route,
        stage=stage,
        checks=stage_checks,
        execution_type=step["type"],
        execution_context=receipt["execution_context"],
        started_at=receipt["recorded_at"],
        finished_at=receipt["recorded_at"],
        actions=receipt["actions"],
        inputs=inputs,
        changes=receipt["changes"],
        artifacts=artifacts,
        metrics=receipt["metrics"],
        rollback=rollback,
        next_allowed_stages=next_stages if all(item["status"] == "PASS" for item in receipt["checks"]) else [],
    )
    _validate(result, "stage-result", "ADAPTER-EVIDENCE-INVALID", "Stage result")
    for label, payload in [("Stage result", result), *[("Check evidence", value) for value in check_records.values()]]:
        _require_public_safe(render_json(payload), terms, label=label)
    return result, check_records


def _write_bundle(
    output_dir: Path,
    stage: dict[str, Any],
    checks: dict[str, dict[str, Any]],
) -> None:
    if output_dir.exists():
        raise CmtkError("OUTPUT-TARGET-EXISTS", "Evidence output directory already exists.")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.", dir=output_dir.parent))
    try:
        for check_id, payload in checks.items():
            write_json_atomic(temporary / "checks" / f"{check_id}.json", payload)
        write_json_atomic(temporary / "stage-result.json", stage)
        os.rename(temporary, output_dir)
    except (CmtkError, OSError) as error:
        shutil.rmtree(temporary, ignore_errors=True)
        if isinstance(error, CmtkError):
            raise
        raise CmtkError("OUTPUT-WRITE-FAILED", "Unable to publish the evidence bundle atomically.") from error


def record_stage_evidence(
    workspace: dict[str, Any],
    plan: dict[str, Any],
    receipt: dict[str, Any],
    *,
    output_dir: str,
    evidence_prefix: str,
    sensitive_terms_path: str,
) -> dict[str, Any]:
    """Validate and atomically record one receipt from its required execution context."""

    _validate(receipt, "adapter-receipt", "ADAPTER-RECEIPT-INVALID", "Adapter receipt")
    _require_utc_timestamp(receipt["recorded_at"], label="Receipt recorded_at")
    if receipt["execution_context"] not in _EXTERNAL_CONTEXTS:
        raise CmtkError("ADAPTER-RECEIPT-INVALID", "Host-only receipts cannot create external-stage evidence.")
    verify_plan(plan, expected_sha256=receipt["plan_sha256"])
    verify_workspace_fingerprint(plan, workspace)
    verify_input_fingerprints(plan, workspace["execution"]["allowed_roots"])
    if receipt["route"] != workspace["route"] or receipt["route"] != plan["route"]:
        raise CmtkError("ROUTE-CONFLICT", "Receipt, plan and workspace must declare the same route.")
    step, next_stages = _find_step(plan, receipt)
    _verify_environment(workspace, receipt)
    _verify_operation(step, receipt)

    allowed_roots = workspace["execution"]["allowed_roots"]
    terms = _sensitive_terms(sensitive_terms_path, allowed_roots)
    prefix = _repository_relative(evidence_prefix.rstrip("/"), label="Evidence prefix")
    artifact_root = require_within_roots(workspace["execution"]["artifact_root"], allowed_roots)
    destination = require_within_roots(output_dir, [artifact_root])
    stage, checks = _build_records(
        receipt,
        step,
        next_stages,
        allowed_roots,
        prefix,
        terms,
    )
    _write_bundle(destination, stage, checks)
    return stage
