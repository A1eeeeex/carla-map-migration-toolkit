from __future__ import annotations

import json

import jsonschema
import pytest
from cmtk.core.errors import CmtkError
from cmtk.core.hashing import sha256_file, sha256_json
from cmtk.validation.verified import validate_verified_references
from conftest import PLUGIN_ROOT, REPO_ROOT

CLAIM_DOCS = {
    "claims.md",
    "non-claims.md",
    "support-status.md",
    "acceptance-contracts.md",
    "proof-model.md",
    "claim-test-traceability.md",
}
SUPPORT_STATUSES = {
    "planned",
    "implemented",
    "maintainer-verified",
    "community-verified",
    "experimental",
    "unsupported",
    "unknown",
}
UE427_REQUIRED_CHECK_STAGES = {
    "source_asset_inventory_complete": "SRC2UE427.BASELINE",
    "dependency_classification_complete": "SRC2UE427.CLASSIFY_DEPS",
    "unreal_safe_migration": "SRC2UE427.MIGRATE_ASSETS",
    "target_engine_version_recorded": "SRC2UE427.CREATE_TARGET",
    "required_assets_present": "SRC2UE427.TARGET_VALIDATE",
    "missing_assets_zero": "SRC2UE427.TARGET_VALIDATE",
    "required_materials_valid": "SRC2UE427.TARGET_VALIDATE",
    "disallowed_carla_refs_zero": "SRC2UE427.CLEAN_REFS",
    "runtime_objects_have_strategy": "SRC2UE427.REPLACE_CARLA",
    "world_settings_environment_lighting": "SRC2UE427.REPAIR_WORLD",
    "road_collision_smoke": "SRC2UE427.TARGET_VALIDATE",
    "target_reopen": "SRC2UE427.TARGET_VALIDATE",
    "pie_smoke": "SRC2UE427.TARGET_VALIDATE",
    "second_clean_project_cold_copy": "SRC2UE427.COLD_COPY",
    "ue427_handoff_complete": "SRC2UE427.HANDOFF",
}
UE427_REQUIRED_CHECK_EVIDENCE_TYPES = {
    "source_asset_inventory_complete": "deterministic-output",
    "dependency_classification_complete": "deterministic-output",
    "unreal_safe_migration": "editor-audit",
    "target_engine_version_recorded": "editor-audit",
    "required_assets_present": "editor-audit",
    "missing_assets_zero": "editor-audit",
    "required_materials_valid": "editor-audit",
    "disallowed_carla_refs_zero": "editor-audit",
    "runtime_objects_have_strategy": "editor-audit",
    "world_settings_environment_lighting": "editor-audit",
    "road_collision_smoke": "runtime-measurement",
    "target_reopen": "editor-audit",
    "pie_smoke": "runtime-measurement",
    "second_clean_project_cold_copy": "portability-replay",
    "ue427_handoff_complete": "deterministic-output",
}
UE427_STAGE_CONTEXTS = {
    "SRC2UE427.BASELINE": "source-unreal-python",
    "SRC2UE427.CLASSIFY_DEPS": "host-cpython",
    "SRC2UE427.MIGRATE_ASSETS": "source-unreal-python",
    "SRC2UE427.CREATE_TARGET": "ue427-unreal-python",
    "SRC2UE427.TARGET_VALIDATE": "ue427-unreal-python",
    "SRC2UE427.CLEAN_REFS": "ue427-unreal-python",
    "SRC2UE427.REPLACE_CARLA": "ue427-unreal-python",
    "SRC2UE427.REPAIR_WORLD": "ue427-unreal-python",
    "SRC2UE427.COLD_COPY": "ue427-unreal-python",
    "SRC2UE427.HANDOFF": "host-cpython",
}


def _registry() -> dict:
    return json.loads((PLUGIN_ROOT / "examples" / "claims-registry.example.json").read_text(encoding="utf-8"))


def _verified_run_schema() -> dict:
    return json.loads((PLUGIN_ROOT / "schemas" / "verified-run.schema.json").read_text(encoding="utf-8"))


def _artifact_schemas() -> dict[str, dict]:
    return {
        kind: json.loads((PLUGIN_ROOT / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8"))
        for kind, name in {
            "stage-result": "stage-result",
            "check-evidence": "check-evidence",
            "validation-report": "validation-report",
            "redaction-report": "redaction-report",
        }.items()
    }


def _complete_source_to_ue427_run(
    stage_paths_by_check: dict[str, str],
    stage_hashes: dict[str, str],
    input_path: str,
    input_sha256: str,
    check_evidence_hashes: dict[str, str],
    redaction_path: str,
    redaction_sha256: str,
) -> dict:
    stage_paths = sorted(set(stage_paths_by_check.values()))
    return {
        "schema_version": "1.4.0",
        "run_id": "run-001",
        "route": "source-carla-to-ue427",
        "profile": "standalone-map",
        "toolkit_version": "0.1.0",
        "git_commit": "a" * 40,
        "status": "PASS",
        "evidence_level": "L5",
        "verification_owner": "maintainer",
        "started_at": "2026-08-26T00:00:00Z",
        "completed_at": "2026-08-26T00:00:01Z",
        "environment": {
            "host_os": "anonymous-linux",
            "platform": "linux-x86_64",
            "source_carla_version": "0.9.16",
            "source_ue_version": "4.26.2-carla-fork",
            "target_ue_version": "4.27.2",
        },
        "input_hashes": [{"path": input_path, "sha256": input_sha256}],
        "target_identity": {
            "engine_version": "4.27.2",
            "project_fingerprint": "anonymous-target",
            "map_mode": "standard",
        },
        "claims_evaluated": ["C-SRC-UE427-001"],
        "required_checks": [
            {
                "id": check_id,
                "required": True,
                "status": "PASS",
                "evidence": [stage_paths_by_check[check_id]],
            }
            for check_id in UE427_REQUIRED_CHECK_STAGES
        ],
        "optional_checks": [],
        "stage_results": stage_paths,
        "repair_summary": [],
        "protected_property_diff": {"status": "PASS"},
        "artifacts": [
            *[
                {"path": stage_path, "sha256": stage_hashes[stage_path], "kind": "stage-result"}
                for stage_path in stage_paths
            ],
            *[
                {"path": evidence_path, "sha256": evidence_sha256, "kind": "check-evidence"}
                for evidence_path, evidence_sha256 in sorted(check_evidence_hashes.items())
            ],
            {"path": redaction_path, "sha256": redaction_sha256, "kind": "redaction-report"},
        ],
        "known_limitations": [],
        "redaction": {"status": "PASS", "report": redaction_path},
        "signoff": {
            "runner": "maintainer",
            "reviewer": "reviewer",
            "date": "2026-08-26",
            "acceptance_contract_version": "1.1",
            "evidence_sha256": stage_hashes[stage_paths[0]],
        },
    }


def _stage_payload(stage: str, check_ids: list[str], evidence_paths_by_check: dict[str, str]) -> dict:
    return {
        "schema_version": "1.0.0",
        "run_id": "run-001",
        "route": "source-carla-to-ue427",
        "stage": stage,
        "status": "PASS",
        "execution_type": "MANUAL",
        "execution_context": UE427_STAGE_CONTEXTS[stage],
        "started_at": "2026-08-26T00:00:00Z",
        "finished_at": "2026-08-26T00:00:01Z",
        "inputs": [],
        "actions": [],
        "changes": [],
        "checks": [
            {
                "id": check_id,
                "category": "route-acceptance",
                "severity": "critical",
                "status": "PASS",
                "confidence": "manual",
                "message": "Anonymous acceptance evidence.",
                "evidence": [evidence_paths_by_check[check_id]],
                "remediation": [],
                "source": "anonymous-fixture",
            }
            for check_id in check_ids
        ],
        "metrics": [],
        "artifacts": [],
        "warnings": [],
        "failures": [],
        "rollback": {},
        "next_allowed_stages": [],
    }


def test_claim_registry_has_unique_ids_and_explicit_evidence_levels():
    registry = _registry()
    claims = registry["claims"]
    ids = [claim["id"] for claim in claims]
    assert len(ids) == len(set(ids))
    assert all(claim["required_evidence_level"] in {"L0", "L1", "L2", "L3", "L4", "L5"} for claim in claims)
    assert all(claim["status"] in SUPPORT_STATUSES for claim in claims)
    assert all("test_ids" in claim and "evidence_artifacts" in claim for claim in claims)


def test_claim_docs_exist_and_registry_ids_are_traceable():
    docs_root = REPO_ROOT / "docs"
    assert {path.name for path in docs_root.glob("*.md")} >= CLAIM_DOCS
    claims_text = (docs_root / "claims.md").read_text(encoding="utf-8")
    traceability_text = (docs_root / "claim-test-traceability.md").read_text(encoding="utf-8")
    for claim in _registry()["claims"]:
        assert claim["id"] in claims_text
        assert claim["id"] in traceability_text


def test_readme_avoids_unproven_marketing_claims():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8").casefold()
    forbidden = {
        "three verified migration workflows",
        "production-ready",
        "one-click migration",
        "fully automated migration",
        "universal carla compatibility",
    }
    assert not {phrase for phrase in forbidden if phrase in readme}


def test_maintainer_verified_compatibility_requires_verified_run_reference():
    schema = json.loads(
        (PLUGIN_ROOT / "schemas" / "compatibility-matrix.schema.json").read_text(encoding="utf-8")
    )
    example = json.loads(
        (PLUGIN_ROOT / "examples" / "compatibility-matrix.example.json").read_text(encoding="utf-8")
    )
    entry = example["entries"][0]
    entry.update(
        {
            "status": "maintainer-verified",
            "environment_sha256": "a" * 64,
            "evidence_bundle": "evidence/verified/source-to-ue427/run-001",
            "verified_run_id": "run-001",
            "evidence_path": "evidence/verified/source-to-ue427/run-001/verified-run.json",
            "verified_date": "2026-08-26",
            "verifier": "maintainer",
        }
    )
    jsonschema.validate(example, schema)

    entry["verified_run_id"] = None
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(example, schema)


def test_fabricated_verified_run_references_are_rejected():
    matrix = json.loads(
        (PLUGIN_ROOT / "examples" / "compatibility-matrix.example.json").read_text(encoding="utf-8")
    )
    registry = _registry()
    matrix["entries"][0].update(
        {
            "status": "maintainer-verified",
            "evidence_bundle": "evidence/verified/source-to-ue427/fabricated",
            "verified_run_id": "fabricated",
            "evidence_path": "evidence/verified/source-to-ue427/fabricated/verified-run.json",
            "verified_date": "2026-08-26",
            "verifier": "maintainer",
        }
    )
    registry["claims"][4].update(
        {
            "status": "maintainer-verified",
            "verified_runs": ["fabricated"],
            "supported_stacks": [{}],
        }
    )

    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix, registry, {}, _verified_run_schema(), _artifact_schemas(), REPO_ROOT
        )
    assert error.value.reason_code == "EVIDENCE-REFERENCE-INVALID"


def test_public_verified_references_are_cross_validated():
    matrix = json.loads(
        (PLUGIN_ROOT / "examples" / "compatibility-matrix.example.json").read_text(encoding="utf-8")
    )
    records = {
        str(path.relative_to(REPO_ROOT)): json.loads(path.read_text(encoding="utf-8"))
        for path in (REPO_ROOT / "evidence" / "verified").glob("**/verified-run.json")
    }
    validate_verified_references(
        matrix, _registry(), records, _verified_run_schema(), _artifact_schemas(), REPO_ROOT
    )


def test_schema_invalid_matching_verified_run_is_rejected():
    matrix = json.loads(
        (PLUGIN_ROOT / "examples" / "compatibility-matrix.example.json").read_text(encoding="utf-8")
    )
    registry = _registry()
    evidence_path = "evidence/verified/source-to-ue427/run-001/verified-run.json"
    matrix["entries"][0].update(
        {
            "status": "maintainer-verified",
            "environment_sha256": "a" * 64,
            "evidence_bundle": "evidence/verified/source-to-ue427/run-001",
            "verified_run_id": "run-001",
            "evidence_path": evidence_path,
            "verified_date": "2026-08-26",
            "verifier": "maintainer",
        }
    )
    claim = registry["claims"][4]
    claim.update(
        {
            "status": "maintainer-verified",
            "verified_runs": ["run-001"],
            "supported_stacks": [{"run_id": "run-001", "environment_sha256": "a" * 64}],
        }
    )
    record = {
        "run_id": "run-001",
        "route": "source-carla-to-ue427",
        "status": "PASS",
        "verification_owner": "maintainer",
        "toolkit_version": "0.1.0",
        "claims_evaluated": [claim["id"]],
    }

    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            REPO_ROOT,
        )
    assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"


def test_schema_valid_hashed_verified_run_references_are_accepted(tmp_path):
    matrix = json.loads(
        (PLUGIN_ROOT / "examples" / "compatibility-matrix.example.json").read_text(encoding="utf-8")
    )
    registry = _registry()
    bundle = "evidence/verified/source-to-ue427/run-001"
    sensitive_terms = ["anonymous-private-term"]
    evidence_path = f"{bundle}/verified-run.json"
    input_path = f"{bundle}/input-manifest.json"
    redaction_path = f"{bundle}/redaction-report.json"
    input_artifact = tmp_path / input_path
    redaction_artifact = tmp_path / redaction_path
    input_artifact.parent.mkdir(parents=True)
    input_artifact.write_text('{"input":"anonymous"}\n', encoding="utf-8")

    evidence_paths_by_check: dict[str, str] = {}
    check_evidence_hashes: dict[str, str] = {}
    for check_id, stage in UE427_REQUIRED_CHECK_STAGES.items():
        check_evidence_path = f"{bundle}/checks/{check_id}.json"
        check_evidence_artifact = tmp_path / check_evidence_path
        check_evidence_artifact.parent.mkdir(parents=True, exist_ok=True)
        check_evidence_artifact.write_text(
            json.dumps(
                {
                    "schema_version": "1.1.0",
                    "run_id": "run-001",
                    "route": "source-carla-to-ue427",
                    "stage": stage,
                    "check_id": check_id,
                    "status": "PASS",
                    "evidence_type": UE427_REQUIRED_CHECK_EVIDENCE_TYPES[check_id],
                    "summary": "Anonymous structured acceptance evidence.",
                    "observations": [
                        {"name": "acceptance", "value": True, "source": "anonymous-fixture"}
                    ],
                }
            ),
            encoding="utf-8",
        )
        evidence_paths_by_check[check_id] = check_evidence_path
        check_evidence_hashes[check_evidence_path] = sha256_file(check_evidence_artifact)

    check_ids_by_stage: dict[str, list[str]] = {}
    for check_id, stage in UE427_REQUIRED_CHECK_STAGES.items():
        check_ids_by_stage.setdefault(stage, []).append(check_id)
    stage_paths_by_check: dict[str, str] = {}
    stage_hashes: dict[str, str] = {}
    for stage, check_ids in check_ids_by_stage.items():
        stage_path = f"{bundle}/{stage.split('.', 1)[1].lower()}-stage.json"
        stage_artifact = tmp_path / stage_path
        stage_artifact.write_text(
            json.dumps(_stage_payload(stage, check_ids, evidence_paths_by_check)),
            encoding="utf-8",
        )
        stage_hashes[stage_path] = sha256_file(stage_artifact)
        for check_id in check_ids:
            stage_paths_by_check[check_id] = stage_path

    scanned_artifacts = [
        {"path": input_path, "sha256": sha256_file(input_artifact)},
        *[
            {"path": path, "sha256": value}
            for path, value in sorted(check_evidence_hashes.items())
        ],
        *[{"path": path, "sha256": value} for path, value in sorted(stage_hashes.items())],
    ]
    redaction_artifact.write_text(
        json.dumps(
            {
                "schema_version": "1.1.0",
                "run_id": "run-001",
                "status": "PASS",
                "scanner": "anonymous-fixture-scanner",
                "sensitive_terms_count": 1,
                "sensitive_terms_sha256": sha256_json(sensitive_terms),
                "scanned_artifacts": scanned_artifacts,
                "findings": [],
            }
        ),
        encoding="utf-8",
    )
    record = _complete_source_to_ue427_run(
        stage_paths_by_check,
        stage_hashes,
        input_path,
        sha256_file(input_artifact),
        check_evidence_hashes,
        redaction_path,
        sha256_file(redaction_artifact),
    )
    record_path = tmp_path / evidence_path
    record_path.write_text(json.dumps(record), encoding="utf-8")
    environment_sha256 = sha256_json(record["environment"])

    matrix["entries"][0].update(
        {
            "status": "maintainer-verified",
            "environment_sha256": environment_sha256,
            "evidence_bundle": bundle,
            "verified_run_id": "run-001",
            "evidence_path": evidence_path,
            "verified_date": "2026-08-26",
            "verifier": "maintainer",
        }
    )
    registry["claims"][4].update(
        {
            "status": "maintainer-verified",
            "verified_runs": ["run-001"],
            "supported_stacks": [
                {"run_id": "run-001", "environment_sha256": environment_sha256}
            ],
        }
    )

    environment_sha256 = sha256_json(record["environment"])
    matrix["entries"][0]["environment_sha256"] = environment_sha256
    registry["claims"][4]["supported_stacks"][0]["environment_sha256"] = environment_sha256
    cold_copy_path = stage_paths_by_check["second_clean_project_cold_copy"]
    validate_verified_references(
        matrix,
        registry,
        {evidence_path: record},
        _verified_run_schema(),
        _artifact_schemas(),
        tmp_path,
        sensitive_terms,
    )

    cold_evidence_path = evidence_paths_by_check["second_clean_project_cold_copy"]
    cold_evidence_artifact = tmp_path / cold_evidence_path
    cold_evidence_payload = json.loads(cold_evidence_artifact.read_text(encoding="utf-8"))

    def reseal_cold_evidence() -> None:
        cold_evidence_artifact.write_text(json.dumps(cold_evidence_payload), encoding="utf-8")
        cold_evidence_sha256 = sha256_file(cold_evidence_artifact)
        next(item for item in record["artifacts"] if item["path"] == cold_evidence_path)[
            "sha256"
        ] = cold_evidence_sha256
        redaction_payload = json.loads(redaction_artifact.read_text(encoding="utf-8"))
        next(
            item
            for item in redaction_payload["scanned_artifacts"]
            if item["path"] == cold_evidence_path
        )["sha256"] = cold_evidence_sha256
        redaction_artifact.write_text(json.dumps(redaction_payload), encoding="utf-8")
        next(item for item in record["artifacts"] if item["path"] == redaction_path)[
            "sha256"
        ] = sha256_file(redaction_artifact)
        record_path.write_text(json.dumps(record), encoding="utf-8")

    cold_evidence_payload["evidence_type"] = "manual-review"
    reseal_cold_evidence()
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
        )
    assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"
    cold_evidence_payload["evidence_type"] = "portability-replay"
    reseal_cold_evidence()

    cold_evidence_payload["observations"][0]["value"] = False
    reseal_cold_evidence()
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
        )
    assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"
    cold_evidence_payload["observations"][0]["value"] = True
    reseal_cold_evidence()

    for contradictory_value in (False, "false", 0):
        cold_evidence_payload["observations"].append(
            {
                "name": "acceptance",
                "value": contradictory_value,
                "source": "anonymous-conflicting-fixture",
            }
        )
        reseal_cold_evidence()
        with pytest.raises(CmtkError) as error:
            validate_verified_references(
                matrix,
                registry,
                {evidence_path: record},
                _verified_run_schema(),
                _artifact_schemas(),
                tmp_path,
                sensitive_terms,
            )
        assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"
        cold_evidence_payload["observations"].pop()
        reseal_cold_evidence()

    record["profile"] = "anonymous-private-term"
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
        )
    assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"
    record["profile"] = "standalone-map"
    record_path.write_text(json.dumps(record), encoding="utf-8")

    redaction_envelope = json.loads(redaction_artifact.read_text(encoding="utf-8"))
    redaction_envelope["scanner"] = "anonymous-private-term"
    redaction_artifact.write_text(json.dumps(redaction_envelope), encoding="utf-8")
    next(item for item in record["artifacts"] if item["path"] == redaction_path)["sha256"] = sha256_file(
        redaction_artifact
    )
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
        )
    assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"
    redaction_envelope["scanner"] = "anonymous-fixture-scanner"
    redaction_artifact.write_text(json.dumps(redaction_envelope), encoding="utf-8")
    next(item for item in record["artifacts"] if item["path"] == redaction_path)["sha256"] = sha256_file(
        redaction_artifact
    )
    record_path.write_text(json.dumps(record), encoding="utf-8")

    record["stage_results"].remove(cold_copy_path)
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
        )
    assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"
    record["stage_results"].append(cold_copy_path)
    record["stage_results"].sort()
    record_path.write_text(json.dumps(record), encoding="utf-8")

    cold_evidence_payload["summary"] = "Changed after the redaction report."
    cold_evidence_artifact.write_text(json.dumps(cold_evidence_payload), encoding="utf-8")
    next(item for item in record["artifacts"] if item["path"] == cold_evidence_path)[
        "sha256"
    ] = sha256_file(cold_evidence_artifact)
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
    )
    assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"
    cold_evidence_payload["summary"] = "Anonymous structured acceptance evidence."
    cold_evidence_artifact.write_text(json.dumps(cold_evidence_payload), encoding="utf-8")
    next(item for item in record["artifacts"] if item["path"] == cold_evidence_path)[
        "sha256"
    ] = sha256_file(cold_evidence_artifact)
    record_path.write_text(json.dumps(record), encoding="utf-8")

    cold_evidence_payload["summary"] = "anonymous-private-term"
    cold_evidence_artifact.write_text(json.dumps(cold_evidence_payload), encoding="utf-8")
    private_sha256 = sha256_file(cold_evidence_artifact)
    next(item for item in record["artifacts"] if item["path"] == cold_evidence_path)[
        "sha256"
    ] = private_sha256
    redaction_payload = json.loads(redaction_artifact.read_text(encoding="utf-8"))
    next(item for item in redaction_payload["scanned_artifacts"] if item["path"] == cold_evidence_path)[
        "sha256"
    ] = private_sha256
    redaction_artifact.write_text(json.dumps(redaction_payload), encoding="utf-8")
    next(item for item in record["artifacts"] if item["path"] == redaction_path)["sha256"] = sha256_file(
        redaction_artifact
    )
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
    )
    assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"
    cold_evidence_payload["summary"] = "Anonymous structured acceptance evidence."
    cold_evidence_artifact.write_text(json.dumps(cold_evidence_payload), encoding="utf-8")
    cold_evidence_sha256 = sha256_file(cold_evidence_artifact)
    next(item for item in record["artifacts"] if item["path"] == cold_evidence_path)[
        "sha256"
    ] = cold_evidence_sha256
    next(item for item in redaction_payload["scanned_artifacts"] if item["path"] == cold_evidence_path)[
        "sha256"
    ] = cold_evidence_sha256
    redaction_artifact.write_text(json.dumps(redaction_payload), encoding="utf-8")
    next(item for item in record["artifacts"] if item["path"] == redaction_path)["sha256"] = sha256_file(
        redaction_artifact
    )
    record_path.write_text(json.dumps(record), encoding="utf-8")

    cold_evidence_artifact.write_bytes(b"")
    empty_sha256 = sha256_file(cold_evidence_artifact)
    next(item for item in record["artifacts"] if item["path"] == cold_evidence_path)["sha256"] = empty_sha256
    next(item for item in redaction_payload["scanned_artifacts"] if item["path"] == cold_evidence_path)[
        "sha256"
    ] = empty_sha256
    redaction_artifact.write_text(json.dumps(redaction_payload), encoding="utf-8")
    next(item for item in record["artifacts"] if item["path"] == redaction_path)["sha256"] = sha256_file(
        redaction_artifact
    )
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
        )
    assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"
    cold_evidence_artifact.write_text(json.dumps(cold_evidence_payload), encoding="utf-8")
    cold_evidence_sha256 = sha256_file(cold_evidence_artifact)
    next(item for item in record["artifacts"] if item["path"] == cold_evidence_path)[
        "sha256"
    ] = cold_evidence_sha256
    next(item for item in redaction_payload["scanned_artifacts"] if item["path"] == cold_evidence_path)[
        "sha256"
    ] = cold_evidence_sha256
    redaction_artifact.write_text(json.dumps(redaction_payload), encoding="utf-8")
    next(item for item in record["artifacts"] if item["path"] == redaction_path)["sha256"] = sha256_file(
        redaction_artifact
    )
    record_path.write_text(json.dumps(record), encoding="utf-8")

    cold_copy_artifact = tmp_path / cold_copy_path
    cold_copy_payload = json.loads(cold_copy_artifact.read_text(encoding="utf-8"))
    cold_copy_payload["stage"] = "SRC2UE427.VALIDATE"
    cold_copy_artifact.write_text(json.dumps(cold_copy_payload), encoding="utf-8")
    next(item for item in record["artifacts"] if item["path"] == cold_copy_path)["sha256"] = sha256_file(
        cold_copy_artifact
    )
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
        )
    assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"
    cold_copy_payload["stage"] = "SRC2UE427.COLD_COPY"
    cold_copy_artifact.write_text(json.dumps(cold_copy_payload), encoding="utf-8")
    next(item for item in record["artifacts"] if item["path"] == cold_copy_path)["sha256"] = sha256_file(
        cold_copy_artifact
    )
    record_path.write_text(json.dumps(record), encoding="utf-8")

    record["input_hashes"][0]["path"] = f"{bundle}/missing-input.json"
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
        )
    assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"
    record["input_hashes"][0]["path"] = input_path
    record_path.write_text(json.dumps(record), encoding="utf-8")

    cold_copy_payload["checks"][0]["evidence"] = []
    cold_copy_artifact.write_text(json.dumps(cold_copy_payload), encoding="utf-8")
    next(item for item in record["artifacts"] if item["path"] == cold_copy_path)["sha256"] = sha256_file(
        cold_copy_artifact
    )
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
        )
    assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"
    cold_copy_payload["checks"][0]["evidence"] = [cold_evidence_path]
    cold_copy_artifact.write_text(json.dumps(cold_copy_payload), encoding="utf-8")
    next(item for item in record["artifacts"] if item["path"] == cold_copy_path)["sha256"] = sha256_file(
        cold_copy_artifact
    )
    record_path.write_text(json.dumps(record), encoding="utf-8")

    record["required_checks"][0]["evidence"].append(
        "evidence/verified/source-to-ue427/run-001/unlisted.json"
    )
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
        )
    assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"
    record["required_checks"][0]["evidence"].pop()
    record_path.write_text(json.dumps(record), encoding="utf-8")

    matrix["entries"][0]["evidence_bundle"] = "evidence/verified/source-to-ue427"
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
        )
    assert error.value.reason_code == "EVIDENCE-REFERENCE-INVALID"
    matrix["entries"][0]["evidence_bundle"] = bundle

    matrix["entries"][0]["engine"] = "fabricated-engine"
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
        )
    assert error.value.reason_code == "EVIDENCE-REFERENCE-INVALID"
    matrix["entries"][0]["engine"] = "4.26.2-carla-fork to 4.27.2"

    registry["claims"][4]["supported_stacks"].append(
        {"run_id": "fabricated", "environment_sha256": "f" * 64}
    )
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
        )
    assert error.value.reason_code == "EVIDENCE-REFERENCE-INVALID"
    registry["claims"][4]["supported_stacks"].pop()

    record["target_identity"]["engine_version"] = "5.5.0"
    record_path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
        )
    assert error.value.reason_code == "EVIDENCE-REFERENCE-INVALID"
    record["target_identity"]["engine_version"] = "4.27.2"
    record_path.write_text(json.dumps(record), encoding="utf-8")

    record_path.write_text("{}\n", encoding="utf-8")
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
        )
    assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"

    record_path.write_text(json.dumps(record), encoding="utf-8")
    cold_copy_artifact.write_text('{"status":"tampered"}\n', encoding="utf-8")
    with pytest.raises(CmtkError) as error:
        validate_verified_references(
            matrix,
            registry,
            {evidence_path: record},
            _verified_run_schema(),
            _artifact_schemas(),
            tmp_path,
            sensitive_terms,
        )
    assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"


def test_verified_claim_schema_requires_supported_stack():
    schema = json.loads((PLUGIN_ROOT / "schemas" / "claims-registry.schema.json").read_text(encoding="utf-8"))
    registry = _registry()
    claim = registry["claims"][4]
    claim.update({"status": "maintainer-verified", "verified_runs": ["run-001"], "supported_stacks": []})
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(registry, schema)
