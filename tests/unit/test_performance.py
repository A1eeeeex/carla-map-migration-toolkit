from cmtk.optimization.comparison import compare_snapshots


def _snapshot(sample_frames: int = 300) -> dict:
    return {
        "schema_version": "1.0.0",
        "conditions": {
            "hardware_id": "fixture-host",
            "os": "linux-x86_64",
            "target_profile": "ue427-standalone",
            "resolution": "1280x720",
            "quality": "Epic",
            "camera_profile_sha256": "a" * 64,
            "traffic_profile_sha256": "1" * 64,
            "sensor_profile_sha256": "2" * 64,
            "warmup_frames": 60,
            "sample_frames": sample_frames,
            "repeats": 3,
            "vsync": False,
            "fps_cap": 0,
        },
        "metrics": {"median_frame_ms": 20.0, "p95_frame_ms": 25.0},
        "protected": {
            "lod0_sha256": "b" * 64,
            "material_slots_sha256": "c" * 64,
            "transforms_sha256": "d" * 64,
            "collision_sha256": "e" * 64,
            "xodr_sha256": "f" * 64,
        },
    }


def test_performance_conditions_must_match():
    baseline = _snapshot()
    candidate = _snapshot(sample_frames=180)
    result = compare_snapshots(baseline, candidate)
    assert result["status"] == "FAIL"
    assert "PERF-CONDITIONS-NOT-COMPARABLE" in result["reason_codes"]


def test_protected_property_change_fails_even_when_faster():
    baseline = _snapshot()
    candidate = _snapshot()
    candidate["metrics"]["median_frame_ms"] = 10.0
    candidate["protected"]["transforms_sha256"] = "0" * 64
    result = compare_snapshots(baseline, candidate)
    assert result["status"] == "FAIL"
    assert "PERF-TRANSFORM-CHANGED" in result["reason_codes"]


def test_comparable_non_regressing_improvement_passes():
    baseline = _snapshot()
    candidate = _snapshot()
    candidate["metrics"]["median_frame_ms"] = 15.0
    candidate["metrics"]["p95_frame_ms"] = 18.0
    result = compare_snapshots(baseline, candidate)
    assert result["status"] == "PASS"
    assert result["median_frame_time_improvement_percent"] == 25.0


def test_missing_protected_evidence_cannot_pass():
    baseline = _snapshot()
    candidate = _snapshot()
    baseline["protected"].pop("collision_sha256")
    candidate["protected"].pop("collision_sha256")
    candidate["metrics"]["median_frame_ms"] = 15.0
    result = compare_snapshots(baseline, candidate)
    assert result["status"] == "FAIL"
    assert "PERF-PROTECTED-EVIDENCE-MISSING" in result["reason_codes"]


def test_p95_regression_fails_even_when_median_improves():
    baseline = _snapshot()
    candidate = _snapshot()
    candidate["metrics"]["median_frame_ms"] = 15.0
    candidate["metrics"]["p95_frame_ms"] = 40.0
    result = compare_snapshots(baseline, candidate)
    assert result["status"] == "FAIL"
    assert "PERF-P95-REGRESSION" in result["reason_codes"]


def test_incomplete_conditions_cannot_pass_even_when_both_snapshots_match():
    baseline = _snapshot()
    candidate = _snapshot()
    baseline["conditions"].pop("traffic_profile_sha256")
    candidate["conditions"].pop("traffic_profile_sha256")
    candidate["metrics"]["median_frame_ms"] = 15.0
    result = compare_snapshots(baseline, candidate)
    assert result["status"] == "FAIL"
    assert "PERF-CONDITIONS-INCOMPLETE" in result["reason_codes"]


def test_invalid_condition_hash_cannot_pass():
    baseline = _snapshot()
    candidate = _snapshot()
    baseline["conditions"]["sensor_profile_sha256"] = "not-a-hash"
    candidate["conditions"]["sensor_profile_sha256"] = "not-a-hash"
    result = compare_snapshots(baseline, candidate)
    assert result["status"] == "FAIL"
    assert "PERF-CONDITIONS-INVALID" in result["reason_codes"]


def test_invalid_protected_hash_cannot_pass():
    baseline = _snapshot()
    candidate = _snapshot()
    baseline["protected"]["lod0_sha256"] = "not-a-hash"
    candidate["protected"]["lod0_sha256"] = "not-a-hash"
    result = compare_snapshots(baseline, candidate)
    assert result["status"] == "FAIL"
    assert "PERF-PROTECTED-EVIDENCE-INVALID" in result["reason_codes"]


def test_non_positive_frame_time_is_invalid():
    baseline = _snapshot()
    candidate = _snapshot()
    candidate["metrics"]["median_frame_ms"] = -1.0
    result = compare_snapshots(baseline, candidate)
    assert result["status"] == "FAIL"
    assert "PERF-METRIC-MISSING" in result["reason_codes"]


def test_malformed_snapshot_sections_return_failure_instead_of_crashing():
    baseline = _snapshot()
    candidate = _snapshot()
    baseline["protected"] = []
    candidate["metrics"] = "invalid"
    result = compare_snapshots(baseline, candidate)
    assert result["status"] == "FAIL"
    assert "PERF-INPUT-INVALID" in result["reason_codes"]
