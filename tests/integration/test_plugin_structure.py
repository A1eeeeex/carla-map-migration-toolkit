import hashlib
import json

import yaml
from cmtk.routes.catalog import (
    OPTIONAL_STAGE_CHECK_EVIDENCE_TYPES,
    OPTIONAL_STAGE_CHECK_STAGES,
    REQUIRED_CHECK_EVIDENCE_TYPES,
    REQUIRED_CHECK_STAGES,
    ROUTES,
    STEP_CATALOG,
)
from conftest import PLUGIN_ROOT, REPO_ROOT

SKILLS = {
    "roadrunner-to-source-carla",
    "source-carla-to-package-carla",
    "source-carla-to-ue427",
}


def test_plugin_has_exactly_three_top_level_skills():
    actual = {path.name for path in (PLUGIN_ROOT / "skills").iterdir() if path.is_dir()}
    assert actual == SKILLS


def test_manifest_and_marketplace_identifiers_match():
    manifest = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    marketplace = json.loads((REPO_ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))
    assert manifest["name"] == PLUGIN_ROOT.name
    assert marketplace["plugins"][0]["name"] == manifest["name"]
    assert marketplace["plugins"][0]["source"]["path"] == "./plugins/carla-map-migration-toolkit"


def test_public_release_metadata_has_an_accountable_identity_and_license():
    citation = yaml.safe_load((REPO_ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    manifest = json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    license_bytes = (REPO_ROOT / "LICENSE").read_bytes()
    notice = (REPO_ROOT / "NOTICE.md").read_text(encoding="utf-8")
    security = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")

    assert len(citation["authors"]) == 1
    author = citation["authors"][0]
    assert set(author) == {"family-names", "given-names"}
    assert all(author.values())
    assert citation["license"] == "Apache-2.0"
    assert manifest["license"] == "Apache-2.0"
    expected_license_sha256 = "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
    assert hashlib.sha256(license_bytes).hexdigest() == expected_license_sha256
    assert f'Copyright 2026 {author["given-names"]} {author["family-names"]}' in notice
    assert manifest["author"] == {"name": "A1eeeeex", "url": "https://github.com/A1eeeeex"}
    assert manifest["interface"]["developerName"] == "A1eeeeex"
    assert "private vulnerability reporting" in security.casefold()


def test_skills_have_discriminating_descriptions_and_ui_metadata():
    for name in SKILLS:
        skill_dir = PLUGIN_ROOT / "skills" / name
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        assert "[TODO:" not in text
        assert "Use This Skill When" in text
        assert "Do Not Use This Skill When" in text
        metadata = yaml.safe_load((skill_dir / "agents" / "openai.yaml").read_text(encoding="utf-8"))
        installed_skill_name = f"$carla-map-migration-toolkit:{name}"
        assert installed_skill_name in metadata["interface"]["default_prompt"]


def test_route_stage_catalog_contains_required_contract_stages():
    expected = {
        "roadrunner-to-source-carla": {
            "DISCOVER_INPUT",
            "PREFLIGHT_ENV",
            "VALIDATE_EXPORT",
            "BASELINE",
            "PREPARE_TARGET",
            "IMPORT",
            "POST_IMPORT_AUDIT",
            "REPAIR",
            "FUNCTIONAL_VALIDATE",
            "OPTIMIZE",
            "TARGET_VALIDATE",
            "HANDOFF",
        },
        "source-carla-to-package-carla": {
            "READ_HANDOFF",
            "PREFLIGHT",
            "BASELINE",
            "SELECT_OUTPUT",
            "AUDIT_CONFIG",
            "AUDIT_COOK_DEPS",
            "REPAIR",
            "BUILD",
            "ARCHIVE_AUDIT",
            "BACKUP_TARGET",
            "IMPORT",
            "RUNTIME_VALIDATE",
            "OPTIMIZE",
            "HANDOFF",
        },
        "source-carla-to-ue427": {
            "READ_HANDOFF",
            "PREFLIGHT",
            "BASELINE",
            "CLASSIFY_DEPS",
            "CREATE_TARGET",
            "MIGRATE_ASSETS",
            "REPAIR_MATERIALS",
            "REPLACE_CARLA",
            "REPAIR_WORLD",
            "REPAIR_COLLISION",
            "CLEAN_REFS",
            "OPTIMIZE",
            "TARGET_VALIDATE",
            "COLD_COPY",
            "HIL_VALIDATE",
            "HANDOFF",
        },
    }
    for route, required in expected.items():
        actual = {step[0] for step in STEP_CATALOG[route]}
        assert actual == required


def test_required_check_stage_contracts_only_reference_catalog_stages():
    assert set(REQUIRED_CHECK_STAGES) == set(STEP_CATALOG)
    for route, checks in REQUIRED_CHECK_STAGES.items():
        prefix = ROUTES[route]["prefix"]
        known_stages = {f"{prefix}.{step[0]}" for step in STEP_CATALOG[route]}
        assert checks
        assert all(stages and set(stages) <= known_stages for stages in checks.values())


def test_required_check_evidence_types_match_stage_execution_contexts():
    unreal_contexts = {"source-unreal-python", "ue427-unreal-python"}
    stage_contexts = {
        route: {
            f"{ROUTES[route]['prefix']}.{suffix}": context
            for suffix, _step_type, context, _risk in steps
        }
        for route, steps in STEP_CATALOG.items()
    }
    assert set(REQUIRED_CHECK_EVIDENCE_TYPES) == set(REQUIRED_CHECK_STAGES)
    for route, checks in REQUIRED_CHECK_STAGES.items():
        assert set(REQUIRED_CHECK_EVIDENCE_TYPES[route]) == set(checks)
        for check_id, stages in checks.items():
            evidence_type = REQUIRED_CHECK_EVIDENCE_TYPES[route][check_id]
            if evidence_type == "editor-audit":
                assert all(stage_contexts[route][stage] in unreal_contexts for stage in stages), (
                    route,
                    check_id,
                    stages,
                )

    assert set(OPTIONAL_STAGE_CHECK_STAGES) == set(REQUIRED_CHECK_STAGES)
    assert set(OPTIONAL_STAGE_CHECK_EVIDENCE_TYPES) == set(REQUIRED_CHECK_STAGES)
    for route, checks in OPTIONAL_STAGE_CHECK_STAGES.items():
        assert set(OPTIONAL_STAGE_CHECK_EVIDENCE_TYPES[route]) == set(checks)
        for check_id, stages in checks.items():
            assert OPTIONAL_STAGE_CHECK_EVIDENCE_TYPES[route][check_id] == "editor-audit"
            assert all(stage_contexts[route][stage] in unreal_contexts for stage in stages)
