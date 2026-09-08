from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path, PurePosixPath
from typing import Any

import jsonschema

from cmtk.core.errors import CmtkError
from cmtk.core.hashing import sha256_bytes, sha256_json
from cmtk.core.paths import require_within_roots
from cmtk.core.redaction import redact_text
from cmtk.routes.catalog import REQUIRED_CHECK_STAGES, ROUTES, STEP_CATALOG

_CHECK_STATUSES = {"PASS", "WARN", "FAIL", "NOT_RUN", "NOT_APPLICABLE", "BLOCKED"}
_ROUTE_STAGE_CONTEXTS = {
    route: {
        f"{ROUTES[route]['prefix']}.{suffix}": context
        for suffix, _step_type, context, _risk in steps
    }
    for route, steps in STEP_CATALOG.items()
}


def aggregate_required_checks(checks: list[dict[str, Any]]) -> str:
    if not checks:
        return "INCOMPLETE"
    statuses = [check.get("status") for check in checks]
    unknown = sorted({status for status in statuses if status not in _CHECK_STATUSES}, key=str)
    if unknown:
        raise CmtkError("STATUS-INVALID", "Unknown required-check status.", details={"values": unknown})
    if "FAIL" in statuses:
        return "FAIL"
    if "BLOCKED" in statuses:
        return "BLOCKED"
    if "NOT_RUN" in statuses or "NOT_APPLICABLE" in statuses:
        return "INCOMPLETE"
    if "WARN" in statuses:
        return "PASS_WITH_WARNINGS"
    return "PASS"


def _verified_reference_error(message: str, **details: Any) -> CmtkError:
    return CmtkError("EVIDENCE-REFERENCE-INVALID", message, details=details)


def _verified_record_error(message: str, **details: Any) -> CmtkError:
    return CmtkError("EVIDENCE-RECORD-INVALID", message, details=details)


def _is_repository_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and path.as_posix() == value


def _require_repository_relative_path(value: Any, *, field: str) -> str:
    if not _is_repository_relative_path(value):
        raise _verified_record_error(
            "Verified evidence paths must be normalized repository-relative POSIX paths.",
            field=field,
            value=value,
        )
    return value


def _read_evidence_bytes(path: Path, *, evidence_path: str, artifact: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError as error:
        raise _verified_record_error(
            "Verified evidence file cannot be read.",
            evidence_path=evidence_path,
            artifact=artifact,
        ) from error


def _load_structured_evidence(content: bytes, *, evidence_path: str, artifact: str) -> dict[str, Any]:
    try:
        payload = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise _verified_record_error(
            "Verified Run structured artifact is not valid JSON.",
            evidence_path=evidence_path,
            artifact=artifact,
        ) from error
    if not isinstance(payload, dict):
        raise _verified_record_error(
            "Verified Run structured artifact must be a JSON object.",
            evidence_path=evidence_path,
            artifact=artifact,
        )
    return payload


def _validate_record(
    path: str,
    record: dict[str, Any],
    schema: dict[str, Any],
    artifact_schemas: dict[str, dict[str, Any]],
    evidence_root: str | Path,
    sensitive_terms: tuple[str, ...],
) -> None:
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(record), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        raise _verified_record_error(
            "Verified Run does not satisfy its schema.",
            evidence_path=path,
            schema_path=list(first.schema_path),
            validation_message=first.message,
        )

    root = Path(evidence_root).resolve()
    relative_record_path = _require_repository_relative_path(path, field="verified_record")
    record_path = require_within_roots(root / relative_record_path, [root])
    if not record_path.is_file():
        raise _verified_record_error("Verified Run path does not exist.", evidence_path=path)
    record_content = _read_evidence_bytes(record_path, evidence_path=path, artifact=path)
    persisted_record = _load_structured_evidence(record_content, evidence_path=path, artifact=path)
    if persisted_record != record:
        raise _verified_record_error(
            "Loaded Verified Run does not match the record at its evidence path.",
            evidence_path=path,
        )
    if record.get("status") != "PASS":
        return

    artifacts = record["artifacts"]
    for artifact in artifacts:
        _require_repository_relative_path(artifact["path"], field="artifact")
    artifacts_by_path = {artifact["path"]: artifact for artifact in artifacts}
    if len(artifacts_by_path) != len(artifacts):
        raise _verified_record_error("Verified Run artifact paths must be unique.", evidence_path=path)
    inputs = record["input_hashes"]
    for input_record in inputs:
        _require_repository_relative_path(input_record["path"], field="input_hash")
    inputs_by_path = {item["path"]: item for item in inputs}
    if len(inputs_by_path) != len(inputs):
        raise _verified_record_error("Verified Run input paths must be unique.", evidence_path=path)
    overlapping_paths = sorted(inputs_by_path.keys() & artifacts_by_path.keys())
    if overlapping_paths:
        raise _verified_record_error(
            "Verified Run inputs and artifacts must use distinct paths.",
            evidence_path=path,
            overlapping=overlapping_paths,
        )
    referenced_paths = set(record["stage_results"])
    referenced_paths.add(record["redaction"]["report"])
    for check in record["required_checks"]:
        referenced_paths.update(check["evidence"])
    missing_references = sorted(referenced_paths - artifacts_by_path.keys())
    if missing_references:
        raise _verified_record_error(
            "Verified Run references evidence outside its artifact manifest.",
            evidence_path=path,
            missing=missing_references,
        )
    bundle_root = record_path.parent
    evidence_contents: dict[str, bytes] = {}
    for input_record in inputs:
        input_path = require_within_roots(root / input_record["path"], [bundle_root])
        content = _read_evidence_bytes(input_path, evidence_path=path, artifact=input_record["path"])
        if sha256_bytes(content) != input_record["sha256"]:
            raise _verified_record_error(
                "Verified Run input is missing or its SHA-256 does not match.",
                evidence_path=path,
                artifact=input_record["path"],
            )
        evidence_contents[input_record["path"]] = content
    artifact_payloads: dict[str, dict[str, Any]] = {}
    for artifact in artifacts:
        artifact_path = require_within_roots(root / artifact["path"], [bundle_root])
        content = _read_evidence_bytes(artifact_path, evidence_path=path, artifact=artifact["path"])
        if sha256_bytes(content) != artifact["sha256"]:
            raise _verified_record_error(
                "Verified Run artifact is missing or its SHA-256 does not match.",
                evidence_path=path,
                artifact=artifact["path"],
            )
        evidence_contents[artifact["path"]] = content
        kind = artifact["kind"]
        if kind == "supporting":
            continue
        artifact_schema = artifact_schemas.get(kind)
        if artifact_schema is None:
            raise _verified_record_error(
                "Verified Run artifact kind has no validation schema.",
                evidence_path=path,
                artifact=artifact["path"],
                kind=kind,
            )
        payload = _load_structured_evidence(content, evidence_path=path, artifact=artifact["path"])
        artifact_errors = list(jsonschema.Draft202012Validator(artifact_schema).iter_errors(payload))
        if artifact_errors:
            raise _verified_record_error(
                "Verified Run structured artifact does not satisfy its schema.",
                evidence_path=path,
                artifact=artifact["path"],
                validation_message=artifact_errors[0].message,
            )
        if kind in {"stage-result", "check-evidence", "redaction-report"} and payload.get("run_id") != record["run_id"]:
            raise _verified_record_error(
                "Verified Run artifact belongs to a different run.",
                evidence_path=path,
                artifact=artifact["path"],
            )
        if kind in {"stage-result", "check-evidence", "validation-report"} and payload.get("route") != record["route"]:
            raise _verified_record_error(
                "Verified Run artifact belongs to a different route.",
                evidence_path=path,
                artifact=artifact["path"],
            )
        if kind == "stage-result" and payload.get("status") != "PASS":
            raise _verified_record_error("Referenced stage result is not PASS.", artifact=artifact["path"])
        if kind == "check-evidence" and payload.get("status") != "PASS":
            raise _verified_record_error("Referenced check evidence is not PASS.", artifact=artifact["path"])
        if kind == "stage-result":
            expected_context = _ROUTE_STAGE_CONTEXTS[record["route"]].get(payload.get("stage"))
            if expected_context is None or payload.get("execution_context") != expected_context:
                raise _verified_record_error(
                    "Referenced stage result is not a contract stage in its required context.",
                    evidence_path=path,
                    artifact=artifact["path"],
                    stage=payload.get("stage"),
                )
        if kind == "validation-report" and payload.get("overall_status") != "PASS":
            raise _verified_record_error("Referenced validation report is not PASS.", artifact=artifact["path"])
        if kind == "redaction-report" and payload.get("status") != "PASS":
            raise _verified_record_error("Referenced redaction report is not PASS.", artifact=artifact["path"])
        artifact_payloads[artifact["path"]] = payload

    declared_stage_results = record["stage_results"]
    typed_stage_results = {
        artifact_path
        for artifact_path, artifact in artifacts_by_path.items()
        if artifact.get("kind") == "stage-result"
    }
    if (
        len(declared_stage_results) != len(set(declared_stage_results))
        or set(declared_stage_results) != typed_stage_results
    ):
        raise _verified_record_error(
            "stage_results must exactly list the typed stage-result artifacts.",
            evidence_path=path,
        )
    redaction_path = record["redaction"]["report"]
    if artifacts_by_path.get(redaction_path, {}).get("kind") != "redaction-report":
        raise _verified_record_error(
            "Redaction report must reference a typed redaction-report artifact.",
            evidence_path=path,
            artifact=redaction_path,
        )
    redaction_payload = artifact_payloads[redaction_path]
    scanned_records = redaction_payload["scanned_artifacts"]
    scanned_by_path = {item["path"]: item["sha256"] for item in scanned_records}
    expected_scanned = {
        **{item["path"]: item["sha256"] for item in inputs},
        **{
            item["path"]: item["sha256"]
            for item in artifacts
            if item["path"] != redaction_path
        },
    }
    if len(scanned_by_path) != len(scanned_records) or scanned_by_path != expected_scanned:
        raise _verified_record_error(
            "Redaction report does not cover the exact input and artifact manifest.",
            evidence_path=path,
            artifact=redaction_path,
        )
    if (
        not sensitive_terms
        or redaction_payload["sensitive_terms_count"] != len(sensitive_terms)
        or redaction_payload["sensitive_terms_sha256"] != sha256_json(list(sensitive_terms))
    ):
        raise _verified_record_error(
            "Redaction report does not match the supplied private sensitive-term set.",
            evidence_path=path,
            artifact=redaction_path,
        )
    scan_contents = {**evidence_contents, path: record_content}
    for scanned_path, content in scan_contents.items():
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as error:
            raise _verified_record_error(
                "Public Verified Run evidence must be UTF-8 text.",
                evidence_path=path,
                artifact=scanned_path,
            ) from error
        if redact_text(text, sensitive_terms=sensitive_terms) != text:
            raise _verified_record_error(
                "Redaction scan found an unredacted sensitive value.",
                evidence_path=path,
                artifact=scanned_path,
            )
    for check in record["required_checks"]:
        expected_stages = REQUIRED_CHECK_STAGES[record["route"]].get(check["id"])
        if expected_stages is None:
            raise _verified_record_error(
                "Required check has no stage contract.",
                evidence_path=path,
                check_id=check["id"],
            )
        matched = any(
            artifacts_by_path.get(evidence_path, {}).get("kind") == "stage-result"
            and artifact_payloads[evidence_path]["stage"] in expected_stages
            and any(
                stage_check.get("id") == check["id"]
                and stage_check.get("status") == "PASS"
                and isinstance(stage_check.get("evidence"), list)
                and bool(stage_check["evidence"])
                and all(
                    isinstance(proof_path, str)
                    and artifacts_by_path.get(proof_path, {}).get("kind") == "check-evidence"
                    and artifact_payloads[proof_path].get("check_id") == check["id"]
                    and artifact_payloads[proof_path].get("stage")
                    == artifact_payloads[evidence_path]["stage"]
                    and artifact_payloads[proof_path].get("status") == "PASS"
                    for proof_path in stage_check["evidence"]
                )
                for stage_check in artifact_payloads[evidence_path]["checks"]
            )
            for evidence_path in check["evidence"]
            if evidence_path in artifact_payloads
        )
        if not matched:
            raise _verified_record_error(
                "Required check has no matching PASS stage-result evidence.",
                evidence_path=path,
                check_id=check["id"],
            )
    signoff_sha256 = record["signoff"]["evidence_sha256"]
    if not any(
        artifact["sha256"] == signoff_sha256 and artifact["kind"] != "supporting"
        for artifact in artifacts
    ):
        raise _verified_record_error(
            "Signoff evidence SHA-256 is not present on a structured artifact.",
            evidence_path=path,
        )


def validate_verified_references(
    compatibility_matrix: dict[str, Any],
    claims_registry: dict[str, Any],
    verified_records: dict[str, dict[str, Any]],
    verified_run_schema: dict[str, Any],
    artifact_schemas: dict[str, dict[str, Any]],
    evidence_root: str | Path,
    sensitive_terms: Iterable[str] = (),
) -> None:
    """Cross-check public verified claims against loaded Verified Run records.

    ``verified_records`` maps the public repository-relative evidence path to
    the parsed ``verified-run.json`` at that path. Each record is schema-checked,
    compared with the persisted file and rehashed before referential integrity
    is evaluated. ``sensitive_terms`` must contain the private identifier set
    used by the redaction scan whenever a PASS record is present.
    """

    normalized_sensitive_terms = tuple(
        sorted({term.strip() for term in sensitive_terms if isinstance(term, str) and term.strip()})
    )
    records_by_id: dict[str, tuple[str, dict[str, Any]]] = {}
    for path, record in verified_records.items():
        run_id = record.get("run_id") if isinstance(record, dict) else None
        if not isinstance(path, str) or not path or not isinstance(run_id, str) or not run_id:
            raise _verified_reference_error("Verified Run index contains an invalid path or run ID.")
        if run_id in records_by_id:
            raise _verified_reference_error("Verified Run IDs must be unique.", run_id=run_id)
        _validate_record(
            path,
            record,
            verified_run_schema,
            artifact_schemas,
            evidence_root,
            normalized_sensitive_terms,
        )
        records_by_id[run_id] = (path, record)

    verified_statuses = {"maintainer-verified": "maintainer", "community-verified": "community"}
    for entry in compatibility_matrix.get("entries", []):
        status = entry.get("status")
        if status not in verified_statuses:
            continue
        run_id = entry.get("verified_run_id")
        indexed = records_by_id.get(run_id)
        if indexed is None:
            raise _verified_reference_error("Compatibility entry references a missing run.", run_id=run_id)
        path, record = indexed
        expected_owner = verified_statuses[status]
        environment_sha256 = sha256_json(record["environment"])
        environment = record["environment"]
        target_identity = record["target_identity"]
        route = record["route"]
        version_fields = {
            "roadrunner-to-source-carla": ("roadrunner_version", "source_carla_version"),
            "source-carla-to-package-carla": ("source_carla_version", "target_carla_version"),
            "source-carla-to-ue427": ("source_carla_version", "target_ue_version"),
        }
        source_field, target_field = version_fields[route]
        expected_engine = (
            f"{environment.get('source_ue_version')} to {environment.get('target_ue_version')}"
            if route == "source-carla-to-ue427"
            else environment.get("source_ue_version")
        )
        stack_matches = (
            entry.get("source_version") == environment.get(source_field)
            and entry.get("target_version") == environment.get(target_field)
            and entry.get("platform") == environment.get("platform")
            and entry.get("map_mode") == target_identity.get("map_mode")
            and entry.get("engine") == expected_engine
        )
        if route == "roadrunner-to-source-carla":
            stack_matches = stack_matches and entry.get("roadrunner") == environment.get("roadrunner_version")
            identity_matches = target_identity.get("engine_version") == environment.get("source_ue_version")
        elif route == "source-carla-to-package-carla":
            identity_matches = target_identity.get("package_version") == environment.get("target_carla_version")
        else:
            identity_matches = target_identity.get("engine_version") == environment.get("target_ue_version")
        if (
            entry.get("evidence_path") != path
            or record.get("status") != "PASS"
            or record.get("verification_owner") != expected_owner
            or record.get("route") != entry.get("route")
            or record.get("toolkit_version") != entry.get("toolkit_version")
            or entry.get("environment_sha256") != environment_sha256
            or not stack_matches
            or not identity_matches
        ):
            raise _verified_reference_error(
                "Compatibility entry does not match its Verified Run.",
                run_id=run_id,
                evidence_path=path,
            )
        bundle = entry.get("evidence_bundle")
        if (
            not _is_repository_relative_path(bundle)
            or not _is_repository_relative_path(path)
            or PurePosixPath(path).parent != PurePosixPath(bundle)
        ):
            raise _verified_reference_error("Verified Run is outside the declared evidence bundle.", run_id=run_id)

    for claim in claims_registry.get("claims", []):
        status = claim.get("status")
        if status not in verified_statuses:
            continue
        if not claim.get("supported_stacks"):
            raise _verified_reference_error("Verified claim has no supported stack.", claim_id=claim.get("id"))
        run_ids = claim.get("verified_runs")
        if not isinstance(run_ids, list) or not run_ids:
            raise _verified_reference_error("Verified claim has no Verified Run.", claim_id=claim.get("id"))
        stack_run_ids = [stack.get("run_id") for stack in claim["supported_stacks"]]
        if (
            len(run_ids) != len(set(run_ids))
            or len(stack_run_ids) != len(set(stack_run_ids))
            or set(stack_run_ids) != set(run_ids)
        ):
            raise _verified_reference_error(
                "Verified claim stacks must map exactly to its Verified Runs.",
                claim_id=claim.get("id"),
            )
        for run_id in run_ids:
            indexed = records_by_id.get(run_id)
            if indexed is None:
                raise _verified_reference_error(
                    "Claim references a missing run.",
                    claim_id=claim.get("id"),
                    run_id=run_id,
                )
            _, record = indexed
            environment_sha256 = sha256_json(record["environment"])
            matching_stack = any(
                stack.get("run_id") == run_id and stack.get("environment_sha256") == environment_sha256
                for stack in claim["supported_stacks"]
            )
            levels = ["L0", "L1", "L2", "L3", "L4", "L5"]
            required_level = claim.get("required_evidence_level")
            if (
                record.get("status") != "PASS"
                or record.get("verification_owner") != verified_statuses[status]
                or record.get("route") != claim.get("route")
                or claim.get("id") not in record.get("claims_evaluated", [])
                or not matching_stack
                or required_level not in levels
                or levels.index(record.get("evidence_level")) < levels.index(required_level)
            ):
                raise _verified_reference_error(
                    "Claim does not match its Verified Run.",
                    claim_id=claim.get("id"),
                    run_id=run_id,
                )
