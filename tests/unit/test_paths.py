from pathlib import Path

import pytest
from cmtk.core.errors import CmtkError
from cmtk.core.paths import canonical_path, require_within_roots, validate_allowed_roots


@pytest.mark.parametrize("value", ["", " ", "/", "~", "~/target", "$MISSING/target", "${MISSING}/target"])
def test_canonical_path_rejects_unsafe_targets(value: str):
    with pytest.raises(CmtkError):
        canonical_path(value)


def test_allowed_roots_reject_filesystem_and_home_roots():
    with pytest.raises(CmtkError):
        validate_allowed_roots(["/"])
    with pytest.raises(CmtkError):
        validate_allowed_roots([str(Path.home())])


def test_path_must_resolve_inside_an_allowed_root(tmp_path: Path):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    target = allowed / "nested" / "result.json"
    assert require_within_roots(target, [allowed]) == target.resolve(strict=False)
    with pytest.raises(CmtkError) as error:
        require_within_roots(tmp_path.parent / "outside.json", [allowed])
    assert error.value.reason_code == "PATH-OUTSIDE-ALLOWED-ROOT"
