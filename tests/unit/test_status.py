import pytest
from cmtk.core.errors import CmtkError
from cmtk.core.status import aggregate_status


@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        (["PASS", "NOT_APPLICABLE"], "PASS"),
        (["PASS", "WARN"], "WARN"),
        (["PASS", "NOT_RUN"], "NOT_RUN"),
        (["PASS", "FAIL"], "FAIL"),
        (["FAIL", "BLOCKED"], "BLOCKED"),
        (["NOT_APPLICABLE"], "NOT_APPLICABLE"),
    ],
)
def test_status_aggregation_never_renders_not_run_as_pass(statuses, expected):
    assert aggregate_status(statuses) == expected


def test_status_aggregation_rejects_unknown_values():
    with pytest.raises(CmtkError) as error:
        aggregate_status(["SUCCESS"])
    assert error.value.reason_code == "STATUS-INVALID"
