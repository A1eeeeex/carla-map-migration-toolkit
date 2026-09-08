#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import unicodedata
from pathlib import Path

MAX_SCAN_BYTES = 64 * 1024 * 1024
APPROVED_SHOWCASE_MEDIA = {
    "docs/assets/showcase/before.png": "38988f25d71b81355d03e44ff4161afbf3ce663f3f8a26017f58d32bc878f145",
    "docs/assets/showcase/after.png": "5c4d0479c0129cc31f1911883fc448bf7510eec5242a3f1e66635dd91e6f88f0",
}


def is_approved_showcase_media(path: str, content: bytes) -> bool:
    return APPROVED_SHOWCASE_MEDIA.get(path) == hashlib.sha256(content).hexdigest()


FORBIDDEN_PUBLIC_SUFFIXES = frozenset(
    {
        ".7z",
        ".fbx",
        ".gz",
        ".jpeg",
        ".jpg",
        ".log",
        ".png",
        ".pyc",
        ".pyo",
        ".tar",
        ".tgz",
        ".uasset",
        ".ubulk",
        ".udatasmith",
        ".uexp",
        ".umap",
        ".xodr",
        ".zip",
    }
)


def _git(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=repo, stderr=subprocess.DEVNULL)


def _load_private_literals(path: Path) -> tuple[list[str], str]:
    values = {
        unicodedata.normalize("NFC", line.strip()).casefold()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    ordered = sorted(values)
    fingerprint = hashlib.sha256(("\n".join(ordered) + "\n").encode()).hexdigest()
    return ordered, fingerprint


def _contains_private_literal(content: bytes, literals: list[str]) -> bool:
    text = unicodedata.normalize("NFC", content.decode("utf-8", errors="ignore")).casefold()
    return any(literal in text for literal in literals)


def _contains_binary_content(content: bytes) -> bool:
    if b"\0" in content:
        return True
    try:
        content.decode("utf-8")
    except UnicodeDecodeError:
        return True
    return False


def _has_forbidden_public_suffix(path: str) -> bool:
    return Path(path).suffix.casefold() in FORBIDDEN_PUBLIC_SUFFIXES


def _subject_fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _scopes(working_tree: int = 0, git_objects: int = 0, git_refs: int = 0, external_export: int = 0) -> dict:
    return {
        "working_tree": {"files_scanned": working_tree},
        "git_history": {"objects_scanned": git_objects, "refs_scanned": git_refs},
        "external_export": {"files_scanned": external_export},
    }


def _blocked_report(reason_code: str, literals: list[str], literals_sha256: str | None) -> dict:
    return {
        "schema_version": "1.0.0",
        "status": "BLOCKED",
        "reason_code": reason_code,
        "private_literals": {
            "count": len(literals),
            "sha256": literals_sha256 if literals else None,
        },
        "scopes": _scopes(),
        "findings": [],
    }


def _scan_history_objects(
    repo: Path, object_ids: list[str], literals: list[str], approved_blob_ids: frozenset[str] = frozenset()
) -> tuple[list[dict[str, str]], bool]:
    findings: list[dict[str, str]] = []
    process = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=repo,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    if process.stdin is None or process.stdout is None:
        process.kill()
        raise RuntimeError("git cat-file pipes unavailable")
    try:
        for object_id in object_ids:
            process.stdin.write(object_id.encode() + b"\n")
            process.stdin.flush()
            header = process.stdout.readline().split()
            if len(header) != 3:
                raise RuntimeError("unexpected git cat-file header")
            object_type = header[1]
            object_size = int(header[2])
            if object_size > MAX_SCAN_BYTES:
                return [], True
            content = process.stdout.read(object_size)
            separator = process.stdout.read(1)
            if len(content) != object_size or separator != b"\n":
                raise RuntimeError("truncated git cat-file output")
            if _contains_private_literal(content, literals):
                findings.append(
                    {
                        "scope": "git_history",
                        "reason_code": "PUBLICATION-PRIVATE-LITERAL-DETECTED",
                        "subject_sha256": _subject_fingerprint(object_id),
                    }
                )
            if object_type == b"blob" and _contains_binary_content(content) and object_id not in approved_blob_ids:
                findings.append(
                    {
                        "scope": "git_history",
                        "reason_code": "PUBLICATION-BINARY-CONTENT-DETECTED",
                        "subject_sha256": _subject_fingerprint(object_id),
                    }
                )
        process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError("git cat-file failed")
        return findings, False
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()


def audit_repository(repo: Path, private_literals: Path, external_root: Path) -> dict:
    if not private_literals.is_file():
        return _blocked_report("PUBLICATION-PRIVATE-LITERALS-MISSING", [], None)
    if private_literals.stat().st_size > MAX_SCAN_BYTES:
        return _blocked_report("PUBLICATION-SCAN-INPUT-TOO-LARGE", [], None)
    literals, literals_sha256 = _load_private_literals(private_literals)
    if not literals:
        return _blocked_report("PUBLICATION-PRIVATE-LITERALS-EMPTY", literals, literals_sha256)
    if external_root.is_symlink():
        return _blocked_report("PUBLICATION-EXTERNAL-EXPORT-UNSAFE-MEMBER", literals, literals_sha256)
    if not external_root.is_dir():
        return _blocked_report("PUBLICATION-EXTERNAL-EXPORT-MISSING", literals, literals_sha256)
    external_members = sorted(external_root.rglob("*"))
    if any(path.is_symlink() for path in external_members):
        return _blocked_report("PUBLICATION-EXTERNAL-EXPORT-UNSAFE-MEMBER", literals, literals_sha256)
    external_files = [path for path in external_members if path.is_file()]
    if not external_files:
        return _blocked_report("PUBLICATION-EXTERNAL-EXPORT-EMPTY", literals, literals_sha256)
    if any(path.stat().st_size > MAX_SCAN_BYTES for path in external_files):
        return _blocked_report("PUBLICATION-SCAN-INPUT-TOO-LARGE", literals, literals_sha256)
    if _git(repo, "status", "--porcelain=v1", "-z"):
        return _blocked_report("PUBLICATION-WORKTREE-DIRTY", literals, literals_sha256)
    findings: list[dict[str, str]] = []

    tracked_entries = []
    for record in _git(repo, "ls-files", "-s", "-z").split(b"\0"):
        if not record:
            continue
        metadata, encoded_path = record.split(b"\t", 1)
        mode = metadata.split(b" ", 1)[0]
        tracked_entries.append((mode, encoded_path.decode()))
    if any(not mode.startswith(b"100") for mode, _ in tracked_entries):
        return _blocked_report("PUBLICATION-WORKTREE-UNSAFE-ENTRY", literals, literals_sha256)
    tracked_paths = [relative_path for _, relative_path in tracked_entries]
    if any((repo / relative_path).stat().st_size > MAX_SCAN_BYTES for relative_path in tracked_paths):
        return _blocked_report("PUBLICATION-SCAN-INPUT-TOO-LARGE", literals, literals_sha256)
    for relative_path in tracked_paths:
        content = (repo / relative_path).read_bytes()
        approved_media = is_approved_showcase_media(relative_path, content)
        if _has_forbidden_public_suffix(relative_path) and not approved_media:
            findings.append(
                {
                    "scope": "working_tree",
                    "reason_code": "PUBLICATION-FORBIDDEN-ASSET-PATH",
                    "subject_sha256": _subject_fingerprint(relative_path),
                }
            )
        if _contains_binary_content(content) and not approved_media:
            findings.append(
                {
                    "scope": "working_tree",
                    "reason_code": "PUBLICATION-BINARY-CONTENT-DETECTED",
                    "subject_sha256": _subject_fingerprint(relative_path),
                }
            )
        if _contains_private_literal(relative_path.encode(), literals) or _contains_private_literal(content, literals):
            findings.append(
                {
                    "scope": "working_tree",
                    "reason_code": "PUBLICATION-PRIVATE-LITERAL-DETECTED",
                    "subject_sha256": _subject_fingerprint(relative_path),
                }
            )

    approved_blob_ids = frozenset(
        _git(repo, "hash-object", "--", path).decode().strip()
        for path in APPROVED_SHOWCASE_MEDIA
        if (repo / path).is_file() and is_approved_showcase_media(path, (repo / path).read_bytes())
    )
    history_objects: set[str] = set()
    for line in _git(repo, "rev-list", "--objects", "--all").decode().splitlines():
        object_id, *path_parts = line.split(" ", 1)
        history_objects.add(object_id)
        if path_parts and _has_forbidden_public_suffix(path_parts[0]) and not (
            path_parts[0] in APPROVED_SHOWCASE_MEDIA and object_id in approved_blob_ids
        ):
            findings.append(
                {
                    "scope": "git_history",
                    "reason_code": "PUBLICATION-FORBIDDEN-ASSET-PATH",
                    "subject_sha256": _subject_fingerprint(path_parts[0]),
                }
            )
    history_findings, history_too_large = _scan_history_objects(
        repo, sorted(history_objects), literals, approved_blob_ids
    )
    if history_too_large:
        return _blocked_report("PUBLICATION-SCAN-INPUT-TOO-LARGE", literals, literals_sha256)
    findings.extend(history_findings)

    refs = _git(repo, "for-each-ref", "--format=%(refname)").decode().splitlines()
    for ref_name in refs:
        if _contains_private_literal(ref_name.encode(), literals):
            findings.append(
                {
                    "scope": "git_history",
                    "reason_code": "PUBLICATION-PRIVATE-LITERAL-DETECTED",
                    "subject_sha256": _subject_fingerprint(ref_name),
                }
            )

    external_subjects: set[str] = set()
    for path in external_members:
        relative_path = str(path.relative_to(external_root))
        if _contains_private_literal(relative_path.encode(), literals):
            external_subjects.add(relative_path)
    for path in external_files:
        relative_path = str(path.relative_to(external_root))
        content = path.read_bytes()
        if _contains_binary_content(content):
            findings.append(
                {
                    "scope": "external_export",
                    "reason_code": "PUBLICATION-BINARY-CONTENT-DETECTED",
                    "subject_sha256": _subject_fingerprint(relative_path),
                }
            )
        if _contains_private_literal(content, literals):
            external_subjects.add(relative_path)
    findings.extend(
        {
            "scope": "external_export",
            "reason_code": "PUBLICATION-PRIVATE-LITERAL-DETECTED",
            "subject_sha256": _subject_fingerprint(relative_path),
        }
        for relative_path in sorted(external_subjects)
    )

    return {
        "schema_version": "1.0.0",
        "status": "FAIL" if findings else "PASS",
        "private_literals": {"count": len(literals), "sha256": literals_sha256},
        "scopes": _scopes(len(tracked_paths), len(history_objects), len(refs), len(external_files)),
        "findings": findings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit a release candidate without exposing private literals.")
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--private-literals", required=True, type=Path)
    parser.add_argument("--external-root", required=True, type=Path)
    args = parser.parse_args()

    report = audit_repository(args.repo.resolve(), args.private_literals.resolve(), args.external_root.absolute())
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"] == "PASS" else 2)


if __name__ == "__main__":
    main()
