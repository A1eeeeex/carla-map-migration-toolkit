from __future__ import annotations

import io
import tarfile
import zipfile
from pathlib import Path

import pytest
from cmtk.core.archive import inspect_archive


def _write_tar(path: Path, members: list[tuple[str, bytes, str | None]]) -> None:
    with tarfile.open(path, "w:gz") as archive:
        for name, payload, link in members:
            info = tarfile.TarInfo(name)
            if link is not None:
                info.type = tarfile.SYMTYPE
                info.linkname = link
                archive.addfile(info)
            else:
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))


def test_safe_tar_is_inspected_without_extraction(tmp_path: Path):
    archive = tmp_path / "map.tar.gz"
    _write_tar(
        archive,
        [
            ("Package/Maps/ExampleMap/ExampleMap.umap", b"fixture", None),
            ("Package/Maps/ExampleMap/OpenDrive/ExampleMap.xodr", b"<OpenDRIVE/>", None),
        ],
    )
    result = inspect_archive(archive, required_patterns=["*.umap", "*.xodr"])
    assert result["status"] == "PASS"
    assert result["member_count"] == 2
    assert not (tmp_path / "Package").exists()


def test_tar_traversal_and_links_are_blocked(tmp_path: Path):
    archive = tmp_path / "unsafe.tar.gz"
    _write_tar(archive, [("../escape", b"x", None), ("link", b"", "/outside")])
    result = inspect_archive(archive)
    assert result["status"] == "BLOCKED"
    assert {finding["reason_code"] for finding in result["findings"]} >= {
        "PKG-ARCHIVE-UNSAFE-TRAVERSAL",
        "PKG-ARCHIVE-UNSAFE-LINK",
    }


def test_zip_absolute_and_duplicate_members_are_blocked(tmp_path: Path):
    archive = tmp_path / "unsafe.zip"
    with pytest.warns(UserWarning, match="Duplicate name"):
        with zipfile.ZipFile(archive, "w") as output:
            output.writestr("/absolute", "x")
            output.writestr("same", "one")
            output.writestr("same", "two")
    result = inspect_archive(archive)
    assert result["status"] == "BLOCKED"
    codes = {finding["reason_code"] for finding in result["findings"]}
    assert "PKG-ARCHIVE-UNSAFE-ABSOLUTE" in codes
    assert "PKG-ARCHIVE-DUPLICATE-MEMBER" in codes


def test_tar_special_device_member_is_blocked(tmp_path: Path):
    archive_path = tmp_path / "special.tar"
    with tarfile.open(archive_path, "w") as archive:
        info = tarfile.TarInfo("named-pipe")
        info.type = tarfile.FIFOTYPE
        archive.addfile(info)
    result = inspect_archive(archive_path)
    assert result["status"] == "BLOCKED"
    assert "PKG-ARCHIVE-UNSAFE-SPECIAL" in {finding["reason_code"] for finding in result["findings"]}
