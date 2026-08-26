from __future__ import annotations

import ast
import json
import re

import pytest
from conftest import PLUGIN_ROOT


def _catalog_entries():
    catalog = json.loads((PLUGIN_ROOT / "references" / "reason-codes.json").read_text(encoding="utf-8"))
    return catalog["reason_codes"]


@pytest.mark.parametrize("entry", _catalog_entries(), ids=lambda entry: entry["code"])
def test_each_reason_code_has_a_stable_contract_case(entry):
    assert re.fullmatch(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+", entry["code"])
    assert entry["severity"] in {"info", "warning", "error", "critical"}
    assert entry["repair"] in {"automatic", "review_required", "checkpoint", "no_auto_repair"}
    assert entry["routes"]


def test_reason_code_catalog_is_unique_and_actionable():
    entries = _catalog_entries()
    codes = [entry["code"] for entry in entries]
    assert len(codes) == len(set(codes))
    assert len(codes) >= 60
    assert all(entry["severity"] in {"info", "warning", "error", "critical"} for entry in entries)
    assert all(entry["repair"] in {"automatic", "review_required", "checkpoint", "no_auto_repair"} for entry in entries)
    assert all(entry["routes"] for entry in entries)
    assert "PLAN-STALE" in codes
    assert "UE427-COLD-COPY-FAILED" in codes
    assert "PERF-CONDITIONS-NOT-COMPARABLE" in codes


def test_every_literal_reason_emitted_by_core_is_cataloged():
    catalog = json.loads((PLUGIN_ROOT / "references" / "reason-codes.json").read_text(encoding="utf-8"))
    documented = {entry["code"] for entry in catalog["reason_codes"]}
    emitted = set()
    for path in (PLUGIN_ROOT / "scripts" / "cmtk").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = node.func.id if isinstance(node.func, ast.Name) else None
            if name in {"CmtkError", "_finding"} and node.args:
                value = node.args[0]
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    emitted.add(value.value)
            for keyword in node.keywords:
                if keyword.arg == "reason_code" and isinstance(keyword.value, ast.Constant):
                    if isinstance(keyword.value.value, str):
                        emitted.add(keyword.value.value)
    assert emitted <= documented, f"undocumented emitted codes: {sorted(emitted - documented)}"
