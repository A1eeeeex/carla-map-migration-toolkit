from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "carla-map-migration-toolkit"
SCRIPTS_ROOT = PLUGIN_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))


@pytest.fixture
def workspace_factory(tmp_path: Path):
    def build(route: str) -> dict:
        data_root = tmp_path / "data"
        source_root = tmp_path / "source-carla"
        package_root = tmp_path / "package-carla"
        ue_root = tmp_path / "ue427"
        project_root = tmp_path / "target-project"
        cold_root = tmp_path / "cold-project"
        artifact_root = tmp_path / "artifacts"
        backup_root = tmp_path / "backups"
        for path in (
            data_root,
            source_root,
            package_root,
            ue_root,
            project_root,
            cold_root,
            artifact_root,
            backup_root,
        ):
            path.mkdir(parents=True, exist_ok=True)
        (data_root / "ExampleMap.udatasmith").write_text("anonymous fixture\n", encoding="utf-8")
        (data_root / "ExampleMap.xodr").write_text("<OpenDRIVE/>\n", encoding="utf-8")
        (source_root / "map-handoff.json").write_text('{"schema_version":"1.0.0"}\n', encoding="utf-8")
        (source_root / "source-asset-inventory.json").write_text('{"assets":[]}\n', encoding="utf-8")
        (source_root / "source-dependency-manifest.json").write_text('{"dependencies":[]}\n', encoding="utf-8")
        (source_root / "route-input-manifest.json").write_text('{"route":"source-carla-map"}\n', encoding="utf-8")
        (project_root / "ExampleMap.uproject").write_text("{}\n", encoding="utf-8")
        (cold_root / "ExampleMapCold.uproject").write_text("{}\n", encoding="utf-8")
        allowed = [
            str(data_root),
            str(source_root),
            str(package_root),
            str(ue_root),
            str(project_root),
            str(cold_root),
            str(artifact_root),
            str(backup_root),
        ]
        route_input = (
            {"profile": "roadrunner-datasmith", "root": str(data_root)}
            if route == "roadrunner-to-source-carla"
            else {
                "profile": "source-carla-map",
                "root": str(source_root),
                "handoff_path": str(source_root / "map-handoff.json"),
                "asset_inventory_path": str(source_root / "source-asset-inventory.json"),
                "dependency_manifest_path": str(source_root / "source-dependency-manifest.json"),
                "route_manifest_path": str(source_root / "route-input-manifest.json"),
            }
        )
        return {
            "schema_version": "1.0.0",
            "workspace_id": "anonymous-workspace",
            "route": route,
            "map": {"id": "example-map", "name": "ExampleMap", "mode": "standard"},
            "input": route_input,
            "source_carla": {
                "root": str(source_root),
                "version": "0.9.16",
                "branch": "ue4-dev",
                "commit": "0" * 40,
                "engine_version": "4.26.2-carla-fork",
                "platform": "linux-x86_64",
                "map_asset_path": "/Game/Carla/Maps/ExampleMap/ExampleMap",
                "xodr_path": str(data_root / "ExampleMap.xodr"),
            },
            "package_carla": {
                "root": str(package_root),
                "version": "0.9.16",
                "platform": "linux-x86_64",
                "profile": "content-package",
            },
            "ue427": {
                "engine_root": str(ue_root),
                "engine_version": "4.27.2",
                "uproject": str(project_root / "ExampleMap.uproject"),
                "map_asset_path": "/Game/MAPS/ExampleMap/ExampleMap",
                "profile": "standalone-map",
                "cold_copy_uproject": str(cold_root / "ExampleMapCold.uproject"),
            },
            "execution": {
                "mode": "plan",
                "backup_root": str(backup_root),
                "artifact_root": str(artifact_root),
                "allow_replace_existing": False,
                "allowed_roots": allowed,
            },
            "performance": {"enabled": False, "profile": None},
        }

    return build
