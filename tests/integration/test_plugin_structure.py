import json

import yaml
from cmtk.routes.catalog import STEP_CATALOG
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


def test_skills_have_discriminating_descriptions_and_ui_metadata():
    for name in SKILLS:
        skill_dir = PLUGIN_ROOT / "skills" / name
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        assert "[TODO:" not in text
        assert "Use This Skill When" in text
        assert "Do Not Use This Skill When" in text
        metadata = yaml.safe_load((skill_dir / "agents" / "openai.yaml").read_text(encoding="utf-8"))
        assert f"${name}" in metadata["interface"]["default_prompt"]


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
