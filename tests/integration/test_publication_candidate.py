from __future__ import annotations

import json
import re
from pathlib import Path

from conftest import REPO_ROOT

_MANIFEST_PATH = REPO_ROOT / "PUBLICATION_ALLOWLIST.json"
_LOCAL_PATH = re.compile(r"/(?:" + "home|Users|root|mnt|media|opt|srv|tmp|var" + r")/[A-Za-z0-9_.-]+/")
_SECRET_ASSIGNMENT = re.compile(r"(?i)\b(?:token|api[_-]?key|password|secret)\s*[:=]\s*[^\s,;]+")
_TEXT_SUFFIXES = {".cff", ".json", ".md", ".py", ".toml", ".txt", ".yaml", ".yml"}


def _load_manifest() -> dict:
    return json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))


def _candidate_files(manifest: dict) -> set[str]:
    files = {path for path in manifest["root_files"]}
    for relative_root in manifest["candidate_roots"]:
        root = REPO_ROOT / relative_root
        assert root.is_dir(), f"candidate root is missing: {relative_root}"
        files.update(str(path.relative_to(REPO_ROOT)) for path in root.rglob("*") if path.is_file())
    return files


def test_publication_candidate_matches_explicit_per_file_allowlist():
    manifest = _load_manifest()
    actual = _candidate_files(manifest)
    expected = set(manifest["files"])
    assert actual == expected, {
        "unexpected": sorted(actual - expected),
        "missing": sorted(expected - actual),
    }


def test_publication_candidate_has_no_forbidden_binary_or_asset_suffix():
    manifest = _load_manifest()
    forbidden = {suffix.lower() for suffix in manifest["forbidden_suffixes"]}
    offenders = [path for path in _candidate_files(manifest) if Path(path).suffix.lower() in forbidden]
    assert offenders == []


def test_publication_candidate_has_no_unapproved_host_path_or_secret_assignment():
    manifest = _load_manifest()
    exceptions = set(manifest["content_scan_exceptions"])
    offenders: list[dict[str, str]] = []
    for relative_path in sorted(_candidate_files(manifest) - exceptions):
        path = REPO_ROOT / relative_path
        if path.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        content = path.read_text(encoding="utf-8")
        if _LOCAL_PATH.search(content):
            offenders.append({"path": relative_path, "class": "host-path"})
        if _SECRET_ASSIGNMENT.search(content):
            offenders.append({"path": relative_path, "class": "secret-assignment"})
        for prohibited in manifest["prohibited_literals"]:
            if prohibited.casefold() in content.casefold():
                offenders.append({"path": relative_path, "class": "private-identifier"})
    assert offenders == []
