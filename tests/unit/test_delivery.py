from __future__ import annotations

import hashlib
import json
import stat
import tarfile
import zipfile

import pytest
from cmtk.cli import run
from cmtk.core.archive import inspect_archive
from cmtk.core.delivery import audit_delivery, build_delivery_manifest
from cmtk.core.errors import CmtkError


def _content(root):
    content = root / "Content"
    for name in ("MAPS/Example/ExampleMap.umap", "MAPS/Example/MESH/Road.uasset"):
        path = content / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(name.encode())
    return content


def _audit(target, **kwargs):
    return audit_delivery(target, kind="content", map_name="ExampleMap", asset_root="MAPS/Example", **kwargs)


@pytest.mark.parametrize("scope", ["content", "project", "tar", "zip"])
def test_content_layout_and_real_file_count(tmp_path, scope):
    content = _content(tmp_path)
    target = content if scope == "content" else tmp_path
    if scope in {"tar", "zip"}:
        target = tmp_path / ("delivery.tar.gz" if scope == "tar" else "delivery.zip")
        if scope == "tar":
            with tarfile.open(target, "w:gz") as archive:
                archive.add(content, arcname="Content")
        else:
            with zipfile.ZipFile(target, "w") as archive:
                for path in content.rglob("*"):
                    if path.is_file():
                        archive.write(path, path.relative_to(tmp_path))
    report = _audit(target)
    assert report["status"] == "PASS"
    assert report["ue_asset_count"] == 2
    assert report["runtime_validation"] == "NOT_RUN"
    assert not report["extracted"]


@pytest.mark.parametrize(
    "relative", ["Content/Content/x.uasset", "Saved/cache", "Project.uproject", "Content/Other/a.uasset"]
)
def test_delivery_rejects_wrong_roots_and_project_junk(tmp_path, relative):
    _content(tmp_path)
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("fixture")
    result = _audit(tmp_path)
    assert result["status"] == "FAIL"
    assert "DELIVERY-CONTENT-INCOMPLETE" in result["reason_codes"]


@pytest.mark.parametrize("kind", ["symlink", "directory-link", "hardlink", "fifo", "traversal", "drive", "duplicate"])
def test_archive_attack_members_cannot_disappear_from_audit(tmp_path, kind):
    content = _content(tmp_path)
    target = tmp_path / "bad.tar"
    with tarfile.open(target, "w") as archive:
        archive.add(content, arcname="Content")
        member = tarfile.TarInfo("Content/unsafe")
        if kind in {"symlink", "directory-link", "hardlink"}:
            member.type = tarfile.LNKTYPE if kind == "hardlink" else tarfile.SYMTYPE
            member.linkname = "outside"
        elif kind == "fifo":
            member.type = tarfile.FIFOTYPE
        else:
            member.name = {
                "traversal": "../escape",
                "drive": "C:/escape",
                "duplicate": "Content/MAPS/Example/ExampleMap.umap",
            }[kind]
        archive.addfile(member)
    assert _audit(target)["status"] == "BLOCKED"


@pytest.mark.parametrize("mode", [stat.S_IFLNK, stat.S_IFIFO])
def test_zip_link_or_special_file_blocked(tmp_path, mode):
    target = tmp_path / "bad.zip"
    with zipfile.ZipFile(target, "w") as archive:
        info = zipfile.ZipInfo("Content/link")
        info.create_system = 3
        info.external_attr = (mode | 0o777) << 16
        archive.writestr(info, "outside")
    assert _audit(target)["status"] == "BLOCKED"


def test_directory_links_are_not_followed_or_hashed(tmp_path):
    content = _content(tmp_path)
    external = tmp_path / "elsewhere"
    external.mkdir()
    (content / "MAPS/Example/link").symlink_to(external, target_is_directory=True)
    assert _audit(content)["status"] == "BLOCKED"
    with pytest.raises(CmtkError, match="links"):
        build_delivery_manifest(content, map_package="/Game/MAPS/Example/ExampleMap", engine_version="4.27.2")


def test_directory_named_map_does_not_satisfy_archive_requirement(tmp_path):
    target = tmp_path / "empty.tar"
    with tarfile.open(target, "w") as archive:
        member = tarfile.TarInfo("ExampleMap.umap")
        member.type = tarfile.DIRTYPE
        archive.addfile(member)
    assert inspect_archive(target, required_patterns=["*.umap"])["status"] == "FAIL"


def test_zip_directory_mode_without_trailing_slash_is_not_a_map(tmp_path):
    target = tmp_path / "empty.zip"
    with zipfile.ZipFile(target, "w") as archive:
        member = zipfile.ZipInfo("ExampleMap.umap")
        member.create_system = 3
        member.external_attr = (stat.S_IFDIR | 0o755) << 16
        archive.writestr(member, "")
    assert inspect_archive(target, required_patterns=["*.umap"])["status"] == "FAIL"


def test_carla_map_xodr_sidecar_and_folder_evidence(tmp_path):
    for name in (
        "ExampleMap.umap",
        "ExampleMap.uexp",
        "OpenDrive/ExampleMap.xodr",
        "MESH/Road.uasset",
        "MATERIAL/Road.uasset",
        "TEXTURE/Road.uasset",
    ):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"fixture")
    kwargs = dict(kind="carla", map_name="ExampleMap", require_cooked_sidecars=True)
    assert audit_delivery(tmp_path, **kwargs)["status"] == "PASS"
    (tmp_path / "ExampleMap.uexp").unlink()
    assert not audit_delivery(tmp_path, **kwargs)["checks"]["cooked_map_sidecar_found"]
    (tmp_path / "OpenDrive/ExampleMap.xodr").rename(tmp_path / "OpenDrive/Stale.xodr")
    assert not audit_delivery(tmp_path, **kwargs)["checks"]["matching_xodr_found"]


def test_folder_labels_are_not_dependency_proof(tmp_path):
    (tmp_path / "ExampleMap.umap").write_bytes(b"map")
    (tmp_path / "ExampleMap.xodr").write_bytes(b"xodr")
    result = audit_delivery(tmp_path, kind="carla", map_name="ExampleMap")
    assert result["status"] == "WARN"
    assert "DELIVERY-ASSET-CATEGORIES-UNCONFIRMED" in result["reason_codes"]


def test_map_manifest_is_deterministic_and_exact(tmp_path):
    content = _content(tmp_path)
    kwargs = dict(map_package="/Game/MAPS/Example/ExampleMap", engine_version="4.27.2")
    report = build_delivery_manifest(content, **kwargs)
    assert report == build_delivery_manifest(content, **kwargs)
    assert report["file_count"] == 2
    assert report["files"] == sorted(report["files"], key=lambda item: item["path"])
    for item in report["files"]:
        assert item["sha256"] == hashlib.sha256((tmp_path / item["path"]).read_bytes()).hexdigest()
    with pytest.raises(CmtkError, match="Map is absent"):
        build_delivery_manifest(content, map_package="/Game/Absent", engine_version="4.27.2")


@pytest.mark.parametrize("root", ["../Example", "/MAPS/Example", "C:/Example", "MAPS/../Example", ""])
def test_invalid_asset_root_is_rejected(tmp_path, root):
    with pytest.raises(CmtkError):
        audit_delivery(tmp_path, kind="content", map_name="ExampleMap", asset_root=root)


@pytest.mark.parametrize("directory", ["Content", "Saved", "DerivedDataCache"])
def test_manifest_rejects_nested_or_generated_directories(tmp_path, directory):
    content = _content(tmp_path)
    (content / directory).mkdir()
    with pytest.raises(CmtkError, match="generated directories"):
        build_delivery_manifest(content, map_package="/Game/MAPS/Example/ExampleMap", engine_version="4.27.2")


def test_cli_can_separate_input_and_report_roots(tmp_path, monkeypatch, capsys):
    source = tmp_path / "input"
    report_root = tmp_path / "reports"
    content = _content(source)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "host-cpython")
    args = [
        "content-audit",
        "--target",
        str(content),
        "--allowed-root",
        str(source),
        "--allowed-root",
        str(report_root),
        "--map-name",
        "ExampleMap",
        "--asset-root",
        "MAPS/Example",
        "--output",
        str(report_root / "audit.json"),
    ]
    assert run(args) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "PASS"


def test_digest_and_size_checks(tmp_path):
    content = _content(tmp_path)
    target = tmp_path / "delivery.tar"
    with tarfile.open(target, "w") as archive:
        archive.add(content, arcname="Content")
    assert not _audit(target, expected_sha256="0" * 64)["checks"]["expected_sha256"]
    assert _audit(target, maximum_expanded_bytes=1)["status"] == "BLOCKED"


def test_cli_context_output_boundary_and_no_overwrite(tmp_path, monkeypatch, capsys):
    content = _content(tmp_path)
    args = [
        "delivery-manifest",
        "--content",
        str(content),
        "--allowed-root",
        str(tmp_path),
        "--map-package",
        "/Game/MAPS/Example/ExampleMap",
        "--engine-version",
        "4.27.2",
    ]
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "ue427-unreal-python")
    with pytest.raises(CmtkError):
        run(args)
    monkeypatch.setenv("CMTK_EXECUTION_CONTEXT", "host-cpython")
    with pytest.raises(CmtkError, match="outside"):
        run(args + ["--output", str(content / "manifest.json")])
    output = tmp_path / "manifest.json"
    assert run(args + ["--output", str(output)]) == 0
    assert json.loads(capsys.readouterr().out)["file_count"] == 2
    with pytest.raises(CmtkError, match="already exists"):
        run(args + ["--output", str(output)])
