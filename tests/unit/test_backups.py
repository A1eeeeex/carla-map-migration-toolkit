from __future__ import annotations

from pathlib import Path

import pytest
from cmtk.core.backups import backup_files
from cmtk.core.errors import CmtkError


def test_backup_copies_only_explicit_non_unreal_files_and_writes_manifest(tmp_path: Path):
    source_root = tmp_path / "source"
    backup_root = tmp_path / "backups"
    source_root.mkdir()
    backup_root.mkdir()
    first = source_root / "Package.json"
    second = source_root / "Config.ini"
    first.write_text("{}\n", encoding="utf-8")
    second.write_text("fixture\n", encoding="utf-8")

    manifest = backup_files(
        [first, second],
        source_root=source_root,
        backup_root=backup_root,
        backup_id="backup-20260826T120000Z-fixture",
        allowed_roots=[source_root, backup_root],
    )

    assert manifest["status"] == "PASS"
    assert manifest["backup_id"] == "backup-20260826T120000Z-fixture"
    assert {item["relative_path"] for item in manifest["files"]} == {"Package.json", "Config.ini"}
    assert (backup_root / "backup-20260826T120000Z-fixture" / "Package.json").read_text(encoding="utf-8") == "{}\n"
    assert (backup_root / "backup-20260826T120000Z-fixture" / "backup-manifest.json").is_file()


@pytest.mark.parametrize("suffix", [".uasset", ".umap", ".uexp", ".ubulk"])
def test_backup_refuses_raw_unreal_binary_copy(tmp_path: Path, suffix: str):
    source_root = tmp_path / "source"
    backup_root = tmp_path / "backups"
    source_root.mkdir()
    backup_root.mkdir()
    asset = source_root / f"Asset{suffix}"
    asset.write_bytes(b"fixture")
    with pytest.raises(CmtkError) as error:
        backup_files(
            [asset],
            source_root=source_root,
            backup_root=backup_root,
            backup_id="backup-20260826T120000Z-fixture",
            allowed_roots=[source_root, backup_root],
        )
    assert error.value.reason_code == "UNREAL-RAW-FILE-OPERATION-FORBIDDEN"


def test_backup_requires_timestamped_id_and_nonempty_source_list(tmp_path: Path):
    source_root = tmp_path / "source"
    backup_root = tmp_path / "backups"
    source_root.mkdir()
    backup_root.mkdir()
    with pytest.raises(CmtkError) as unsafe_id:
        backup_files(
            [],
            source_root=source_root,
            backup_root=backup_root,
            backup_id="backup-fixture",
            allowed_roots=[source_root, backup_root],
        )
    assert unsafe_id.value.reason_code == "BACKUP-ID-INVALID"
    with pytest.raises(CmtkError) as empty:
        backup_files(
            [],
            source_root=source_root,
            backup_root=backup_root,
            backup_id="backup-20260826T120000Z-fixture",
            allowed_roots=[source_root, backup_root],
        )
    assert empty.value.reason_code == "BACKUP-SOURCE-EMPTY"
