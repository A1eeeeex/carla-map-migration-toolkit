from __future__ import annotations

import json
import shlex
import xml.etree.ElementTree as ET

import yaml
from cmtk.cli import _parser
from conftest import REPO_ROOT

from development.shared.release_tools.check_doc_links import check_links


def test_public_document_links_resolve():
    files = json.loads((REPO_ROOT / "PUBLICATION_ALLOWLIST.json").read_text())["files"]
    assert check_links(REPO_ROOT, files) == []


def test_link_checker_rejects_missing_files_and_headings(tmp_path):
    (tmp_path / "README.md").write_text("# Guide\n\n[Missing](absent.md)\n[Heading](#absent)\n")
    failures = check_links(tmp_path, ["README.md"])
    assert len(failures) == 2
    assert any("missing or outside repository" in failure for failure in failures)
    assert any("missing heading" in failure for failure in failures)


def test_cookbook_documents_real_commands_and_boundaries():
    pages = sorted((REPO_ROOT / "docs/troubleshooting").glob("*.md"))
    assert len(pages) >= 6
    required = (
        "Symptoms", "What usually needs checking", "Toolkit diagnosis",
        "Manual / Editor checkpoint", "Validation", "Evidence to keep",
        "What this guide does NOT prove",
    )
    for page in pages:
        if page.name == "README.md":
            continue
        text = page.read_text()
        assert all(f"## {heading}" in text for heading in required)
        commands = [line for line in text.splitlines() if line.startswith("CMTK_EXECUTION_CONTEXT=")]
        assert commands
        for command in commands:
            arguments = shlex.split(command)
            index = next(i for i, value in enumerate(arguments) if value.endswith("/cmtk.py"))
            _parser().parse_args(arguments[index + 1:])


def test_issue_forms_and_release_version_are_consistent():
    for name in ("bug_report", "compatibility_report", "feature_request"):
        form = yaml.safe_load((REPO_ROOT / f".github/ISSUE_TEMPLATE/{name}.yml").read_text())
        assert form["name"] and form["description"] and form["body"]
        ids = [item["id"] for item in form["body"] if "id" in item]
        assert len(ids) == len(set(ids))
        assert "Do not upload private maps" in form["body"][0]["attributes"]["value"]
    manifest = json.loads(
        (REPO_ROOT / "plugins/carla-map-migration-toolkit/.codex-plugin/plugin.json").read_text()
    )
    notes = REPO_ROOT / f"docs/release/v{manifest['version']}-release-notes.md"
    assert notes.read_text().startswith(f"# v{manifest['version']} — Experimental Public Preview")
    svg = ET.parse(REPO_ROOT / "docs/assets/social/social-preview.svg").getroot()
    assert (svg.attrib["width"], svg.attrib["height"]) == ("1280", "640")
    assert not any(element.tag.endswith(("script", "image", "foreignObject")) for element in svg.iter())


def test_golden_map_protocol_has_no_fabricated_execution():
    root = REPO_ROOT / "development/shared/plans/golden-map"
    for name in ("INPUT_CONTRACT", "RIGHTS_CHECKLIST", "RUNBOOK", "CAPTURE_CHECKLIST", "EVIDENCE_CHECKLIST"):
        assert (root / f"{name}.md").is_file()
    manifest = json.loads((root / "manifest.json").read_text())
    assert manifest["status"] == "planned"
    assert manifest["verified_environments"] == []
    for name in ("README.md", "README.zh-CN.md"):
        text = (REPO_ROOT / name).read_text()
        assert text.count("<!-- GOLDEN_MAP_SHOWCASE_START -->") == 1
        assert text.count("<!-- GOLDEN_MAP_SHOWCASE_END -->") == 1
        assert "```mermaid" in text
