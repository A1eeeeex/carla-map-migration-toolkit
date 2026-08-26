from __future__ import annotations

import fnmatch
import posixpath
import re
import stat
import tarfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from .errors import CmtkError

_WINDOWS_ABSOLUTE = re.compile(r"^[A-Za-z]:[/\\]")


def _unsafe_name_reason(name: str) -> str | None:
    portable = name.replace("\\", "/")
    path = PurePosixPath(portable)
    if path.is_absolute() or _WINDOWS_ABSOLUTE.match(name):
        return "PKG-ARCHIVE-UNSAFE-ABSOLUTE"
    if any(part == ".." for part in path.parts):
        return "PKG-ARCHIVE-UNSAFE-TRAVERSAL"
    return None


def _finding(reason_code: str, member: str, message: str) -> dict[str, str]:
    return {"reason_code": reason_code, "member": member, "message": message}


def inspect_archive(
    path: str | Path,
    *,
    required_patterns: list[str] | None = None,
    maximum_expanded_bytes: int = 20 * 1024 * 1024 * 1024,
) -> dict[str, Any]:
    archive_path = Path(path)
    names: list[str] = []
    findings: list[dict[str, str]] = []
    expanded_bytes = 0
    try:
        if tarfile.is_tarfile(archive_path):
            with tarfile.open(archive_path, "r:*") as archive:
                for member in archive.getmembers():
                    names.append(member.name)
                    expanded_bytes += max(member.size, 0)
                    if reason := _unsafe_name_reason(member.name):
                        findings.append(_finding(reason, member.name, "Unsafe archive member path."))
                    if member.issym() or member.islnk():
                        findings.append(
                            _finding("PKG-ARCHIVE-UNSAFE-LINK", member.name, "Links are not accepted in map archives.")
                        )
                    elif not (member.isfile() or member.isdir()):
                        findings.append(
                            _finding(
                                "PKG-ARCHIVE-UNSAFE-SPECIAL",
                                member.name,
                                "Special tar members are not accepted in map archives.",
                            )
                        )
        elif zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path) as archive:
                for member in archive.infolist():
                    names.append(member.filename)
                    expanded_bytes += max(member.file_size, 0)
                    if reason := _unsafe_name_reason(member.filename):
                        findings.append(_finding(reason, member.filename, "Unsafe archive member path."))
                    mode = (member.external_attr >> 16) & 0o170000
                    if mode == stat.S_IFLNK:
                        findings.append(
                            _finding(
                                "PKG-ARCHIVE-UNSAFE-LINK", member.filename, "Links are not accepted in map archives."
                            )
                        )
        else:
            raise CmtkError("PKG-ARCHIVE-INVALID", "Unsupported or invalid archive.", status="FAIL")
    except (OSError, tarfile.TarError, zipfile.BadZipFile) as error:
        raise CmtkError(
            "PKG-ARCHIVE-INVALID",
            "Unable to inspect archive.",
            status="FAIL",
            details={"error": str(error)},
        ) from error

    seen: set[str] = set()
    for name in names:
        normalized = posixpath.normpath(name.replace("\\", "/"))
        if normalized in seen:
            findings.append(_finding("PKG-ARCHIVE-DUPLICATE-MEMBER", name, "Duplicate normalized archive member."))
        seen.add(normalized)
    if expanded_bytes > maximum_expanded_bytes:
        findings.append(
            _finding("PKG-ARCHIVE-EXPANDED-SIZE-EXCEEDED", "", "Declared expanded size exceeds the configured limit.")
        )

    missing: list[str] = []
    for pattern in required_patterns or []:
        if not any(fnmatch.fnmatch(name, pattern) for name in names):
            missing.append(pattern)
            findings.append(_finding("PKG-ARCHIVE-MEMBER-MISSING", pattern, "Required member pattern was not found."))

    unsafe = any(
        item["reason_code"].startswith("PKG-ARCHIVE-UNSAFE")
        or item["reason_code"] in {"PKG-ARCHIVE-DUPLICATE-MEMBER", "PKG-ARCHIVE-EXPANDED-SIZE-EXCEEDED"}
        for item in findings
    )
    status = "BLOCKED" if unsafe else ("FAIL" if missing else "PASS")
    return {
        "schema_version": "1.0.0",
        "status": status,
        "member_count": len(names),
        "expanded_bytes": expanded_bytes,
        "required_patterns": required_patterns or [],
        "missing_patterns": missing,
        "findings": findings,
        "members": names,
        "extracted": False,
    }
