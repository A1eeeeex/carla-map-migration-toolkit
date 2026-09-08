from __future__ import annotations

import json
from pathlib import Path

from conftest import REPO_ROOT


def test_golden_map_plan_is_text_only_and_covers_required_faults():
    root = REPO_ROOT / "demo" / "golden-map"
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["public_tier"] == "public-golden-map-lite"
    assert manifest["rights"]["status"] == "REVIEW_REQUIRED"
    assert {variant["id"] for variant in manifest["failure_variants"]} == {
        "GM-F01",
        "GM-F02",
        "GM-F03",
        "GM-F04",
        "GM-F05",
        "GM-F06",
        "GM-F07",
        "GM-F08",
    }
    assert all(variant["reason_code"] and variant["expected_status"] for variant in manifest["failure_variants"])
    forbidden = {".uasset", ".umap", ".uexp", ".ubulk", ".xodr", ".fbx", ".udatasmith"}
    assert not any(Path(path).suffix.lower() in forbidden for path in manifest["public_files"])
    assert manifest["private_files"] == []
