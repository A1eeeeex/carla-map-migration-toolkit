from __future__ import annotations

import json
from collections import Counter, defaultdict

from conftest import REPO_ROOT

ROUTES = {
    "roadrunner-to-source-carla",
    "source-carla-to-package-carla",
    "source-carla-to-ue427",
}


def test_trigger_eval_dataset_has_required_route_coverage():
    payload = json.loads((REPO_ROOT / "evals" / "trigger" / "cases.json").read_text(encoding="utf-8"))
    counts: dict[str, Counter] = defaultdict(Counter)
    ids = set()
    for case in payload["cases"]:
        assert case["id"] not in ids
        ids.add(case["id"])
        expected_skill = case["expected_skill"]
        if case["category"] in {"direct-positive", "indirect-positive"}:
            assert expected_skill in ROUTES
            counts[expected_skill][case["category"]] += 1
            for route in ROUTES - {expected_skill}:
                counts[route]["adjacent-negative"] += 1
        elif case["category"] == "out-of-scope":
            assert expected_skill is None
            assert case["expected_action"] == "do-not-invoke"
            for route in ROUTES:
                counts[route]["out-of-scope"] += 1
        elif case["category"] == "ambiguous":
            assert expected_skill is None
            assert case["expected_action"] == "inspect-only"
            for route in ROUTES:
                counts[route]["ambiguous"] += 1
        else:
            raise AssertionError(f"unknown category: {case['category']}")
    for route in ROUTES:
        assert counts[route]["direct-positive"] >= 10
        assert counts[route]["indirect-positive"] >= 10
        assert counts[route]["adjacent-negative"] >= 8
        assert counts[route]["out-of-scope"] >= 8
        assert counts[route]["ambiguous"] >= 5


def test_behavior_eval_covers_non_negotiable_safety_rules():
    payload = json.loads((REPO_ROOT / "evals" / "behavior" / "cases.json").read_text(encoding="utf-8"))
    rules = {case["rule"] for case in payload["cases"]}
    assert rules >= {
        "missing-facts-inspect-only",
        "plan-before-write",
        "backup-before-replace",
        "context-fast-fail",
        "not-run-is-not-pass",
        "rr-no-package-jump",
        "package-no-raw-map-copy",
        "package-platform-block",
        "ue427-no-os-asset-move",
        "ue427-cold-copy-required",
        "performance-baseline-required",
        "remaining-risk-required",
    }
