from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Iterable

from .errors import CmtkError
from .hashing import sha256_file
from .jsonio import write_json_atomic
from .paths import require_within_roots

_BACKUP_ID = re.compile(r"^backup-\d{8}T\d{6}Z-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")
_UNREAL_BINARY_SUFFIXES = {".uasset", ".umap", ".uexp", ".ubulk"}


def backup_files(
    paths: Iterable[str | Path],
    *,
    source_root: str | Path,
    backup_root: str | Path,
    backup_id: str,
    allowed_roots: Iterable[str | Path],
) -> dict:
    """Back up an explicit list of ordinary files and emit a hash manifest.

    Unreal binary assets are intentionally rejected because they must be handled
    through engine-aware migration or project-level backup workflows.
    """

    if not _BACKUP_ID.fullmatch(backup_id):
        raise CmtkError("BACKUP-ID-INVALID", "Backup ID must contain a UTC timestamp and a safe suffix.")
    requested_paths = list(paths)
    if not requested_paths:
        raise CmtkError("BACKUP-SOURCE-EMPTY", "At least one explicit file is required for a backup.")
    allowed = list(allowed_roots)
    resolved_source_root = require_within_roots(source_root, allowed)
    resolved_backup_root = require_within_roots(backup_root, allowed)
    resolved_paths: list[tuple[Path, Path]] = []
    for value in requested_paths:
        source = require_within_roots(value, [resolved_source_root])
        if source.suffix.lower() in _UNREAL_BINARY_SUFFIXES:
            raise CmtkError(
                "UNREAL-RAW-FILE-OPERATION-FORBIDDEN",
                "Unreal binary assets must not be copied by the host backup helper.",
                details={"suffix": source.suffix.lower()},
            )
        if not source.is_file():
            raise CmtkError("BACKUP-SOURCE-INVALID", "Backup source is not a regular file.")
        resolved_paths.append((source, source.relative_to(resolved_source_root)))

    destination_root = require_within_roots(resolved_backup_root / backup_id, [resolved_backup_root])
    if destination_root.exists():
        raise CmtkError("BACKUP-TARGET-EXISTS", "Backup target already exists.")
    destination_root.mkdir(parents=True)

    entries = []
    try:
        for source, relative in resolved_paths:
            destination = require_within_roots(destination_root / relative, [destination_root])
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            source_hash = sha256_file(source)
            destination_hash = sha256_file(destination)
            if source_hash != destination_hash:
                raise CmtkError("BACKUP-VERIFY-FAILED", "Backup copy hash does not match its source.")
            entries.append(
                {
                    "relative_path": relative.as_posix(),
                    "source_sha256": source_hash,
                    "backup_sha256": destination_hash,
                    "size_bytes": source.stat().st_size,
                }
            )
    except CmtkError:
        raise
    except OSError as error:
        raise CmtkError(
            "BACKUP-CREATE-FAILED", "Unable to create a verified backup.", details={"error": str(error)}
        ) from error

    manifest = {
        "schema_version": "1.0.0",
        "status": "PASS",
        "backup_id": backup_id,
        "source_root": str(resolved_source_root),
        "backup_root": str(destination_root),
        "files": entries,
        "rollback": "Restore only listed files after verifying their backup_sha256 values.",
    }
    write_json_atomic(destination_root / "backup-manifest.json", manifest)
    return manifest
