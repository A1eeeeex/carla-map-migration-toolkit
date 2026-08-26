from __future__ import annotations

import argparse
import sys
from typing import Any

from cmtk.core.archive import inspect_archive
from cmtk.core.context import require_context
from cmtk.core.errors import CmtkError
from cmtk.core.jsonio import load_json, render_json, write_json_atomic
from cmtk.core.paths import require_within_roots
from cmtk.core.plans import verify_input_fingerprints, verify_plan, verify_workspace_fingerprint
from cmtk.core.workspace import validate_workspace_shape
from cmtk.optimization.comparison import compare_snapshots
from cmtk.routes.catalog import ROUTES
from cmtk.routes.inspection import inspect_workspace
from cmtk.routes.planning import build_plan
from cmtk.validation.reporting import pending_validation_report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cmtk", description="Guarded host core for CARLA map migration evidence.")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("inspect", "plan", "validate"):
        command = sub.add_parser(name)
        command.add_argument("--route", required=True, choices=sorted(ROUTES))
        command.add_argument("--config", required=True)
        if name in {"plan", "validate"}:
            command.add_argument("--output")

    verify = sub.add_parser("verify-plan")
    verify.add_argument("--config", required=True)
    verify.add_argument("--plan", required=True)
    verify.add_argument("--plan-sha256", required=True)

    archive = sub.add_parser("archive-audit")
    archive.add_argument("--archive", required=True)
    archive.add_argument("--allowed-root")
    archive.add_argument("--require", action="append", default=[])
    archive.add_argument("--maximum-expanded-bytes", type=int, default=20 * 1024 * 1024 * 1024)

    performance = sub.add_parser("compare-performance")
    performance.add_argument("--baseline", required=True)
    performance.add_argument("--candidate", required=True)
    performance.add_argument("--output")
    performance.add_argument("--allowed-root")
    return parser


def _emit(payload: dict[str, Any], *, output: str | None = None) -> int:
    if output:
        write_json_atomic(output, payload)
    sys.stdout.write(render_json(payload))
    status = payload.get("status", payload.get("overall_status"))
    if status is None and payload.get("blocked_reasons"):
        status = "BLOCKED"
    return 2 if status in {"FAIL", "BLOCKED"} else (3 if status == "NOT_RUN" else 0)


def _load_workspace(path: str, route: str | None = None) -> dict[str, Any]:
    value = load_json(path)
    if not isinstance(value, dict):
        raise CmtkError("WORKSPACE-INVALID", "Workspace JSON must be an object.")
    validate_workspace_shape(value, route)
    return value


def _load_object(path: str, reason_code: str, label: str) -> dict[str, Any]:
    value = load_json(path)
    if not isinstance(value, dict):
        raise CmtkError(reason_code, f"{label} JSON must be an object.")
    return value


def _artifact_output(workspace: dict[str, Any], output: str) -> str:
    execution = workspace["execution"]
    artifact_root = require_within_roots(execution["artifact_root"], execution["allowed_roots"])
    return str(require_within_roots(output, [artifact_root]))


def run(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    require_context("host-cpython")
    if args.command == "inspect":
        workspace = _load_workspace(args.config, args.route)
        return _emit(inspect_workspace(workspace, args.route))
    if args.command == "plan":
        workspace = _load_workspace(args.config, args.route)
        inspection = inspect_workspace(workspace, args.route)
        plan = build_plan(workspace, args.route, inspection)
        if args.output:
            args.output = _artifact_output(workspace, args.output)
        return _emit(plan, output=args.output)
    if args.command == "validate":
        workspace = _load_workspace(args.config, args.route)
        inspection = inspect_workspace(workspace, args.route)
        if inspection["status"] in {"FAIL", "BLOCKED"}:
            return _emit(inspection)
        report = pending_validation_report(workspace, args.route)
        if args.output:
            args.output = _artifact_output(workspace, args.output)
        return _emit(report, output=args.output)
    if args.command == "verify-plan":
        workspace = _load_workspace(args.config)
        plan = _load_object(args.plan, "PLAN-INVALID", "Route plan")
        verify_plan(plan, expected_sha256=args.plan_sha256)
        verify_workspace_fingerprint(plan, workspace)
        verify_input_fingerprints(plan, workspace["execution"]["allowed_roots"])
        return _emit({"schema_version": "1.0.0", "status": "PASS", "plan_sha256": plan["plan_sha256"]})
    if args.command == "archive-audit":
        if not args.allowed_root:
            raise CmtkError(
                "ARCHIVE-ALLOWED-ROOT-REQUIRED",
                "Archive inspection requires an explicit allowed root.",
            )
        archive_path = require_within_roots(args.archive, [args.allowed_root])
        return _emit(
            inspect_archive(
                archive_path, required_patterns=args.require, maximum_expanded_bytes=args.maximum_expanded_bytes
            )
        )
    if args.command == "compare-performance":
        if not args.allowed_root:
            raise CmtkError(
                "OUTPUT-ALLOWED-ROOT-REQUIRED",
                "Performance inputs and output require an explicit allowed root.",
            )
        baseline_path = require_within_roots(args.baseline, [args.allowed_root])
        candidate_path = require_within_roots(args.candidate, [args.allowed_root])
        output = str(require_within_roots(args.output, [args.allowed_root])) if args.output else None
        result = compare_snapshots(
            _load_object(str(baseline_path), "PERF-INPUT-INVALID", "Baseline performance snapshot"),
            _load_object(str(candidate_path), "PERF-INPUT-INVALID", "Candidate performance snapshot"),
        )
        return _emit(result, output=output)
    raise CmtkError("COMMAND-UNKNOWN", "Unknown command.")


def main() -> None:
    try:
        raise SystemExit(run())
    except CmtkError as error:
        sys.stdout.write(render_json(error.as_dict()))
        raise SystemExit(2) from None
