import pytest
from cmtk.optimization.comparison import compare_snapshots
from cmtk.optimization.metrics import compare_metrics
from test_performance import _snapshot


def test_invalid_secondary_metric_cannot_hide_behind_primary_improvement():
    baseline, candidate = _snapshot(), _snapshot()
    candidate["metrics"].update(median_frame_ms=15, p95_frame_ms=20)
    baseline["metrics"]["GameThread"] = 3
    candidate["metrics"]["GameThread"] = float("nan")
    result = compare_snapshots(baseline, candidate)
    assert result["status"] == "FAIL"
    assert "PERF-INPUT-INVALID" in result["reason_codes"]


def test_missing_optional_counter_warns_without_failing_primary_metrics():
    baseline, candidate = _snapshot(), _snapshot()
    candidate["metrics"].update(median_frame_ms=15, p95_frame_ms=20)
    baseline["metrics"]["GameThread"] = 3
    result = compare_snapshots(baseline, candidate)
    assert result["status"] == "WARN"
    assert "GameThread" in result["metric_comparison"]["missing_metrics"]


@pytest.mark.parametrize("statistic", ["mean", "median", "p95", "p99", "max"])
def test_nested_statistics_and_regressions_remain_visible(statistic):
    baseline = {"metrics": {"GPU/BasePass": {statistic: 2}, "GameThreadTime": {statistic: 4}}}
    candidate = {"metrics": {"GPU/BasePass": {statistic: 1}, "GameThreadTime": {statistic: 5}}}
    result = compare_metrics(baseline, candidate, statistic=statistic)
    rows = {row["metric"]: row for row in result["rows"]}
    assert rows["GPU/BasePass"]["improvement_percent"] == 50
    assert rows["GameThreadTime"]["improvement_percent"] == -25
    assert result["regressions"] == ["GameThreadTime"]
    assert result["optimization_acceptance"] == "NOT_RUN"


def test_zero_baseline_direction_and_missing_counters():
    result = compare_metrics({"GPUTime": 0, "FPS": 30}, {"GPUTime": 2, "FPS": 60, "RAM": 4})
    rows = {row["metric"]: row for row in result["rows"]}
    assert rows["GPUTime"]["improvement_percent"] is None
    assert rows["GPUTime"]["change"] == "regressed"
    assert rows["FPS"]["improvement_percent"] == 100
    assert result["missing_metrics"] == ["RAM"]


@pytest.mark.parametrize("invalid", [True, float("nan"), float("inf"), -1, "3", 10**1000])
def test_invalid_counters_do_not_look_like_improvement(invalid):
    assert compare_metrics({"GPUTime": 2}, {"GPUTime": invalid})["status"] == "FAIL"


def test_missing_counter_does_not_hide_an_invalid_value_on_the_other_side():
    result = compare_metrics({"GPUTime": 2}, {"GPUTime": 1, "GameThread": True})
    assert result["status"] == "FAIL"
    assert result["invalid_metrics"] == ["GameThread"]


def test_empty_overlap_is_failure():
    assert compare_metrics({"GPUTime": 2}, {"OtherTime": 1})["status"] == "FAIL"


def test_secondary_regression_is_not_hidden_by_better_frame_times():
    baseline, candidate = _snapshot(), _snapshot()
    candidate["metrics"].update(median_frame_ms=15, p95_frame_ms=18)
    baseline["metrics"]["game_thread_ms"] = 3
    candidate["metrics"]["game_thread_ms"] = 5
    result = compare_snapshots(baseline, candidate)
    assert result["status"] == "WARN"
    assert "PERF-SECONDARY-REGRESSION" in result["reason_codes"]
    assert result["metric_comparison"]["regressions"] == ["game_thread_ms"]


def test_diagnostic_deltas_do_not_approve_mismatched_conditions():
    result = compare_metrics(
        {"metrics": {"GPUTime": 4}, "conditions": {"quality": "Epic"}},
        {"metrics": {"GPUTime": 2}, "conditions": {"quality": "Low"}},
    )
    assert result["supplied_conditions_equal"] is False
    assert result["optimization_acceptance"] == "NOT_RUN"
