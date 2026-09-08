from __future__ import annotations

import os
import re
import stat
from pathlib import Path, PurePosixPath
from typing import Any

from .archive import inspect_archive
from .errors import CmtkError
from .hashing import sha256_file

ASSET_SUFFIXES = {".umap", ".uasset", ".uexp", ".ubulk"}
_PACKAGE_PATH = re.compile(r"[A-Za-z0-9_]+(?:/[A-Za-z0-9_]+)*")
_GENERATED = {"saved", "intermediate", "deriveddatacache", "binaries", "plugins", "source", "config", ".vs"}


def package_relative(value: str) -> str:
    if not _PACKAGE_PATH.fullmatch(value):
        raise CmtkError("DELIVERY-INPUT-INVALID", "Use a relative Unreal package path with exact case.")
    return value


def _normalized(name: str) -> str:
    return PurePosixPath(name.replace("\\", "/")).as_posix()


def inventory_tree(target: Path) -> dict[str, Any]:
    """Inventory regular files without following links or interpreting UE assets."""
    files: list[dict[str, Any]] = []
    members: list[str] = []
    findings: list[dict[str, str]] = []
    if target.is_symlink():
        raise CmtkError("PKG-ARCHIVE-UNSAFE-LINK", "Delivery root cannot be a symbolic link.")

    def onerror(error: OSError) -> None:
        raise error

    try:
        for directory, dirs, names in os.walk(target, followlinks=False, onerror=onerror):
            for name in sorted(dirs + names):
                path = Path(directory) / name
                relative = path.relative_to(target).as_posix()
                members.append(relative)
                info = path.lstat()
                if stat.S_ISLNK(info.st_mode):
                    findings.append({"reason_code": "PKG-ARCHIVE-UNSAFE-LINK", "member": relative})
                elif stat.S_ISREG(info.st_mode):
                    files.append({"path": relative, "bytes": info.st_size})
                elif not stat.S_ISDIR(info.st_mode):
                    findings.append({"reason_code": "PKG-ARCHIVE-UNSAFE-SPECIAL", "member": relative})
    except OSError as error:
        raise CmtkError("DELIVERY-INPUT-INVALID", "Unable to inspect delivery tree.") from error
    return {
        "status": "BLOCKED" if findings else "PASS",
        "members": sorted(members),
        "files": sorted(files, key=lambda item: item["path"]),
        "findings": findings,
        "expanded_bytes": sum(item["bytes"] for item in files),
        "extracted": False,
    }


def _inventory(target: Path, maximum_expanded_bytes: int) -> dict[str, Any]:
    if target.is_symlink():
        raise CmtkError("PKG-ARCHIVE-UNSAFE-LINK", "Delivery target cannot be a symbolic link.")
    if not target.exists():
        raise CmtkError("DELIVERY-INPUT-INVALID", "Delivery target does not exist.")
    result = (
        inventory_tree(target)
        if target.is_dir()
        else inspect_archive(target, maximum_expanded_bytes=maximum_expanded_bytes)
    )
    if target.is_dir() and result["expanded_bytes"] > maximum_expanded_bytes:
        result["findings"].append({"reason_code": "PKG-ARCHIVE-EXPANDED-SIZE-EXCEEDED", "member": ""})
        result["status"] = "BLOCKED"
    return result


def audit_delivery(
    target: str | Path,
    *,
    kind: str,
    map_name: str,
    asset_root: str | None = None,
    require_cooked_sidecars: bool = False,
    expected_sha256: str | None = None,
    maximum_expanded_bytes: int = 20 * 1024**3,
) -> dict[str, Any]:
    target = Path(target)
    package_relative(map_name)
    if "/" in map_name or kind not in {"content", "carla"} or maximum_expanded_bytes <= 0:
        raise CmtkError("DELIVERY-INPUT-INVALID", "Select a map basename, delivery kind and positive size limit.")
    if kind == "content":
        asset_root = package_relative(asset_root or "")
    if expected_sha256 is not None and (not re.fullmatch(r"[a-fA-F0-9]{64}", expected_sha256) or not target.is_file()):
        raise CmtkError("DELIVERY-INPUT-INVALID", "Expected SHA256 requires an archive and a 64-digit digest.")
    inventory = _inventory(target, maximum_expanded_bytes)
    content_directory = kind == "content" and target.is_dir() and target.name == "Content"
    prefix = "Content/" if content_directory else ""
    files = [dict(item, path=prefix + _normalized(item["path"])) for item in inventory["files"]]
    members = [prefix + _normalized(name) for name in inventory["members"]]
    names = {item["path"] for item in files}
    maps = sorted(name for name in names if PurePosixPath(name).suffix.lower() == ".umap")
    checks = {"safe_members": inventory["status"] != "BLOCKED", "files_present": bool(files)}
    observations: dict[str, Any] = {}
    if kind == "content":
        expected = f"Content/{asset_root}/{map_name}.umap"
        selected = expected if expected in names else None
        outside = sorted(name for name in names if not name.startswith(f"Content/{asset_root}/"))
        checks.update(
            {
                "only_content_top_level": all(name.split("/")[0] == "Content" for name in members),
                "no_double_content": not any(name.casefold().startswith("content/content/") for name in members),
                "no_project_or_cache_files": not any(
                    _GENERATED.intersection(part.casefold() for part in PurePosixPath(name).parts)
                    or PurePosixPath(name).suffix.lower() == ".uproject"
                    for name in members
                ),
                "only_unreal_package_files": all(
                    PurePosixPath(name).suffix.lower() in ASSET_SUFFIXES for name in names
                ),
                "within_asset_root": not outside,
                "expected_map_found": selected is not None,
            }
        )
        observations["outside_asset_root"] = outside
    else:
        matches = [name for name in maps if PurePosixPath(name).stem == map_name]
        selected = matches[0] if len(matches) == 1 else None
        xodrs = sorted(name for name in names if PurePosixPath(name).name == f"{map_name}.xodr")
        checks.update({"expected_map_found": selected is not None, "matching_xodr_found": len(xodrs) == 1})
        if require_cooked_sidecars:
            checks["cooked_map_sidecar_found"] = bool(
                selected and str(PurePosixPath(selected).with_suffix(".uexp")) in names
            )
        groups = {
            "geometry": {"geometry", "geometries", "mesh", "meshes"},
            "materials": {"material", "materials"},
            "textures": {"texture", "textures"},
        }
        # Folder labels are diagnostic hints; they cannot establish asset classes or dependency closure.
        observations["asset_folder_hints"] = {
            group: any(
                PurePosixPath(name).suffix.lower() == ".uasset"
                and terms.intersection(part.casefold() for part in PurePosixPath(name).parts[:-1])
                for name in names
            )
            for group, terms in groups.items()
        }
        observations["matching_xodrs"] = xodrs
    try:
        archive_hash = sha256_file(target) if target.is_file() and checks["safe_members"] else None
    except OSError as error:
        raise CmtkError("DELIVERY-INPUT-INVALID", "Unable to hash delivery archive.") from error
    if expected_sha256 is not None:
        checks["expected_sha256"] = archive_hash == expected_sha256.lower()
    reasons = sorted({item["reason_code"] for item in inventory["findings"]})
    if not all(checks.values()):
        reasons.append("DELIVERY-CONTENT-INCOMPLETE")
    status = "BLOCKED" if inventory["status"] == "BLOCKED" else ("PASS" if all(checks.values()) else "FAIL")
    if status == "PASS" and kind == "carla" and not all(observations["asset_folder_hints"].values()):
        status = "WARN"
        reasons.append("DELIVERY-ASSET-CATEGORIES-UNCONFIRMED")
    return {
        "schema_version": "1.0.0",
        "report_type": "delivery-audit",
        "status": status,
        "execution_context": "host-cpython",
        "kind": kind,
        "checks": checks,
        "reason_codes": reasons,
        "archive_sha256": archive_hash,
        "selected_map": selected,
        "map_candidates": maps,
        "file_count": len(files),
        "expanded_bytes": inventory["expanded_bytes"],
        "ue_asset_count": sum(PurePosixPath(name).suffix.lower() in {".umap", ".uasset"} for name in names),
        "files": files,
        "findings": inventory["findings"],
        "observations": observations,
        "extracted": False,
        "runtime_validation": "NOT_RUN",
        "limitations": [
            "File structure does not prove UE dependency closure, rendering, lane alignment or cold-copy acceptance."
        ],
    }


def build_delivery_manifest(content: str | Path, *, map_package: str, engine_version: str) -> dict[str, Any]:
    content = Path(content)
    if not content.is_dir() or content.name != "Content" or not map_package.startswith("/Game/"):
        raise CmtkError("DELIVERY-INPUT-INVALID", "Use an existing Content directory and an exact /Game/ map package.")
    relative = package_relative(map_package[len("/Game/") :])
    if not re.fullmatch(r"4\.27\.\d+", engine_version):
        raise CmtkError("DELIVERY-INPUT-INVALID", "Specify the exact UE4.27 patch, for example 4.27.2.")
    inventory = inventory_tree(content)
    if inventory["status"] != "PASS":
        raise CmtkError("DELIVERY-CONTENT-INCOMPLETE", "Content tree has links or special files.")
    names = {item["path"] for item in inventory["files"]}
    if any(
        name.split("/")[0].casefold() == "content"
        or _GENERATED.intersection(part.casefold() for part in PurePosixPath(name).parts)
        for name in inventory["members"]
    ):
        raise CmtkError("DELIVERY-CONTENT-INCOMPLETE", "Content contains nested Content or generated directories.")
    if relative + ".umap" not in names or any(
        PurePosixPath(name).suffix.lower() not in ASSET_SUFFIXES for name in names
    ):
        raise CmtkError("DELIVERY-CONTENT-INCOMPLETE", "Map is absent or Content contains non-package files.")
    files = []
    try:
        for item in inventory["files"]:
            path = content / item["path"]
            before = path.lstat()
            if not stat.S_ISREG(before.st_mode):
                raise CmtkError("DELIVERY-INPUT-INVALID", "File changed type during inventory.")
            digest = sha256_file(path)
            after = path.lstat()
            if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
                raise CmtkError("DELIVERY-INPUT-INVALID", "File changed during hashing; close the producer and retry.")
            files.append({"path": "Content/" + item["path"], "bytes": after.st_size, "sha256": digest})
    except OSError as error:
        raise CmtkError("DELIVERY-INPUT-INVALID", "Unable to hash delivery file.") from error
    if inventory_tree(content) != inventory:
        raise CmtkError("DELIVERY-INPUT-INVALID", "Delivery tree changed during hashing; close the producer and retry.")
    return {
        "schema_version": "1.0.0",
        "report_type": "delivery-manifest",
        "status": "PASS",
        "execution_context": "host-cpython",
        "engine_version": engine_version,
        "map_package": map_package,
        "file_count": len(files),
        "total_bytes": sum(item["bytes"] for item in files),
        "files": files,
        "runtime_validation": "NOT_RUN",
    }
