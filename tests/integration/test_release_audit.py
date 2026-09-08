from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from conftest import REPO_ROOT

AUDIT_SCRIPT = REPO_ROOT / "development" / "shared" / "release_tools" / "publication_audit.py"


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def test_reviewed_showcase_passes_tree_and_history_but_not_external_binary(tmp_path: Path):
    from development.shared.release_tools.publication_audit import audit_repository

    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    _git(candidate, "config", "user.name", "Anonymous Fixture")
    _git(candidate, "config", "user.email", "fixture@example.invalid")
    path = "docs/assets/showcase/before.png"
    image = candidate / path
    image.parent.mkdir(parents=True)
    content = (REPO_ROOT / path).read_bytes()
    image.write_bytes(content)
    _git(candidate, "add", path)
    _git(candidate, "commit", "--quiet", "-m", "reviewed media")
    terms = tmp_path / "terms.txt"
    terms.write_text("private-project\n")
    export = tmp_path / "export"
    export.mkdir()
    (export / "summary.txt").write_text("anonymous fixture\n")
    assert audit_repository(candidate, terms, export)["status"] == "PASS"
    (export / "before.png").write_bytes(content)
    assert audit_repository(candidate, terms, export)["status"] == "FAIL"
    (export / "before.png").unlink()
    image.write_bytes(content + b"unreviewed")
    _git(candidate, "add", path)
    _git(candidate, "commit", "--quiet", "-m", "changed media")
    assert audit_repository(candidate, terms, export)["status"] == "FAIL"


def test_release_audit_scans_tree_history_and_external_export_without_echoing_terms(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    _git(candidate, "config", "user.name", "Anonymous Fixture")
    _git(candidate, "config", "user.email", "fixture@example.invalid")
    (candidate / "safe.txt").write_text("anonymous public content\n", encoding="utf-8")
    _git(candidate, "add", "safe.txt")
    _git(candidate, "commit", "--quiet", "-m", "fixture")

    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("private-project\n", encoding="utf-8")
    external_export = tmp_path / "actions-export"
    external_export.mkdir()
    (external_export / "job.txt").write_text("anonymous action output\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report == {
        "schema_version": "1.0.0",
        "status": "PASS",
        "private_literals": {
            "count": 1,
            "sha256": hashlib.sha256(b"private-project\n").hexdigest(),
        },
        "scopes": {
            "working_tree": {"files_scanned": 1},
            "git_history": {"objects_scanned": 3, "refs_scanned": 1},
            "external_export": {"files_scanned": 1},
        },
        "findings": [],
    }
    assert "private-project" not in result.stdout


def test_release_audit_blocks_an_empty_private_literal_set(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("# no approved terms supplied\n", encoding="utf-8")
    external_export = tmp_path / "actions-export"
    external_export.mkdir()

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert json.loads(result.stdout) == {
        "schema_version": "1.0.0",
        "status": "BLOCKED",
        "reason_code": "PUBLICATION-PRIVATE-LITERALS-EMPTY",
        "private_literals": {"count": 0, "sha256": None},
        "scopes": {
            "working_tree": {"files_scanned": 0},
            "git_history": {"objects_scanned": 0, "refs_scanned": 0},
            "external_export": {"files_scanned": 0},
        },
        "findings": [],
    }


def test_release_audit_blocks_when_external_actions_export_is_missing(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("private-project\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(tmp_path / "missing-actions-export"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert json.loads(result.stdout)["reason_code"] == "PUBLICATION-EXTERNAL-EXPORT-MISSING"


def test_release_audit_reports_private_hits_by_scope_without_echoing_the_literal(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    _git(candidate, "config", "user.name", "Anonymous Fixture")
    _git(candidate, "config", "user.email", "fixture@example.invalid")
    (candidate / "tracked.txt").write_text("private-project\n", encoding="utf-8")
    _git(candidate, "add", "tracked.txt")
    _git(candidate, "commit", "--quiet", "-m", "fixture")

    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("private-project\n", encoding="utf-8")
    external_export = tmp_path / "actions-export"
    external_export.mkdir()
    (external_export / "job.txt").write_text("private-project\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "FAIL"
    assert {item["scope"] for item in report["findings"]} == {
        "working_tree",
        "git_history",
        "external_export",
    }
    assert all(item["reason_code"] == "PUBLICATION-PRIVATE-LITERAL-DETECTED" for item in report["findings"])
    assert "private-project" not in result.stdout


def test_release_audit_blocks_a_dirty_or_untracked_worktree(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    _git(candidate, "config", "user.name", "Anonymous Fixture")
    _git(candidate, "config", "user.email", "fixture@example.invalid")
    (candidate / "tracked.txt").write_text("anonymous\n", encoding="utf-8")
    _git(candidate, "add", "tracked.txt")
    _git(candidate, "commit", "--quiet", "-m", "fixture")
    (candidate / "untracked.txt").write_text("anonymous\n", encoding="utf-8")

    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("private-project\n", encoding="utf-8")
    external_export = tmp_path / "actions-export"
    external_export.mkdir()
    (external_export / "job.txt").write_text("anonymous action output\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert json.loads(result.stdout)["reason_code"] == "PUBLICATION-WORKTREE-DIRTY"


def test_release_audit_blocks_an_empty_external_actions_export(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("private-project\n", encoding="utf-8")
    external_export = tmp_path / "actions-export"
    external_export.mkdir()

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert json.loads(result.stdout)["reason_code"] == "PUBLICATION-EXTERNAL-EXPORT-EMPTY"


def test_release_audit_rejects_symlinks_in_the_external_export(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("private-project\n", encoding="utf-8")
    external_export = tmp_path / "actions-export"
    external_export.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("anonymous\n", encoding="utf-8")
    (external_export / "linked.txt").symlink_to(outside)

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert json.loads(result.stdout)["reason_code"] == "PUBLICATION-EXTERNAL-EXPORT-UNSAFE-MEMBER"


def test_release_audit_scans_reachable_commit_metadata_without_echoing_terms(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    _git(candidate, "config", "user.name", "Anonymous Fixture")
    _git(candidate, "config", "user.email", "fixture@example.invalid")
    (candidate / "safe.txt").write_text("anonymous public content\n", encoding="utf-8")
    _git(candidate, "add", "safe.txt")
    _git(candidate, "commit", "--quiet", "-m", "private-project")

    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("private-project\n", encoding="utf-8")
    external_export = tmp_path / "actions-export"
    external_export.mkdir()
    (external_export / "job.txt").write_text("anonymous action output\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "FAIL"
    assert {item["scope"] for item in report["findings"]} == {"git_history"}
    assert "private-project" not in result.stdout


def test_release_audit_scans_historical_tree_names_without_echoing_terms(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    _git(candidate, "config", "user.name", "Anonymous Fixture")
    _git(candidate, "config", "user.email", "fixture@example.invalid")
    (candidate / "private-project.txt").write_text("anonymous public content\n", encoding="utf-8")
    _git(candidate, "add", "private-project.txt")
    _git(candidate, "commit", "--quiet", "-m", "fixture")
    _git(candidate, "mv", "private-project.txt", "safe.txt")
    _git(candidate, "commit", "--quiet", "-m", "anonymous rename")

    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("private-project\n", encoding="utf-8")
    external_export = tmp_path / "actions-export"
    external_export.mkdir()
    (external_export / "job.txt").write_text("anonymous action output\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "FAIL"
    assert {item["scope"] for item in report["findings"]} == {"git_history"}
    assert "private-project" not in result.stdout


def test_release_audit_blocks_when_the_private_literal_file_is_missing(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    external_export = tmp_path / "actions-export"
    external_export.mkdir()
    (external_export / "job.txt").write_text("anonymous action output\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(tmp_path / "missing-private-literals.txt"),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert json.loads(result.stdout)["reason_code"] == "PUBLICATION-PRIVATE-LITERALS-MISSING"


def test_release_audit_rejects_a_symlinked_external_export_root(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("private-project\n", encoding="utf-8")
    external_target = tmp_path / "actions-export-target"
    external_target.mkdir()
    (external_target / "job.txt").write_text("anonymous action output\n", encoding="utf-8")
    external_export = tmp_path / "actions-export"
    external_export.symlink_to(external_target, target_is_directory=True)

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert json.loads(result.stdout)["reason_code"] == "PUBLICATION-EXTERNAL-EXPORT-UNSAFE-MEMBER"


def test_release_audit_scans_external_export_names_without_echoing_terms(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    _git(candidate, "config", "user.name", "Anonymous Fixture")
    _git(candidate, "config", "user.email", "fixture@example.invalid")
    (candidate / "safe.txt").write_text("anonymous public content\n", encoding="utf-8")
    _git(candidate, "add", "safe.txt")
    _git(candidate, "commit", "--quiet", "-m", "fixture")
    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("private-project\n", encoding="utf-8")
    external_export = tmp_path / "actions-export"
    external_export.mkdir()
    (external_export / "private-project.txt").write_text("anonymous action output\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "FAIL"
    assert {item["scope"] for item in report["findings"]} == {"external_export"}
    assert "private-project" not in result.stdout


def test_release_audit_rejects_tracked_symlinks_without_reading_their_target(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    _git(candidate, "config", "user.name", "Anonymous Fixture")
    _git(candidate, "config", "user.email", "fixture@example.invalid")
    outside = tmp_path / "outside.txt"
    outside.write_text("private-project\n", encoding="utf-8")
    (candidate / "linked.txt").symlink_to(outside)
    _git(candidate, "add", "linked.txt")
    _git(candidate, "commit", "--quiet", "-m", "fixture")
    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("private-project\n", encoding="utf-8")
    external_export = tmp_path / "actions-export"
    external_export.mkdir()
    (external_export / "job.txt").write_text("anonymous action output\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert json.loads(result.stdout)["reason_code"] == "PUBLICATION-WORKTREE-UNSAFE-ENTRY"
    assert "private-project" not in result.stdout


def test_release_audit_blocks_oversized_scan_inputs_before_reading_them(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("private-project\n", encoding="utf-8")
    external_export = tmp_path / "actions-export"
    external_export.mkdir()
    oversized = external_export / "oversized.txt"
    with oversized.open("wb") as handle:
        handle.seek(64 * 1024 * 1024)
        handle.write(b"\0")

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert json.loads(result.stdout)["reason_code"] == "PUBLICATION-SCAN-INPUT-TOO-LARGE"


def test_release_audit_scans_empty_external_directory_names_without_echoing_terms(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    _git(candidate, "config", "user.name", "Anonymous Fixture")
    _git(candidate, "config", "user.email", "fixture@example.invalid")
    (candidate / "safe.txt").write_text("anonymous public content\n", encoding="utf-8")
    _git(candidate, "add", "safe.txt")
    _git(candidate, "commit", "--quiet", "-m", "fixture")
    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("private-project\n", encoding="utf-8")
    external_export = tmp_path / "actions-export"
    external_export.mkdir()
    (external_export / "safe.txt").write_text("anonymous action output\n", encoding="utf-8")
    (external_export / "private-project-empty").mkdir()

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["status"] == "FAIL"
    assert {item["scope"] for item in report["findings"]} == {"external_export"}
    assert "private-project" not in result.stdout


def test_release_audit_rejects_forbidden_asset_paths_in_git_history(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    _git(candidate, "config", "user.name", "Anonymous Fixture")
    _git(candidate, "config", "user.email", "fixture@example.invalid")
    asset = candidate / "anonymous-map.uasset"
    asset.write_text("synthetic forbidden-extension fixture\n", encoding="utf-8")
    _git(candidate, "add", asset.name)
    _git(candidate, "commit", "--quiet", "-m", "fixture asset path")
    asset.unlink()
    (candidate / "safe.txt").write_text("anonymous public content\n", encoding="utf-8")
    _git(candidate, "add", "--all")
    _git(candidate, "commit", "--quiet", "-m", "remove fixture asset path")

    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("private-project\n", encoding="utf-8")
    external_export = tmp_path / "actions-export"
    external_export.mkdir()
    (external_export / "job.txt").write_text("anonymous action output\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert any(
        item["scope"] == "git_history" and item["reason_code"] == "PUBLICATION-FORBIDDEN-ASSET-PATH"
        for item in report["findings"]
    )
    assert "anonymous-map.uasset" not in result.stdout


def test_release_audit_rejects_binary_git_blobs_without_exposing_content(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    _git(candidate, "config", "user.name", "Anonymous Fixture")
    _git(candidate, "config", "user.email", "fixture@example.invalid")
    binary = candidate / "opaque-data"
    binary.write_bytes(b"anonymous\0binary\xfffixture")
    _git(candidate, "add", binary.name)
    _git(candidate, "commit", "--quiet", "-m", "binary fixture")
    binary.unlink()
    (candidate / "safe.txt").write_text("anonymous public content\n", encoding="utf-8")
    _git(candidate, "add", "--all")
    _git(candidate, "commit", "--quiet", "-m", "remove binary fixture")

    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("private-project\n", encoding="utf-8")
    external_export = tmp_path / "actions-export"
    external_export.mkdir()
    (external_export / "job.txt").write_text("anonymous action output\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert any(
        item["scope"] == "git_history" and item["reason_code"] == "PUBLICATION-BINARY-CONTENT-DETECTED"
        for item in report["findings"]
    )
    assert "binary fixture" not in result.stdout


def test_release_audit_rejects_binary_external_artifacts(tmp_path: Path):
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    _git(candidate, "init", "--quiet")
    _git(candidate, "config", "user.name", "Anonymous Fixture")
    _git(candidate, "config", "user.email", "fixture@example.invalid")
    (candidate / "safe.txt").write_text("anonymous public content\n", encoding="utf-8")
    _git(candidate, "add", "safe.txt")
    _git(candidate, "commit", "--quiet", "-m", "fixture")

    private_terms = tmp_path / "private-literals.txt"
    private_terms.write_text("private-project\n", encoding="utf-8")
    external_export = tmp_path / "actions-export"
    external_export.mkdir()
    (external_export / "artifact.bin").write_bytes(b"anonymous\0binary\xfffixture")

    result = subprocess.run(
        [
            sys.executable,
            str(AUDIT_SCRIPT),
            "--repo",
            str(candidate),
            "--private-literals",
            str(private_terms),
            "--external-root",
            str(external_export),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["findings"] == [
        {
            "scope": "external_export",
            "reason_code": "PUBLICATION-BINARY-CONTENT-DETECTED",
            "subject_sha256": hashlib.sha256(b"artifact.bin").hexdigest(),
        }
    ]
