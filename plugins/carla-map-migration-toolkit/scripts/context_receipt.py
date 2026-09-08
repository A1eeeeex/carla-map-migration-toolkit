#!/usr/bin/env python3
"""Finalize an adapter receipt inside Unreal, CARLA client, or shell context.

This file intentionally uses only Python 3.7-compatible syntax and the standard
library so the host-side Python 3.10 package is not imported into old Unreal
embedded runtimes. It never executes a migration, build, repair, or optimization.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

CONTEXTS = {
    "source-unreal-python",
    "ue427-unreal-python",
    "carla-client-python",
    "shell-build",
}
VERSION_TRIPLET = re.compile(r"\d+\.\d+\.\d+")


class BoundaryError(RuntimeError):
    def __init__(self, reason_code, message):
        RuntimeError.__init__(self, message)
        self.reason_code = reason_code
        self.message = message


def _load_object(path, label):
    try:
        with Path(path).open("r", encoding="utf-8") as source:
            value = json.load(source)
    except (OSError, ValueError) as error:
        raise BoundaryError("ADAPTER-RECEIPT-INVALID", "%s is not readable JSON: %s" % (label, error))
    if not isinstance(value, dict):
        raise BoundaryError("ADAPTER-RECEIPT-INVALID", "%s must be a JSON object." % label)
    return value


def _canonical_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256_json(value):
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        while True:
            chunk = source.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_path(value):
    text = str(value).strip()
    if not text or text == "~" or text.startswith("~/") or "$" in text or "%" in text:
        raise BoundaryError("PATH-TARGET-AMBIGUOUS", "Receipt path is empty, home-relative, or unresolved.")
    path = Path(text)
    if not path.is_absolute():
        path = Path.cwd() / path
    resolved = path.resolve()
    if resolved == Path(resolved.anchor):
        raise BoundaryError("PATH-TARGET-AMBIGUOUS", "Filesystem roots are not accepted.")
    return resolved


def _within(path, roots):
    resolved = _canonical_path(path)
    for root_value in roots:
        root = _canonical_path(root_value)
        try:
            resolved.relative_to(root)
            return resolved
        except ValueError:
            pass
    raise BoundaryError("PATH-OUTSIDE-ALLOWED-ROOT", "Receipt path is outside every allowed root.")


def _require_equal(label, actual, expected):
    if not isinstance(actual, str) or not actual or actual != expected:
        raise BoundaryError("ADAPTER-ENVIRONMENT-MISMATCH", "%s does not match the workspace." % label)


def _triplet(value):
    match = VERSION_TRIPLET.search(value or "")
    return match.group(0) if match else None


def _verify_plan(workspace, plan, receipt):
    recorded = plan.get("plan_sha256")
    unsigned = dict(plan)
    unsigned.pop("plan_sha256", None)
    actual = _sha256_json(unsigned)
    if recorded != actual or receipt.get("plan_sha256") != actual:
        raise BoundaryError("PLAN-HASH-MISMATCH", "Route plan hash does not match the receipt.")
    if plan.get("workspace_sha256") != _sha256_json(workspace):
        raise BoundaryError("PLAN-STALE", "Workspace changed after the route plan was sealed.")
    if receipt.get("route") != workspace.get("route") or receipt.get("route") != plan.get("route"):
        raise BoundaryError("ROUTE-CONFLICT", "Receipt, workspace, and plan routes differ.")
    steps = [step for step in plan.get("steps", []) if step.get("step_id") == receipt.get("stage")]
    if len(steps) != 1 or steps[0].get("execution_context") != receipt.get("execution_context"):
        raise BoundaryError("ENV-EXECUTION-CONTEXT-MISMATCH", "Receipt stage/context does not match the plan.")
    for fingerprint in plan.get("input_fingerprints", []):
        path = _within(fingerprint.get("path", ""), workspace["execution"]["allowed_roots"])
        if not path.is_file() or path.is_symlink():
            raise BoundaryError("PLAN-STALE", "A planned input is absent or is a symbolic link.")
        if path.stat().st_size != fingerprint.get("size_bytes") or _sha256_file(path) != fingerprint.get("sha256"):
            raise BoundaryError("PLAN-STALE", "A planned input changed after the plan was sealed.")


def _verify_declared_environment(workspace, receipt):
    context = receipt["execution_context"]
    environment = receipt.get("environment", {})
    source = workspace["source_carla"]
    if context == "source-unreal-python":
        _require_equal("Execution platform", environment.get("platform"), source["platform"])
        _require_equal("Source CARLA version", environment.get("source_carla_version"), source["version"])
        _require_equal("Source Unreal version", environment.get("source_ue_version"), source["engine_version"])
        return source["engine_version"]
    if context == "ue427-unreal-python":
        _require_equal("Execution platform", environment.get("platform"), source["platform"])
        _require_equal(
            "Target Unreal version",
            environment.get("target_ue_version"),
            workspace["ue427"]["engine_version"],
        )
        return workspace["ue427"]["engine_version"]
    expected = (
        workspace["package_carla"]["version"]
        if receipt["route"] == "source-carla-to-package-carla"
        else source["version"]
    )
    if context == "carla-client-python":
        expected_platform = (
            workspace["package_carla"]["platform"]
            if receipt["route"] == "source-carla-to-package-carla"
            else source["platform"]
        )
        _require_equal("Execution platform", environment.get("platform"), expected_platform)
        _require_equal("CARLA client version", environment.get("carla_client_version"), expected)
        _require_equal("CARLA server version", environment.get("carla_server_version"), expected)
        return expected
    operation = receipt.get("operation", {})
    if "command_sha256" not in operation or "return_code" not in operation:
        raise BoundaryError("ADAPTER-EVIDENCE-INVALID", "Shell receipt lacks command hash or return code.")
    if any(item.get("status") == "PASS" for item in receipt.get("checks", [])) and operation["return_code"] != 0:
        raise BoundaryError("ADAPTER-EVIDENCE-INVALID", "Non-zero shell return code cannot support PASS.")
    _require_equal("Source CARLA version", environment.get("source_carla_version"), source["version"])
    _require_equal("Execution platform", environment.get("platform"), workspace["package_carla"]["platform"])
    _require_equal(
        "Target CARLA version",
        environment.get("target_carla_version"),
        workspace["package_carla"]["version"],
    )
    return expected


def _observe_api(receipt, configured_version):
    context = receipt["execution_context"]
    environment = receipt["environment"]
    if context in {"source-unreal-python", "ue427-unreal-python"}:
        try:
            import unreal

            actual = str(unreal.SystemLibrary.get_engine_version())
        except (ImportError, AttributeError, RuntimeError) as error:
            raise BoundaryError("ADAPTER-API-UNAVAILABLE", "Unreal Python API probe failed: %s" % error)
        _require_equal("Runtime Unreal version", environment.get("runtime_engine_version"), actual)
        if _triplet(actual) != _triplet(configured_version):
            raise BoundaryError(
                "ADAPTER-ENVIRONMENT-MISMATCH",
                "Runtime Unreal engine line differs from the workspace.",
            )
        return actual
    if context == "carla-client-python":
        try:
            import carla

            client = carla.Client
        except (ImportError, AttributeError) as error:
            raise BoundaryError("ADAPTER-API-UNAVAILABLE", "CARLA Python API probe failed: %s" % error)
        if client is None:
            raise BoundaryError("ADAPTER-API-UNAVAILABLE", "CARLA Client class is unavailable.")
        return "carla-client-server-%s" % configured_version
    return "shell-build-command-receipt"


def _finalize(workspace, plan, receipt):
    required = {
        "schema_version",
        "run_id",
        "route",
        "stage",
        "execution_context",
        "plan_sha256",
        "recorded_at",
        "environment",
        "operation",
        "inputs",
        "actions",
        "changes",
        "checks",
        "metrics",
        "artifacts",
        "rollback",
    }
    if receipt.get("schema_version") != "1.0.0" or not required.issubset(receipt) or "boundary" in receipt:
        raise BoundaryError("ADAPTER-RECEIPT-INVALID", "Receipt draft is incomplete, stale, or already finalized.")
    context = receipt.get("execution_context")
    actual_context = os.environ.get("CMTK_EXECUTION_CONTEXT", "host-cpython")
    if context not in CONTEXTS or actual_context != context:
        raise BoundaryError(
            "ENV-EXECUTION-CONTEXT-MISMATCH",
            "Receipt must be finalized in its declared execution context.",
        )
    _verify_plan(workspace, plan, receipt)
    configured_version = _verify_declared_environment(workspace, receipt)
    observed = _observe_api(receipt, configured_version)
    finalized = dict(receipt)
    finalized["boundary"] = {
        "schema_version": "1.0.0",
        "adapter": "cmtk-context-receipt",
        "adapter_sha256": _sha256_file(Path(__file__).resolve()),
        "draft_sha256": _sha256_json(receipt),
        "observed_context": context,
        "observed_api_version": observed,
        "finalized_at": (
            datetime.datetime.now(datetime.timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        ),
    }
    return finalized


def _write_atomic(path, value, roots):
    destination = _within(path, roots)
    if destination.exists():
        raise BoundaryError("OUTPUT-TARGET-EXISTS", "Finalized receipt output already exists.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=".%s." % destination.name, dir=str(destination.parent))
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            json.dump(value, output, ensure_ascii=False, indent=2, sort_keys=True)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.link(temporary_name, str(destination))
    except OSError as error:
        raise BoundaryError("OUTPUT-WRITE-FAILED", "Unable to write finalized receipt: %s" % error)
    finally:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass


def _parser():
    parser = argparse.ArgumentParser(description="Finalize a CMTK receipt in its external execution context.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--receipt-draft", required=True)
    parser.add_argument("--output", required=True)
    return parser


def finalize_receipt(config_path, plan_path, receipt_draft_path, output_path):
    """Finalize and persist one receipt from an already-running context."""
    workspace = _load_object(config_path, "Workspace")
    plan = _load_object(plan_path, "Route plan")
    receipt = _load_object(receipt_draft_path, "Receipt draft")
    finalized = _finalize(workspace, plan, receipt)
    _write_atomic(output_path, finalized, [workspace["execution"]["artifact_root"]])
    return finalized


def main():
    try:
        args = _parser().parse_args()
        finalized = finalize_receipt(args.config, args.plan, args.receipt_draft, args.output)
        sys.stdout.write(json.dumps(finalized, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        return 0
    except BoundaryError as error:
        sys.stdout.write(
            json.dumps(
                {
                    "schema_version": "1.0.0",
                    "status": "BLOCKED",
                    "reason_code": error.reason_code,
                    "message": error.message,
                    "details": {},
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
