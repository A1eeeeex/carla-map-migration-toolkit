from pathlib import Path

import pytest
from cmtk.core.errors import CmtkError
from cmtk.core.hashing import sha256_bytes
from cmtk.validation.verified import (
    _load_structured_evidence,
    _read_evidence_bytes,
    _require_repository_relative_path,
    aggregate_required_checks,
)


@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        (["PASS", "PASS"], "PASS"),
        (["PASS", "WARN"], "PASS_WITH_WARNINGS"),
        (["PASS", "NOT_RUN"], "INCOMPLETE"),
        (["PASS", "FAIL"], "FAIL"),
        (["PASS", "BLOCKED"], "BLOCKED"),
        (["FAIL", "BLOCKED"], "FAIL"),
        (["NOT_APPLICABLE"], "INCOMPLETE"),
        ([], "INCOMPLETE"),
    ],
)
def test_verified_run_required_check_aggregation(statuses: list[str], expected: str):
    checks = [{"id": f"check-{index}", "status": status} for index, status in enumerate(statuses)]
    assert aggregate_required_checks(checks) == expected


def test_verified_run_aggregation_rejects_unknown_status():
    with pytest.raises(CmtkError) as error:
        aggregate_required_checks([{"id": "bad", "status": "SUCCESS"}])
    assert error.value.reason_code == "STATUS-INVALID"


def test_hashed_structured_evidence_uses_one_byte_snapshot(tmp_path, monkeypatch):
    path = tmp_path / "stage-result.json"
    path.write_text('{"status":"PASS"}\n', encoding="utf-8")
    first_snapshot = b'{"status":"PASS"}\n'
    second_snapshot = b'{"status":"tampered"}\n'
    original_read_bytes = Path.read_bytes
    calls = 0

    def shifting_read_bytes(self):
        nonlocal calls
        if self == path:
            calls += 1
            return first_snapshot if calls == 1 else second_snapshot
        return original_read_bytes(self)

    monkeypatch.setattr(Path, "read_bytes", shifting_read_bytes)
    content = _read_evidence_bytes(path, evidence_path="verified-run.json", artifact="stage-result.json")
    assert sha256_bytes(content) == sha256_bytes(first_snapshot)
    assert _load_structured_evidence(
        content,
        evidence_path="verified-run.json",
        artifact="stage-result.json",
    ) == {"status": "PASS"}
    assert calls == 1


@pytest.mark.parametrize("value", ["/tmp/evidence.json", "../evidence.json", "folder\\evidence.json"])
def test_verified_evidence_paths_must_be_repository_relative(value):
    with pytest.raises(CmtkError) as error:
        _require_repository_relative_path(value, field="artifact")
    assert error.value.reason_code == "EVIDENCE-RECORD-INVALID"
