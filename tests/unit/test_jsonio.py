import os
from pathlib import Path

import pytest
from cmtk.core.errors import CmtkError
from cmtk.core.jsonio import write_json_atomic


def test_non_replace_write_does_not_overwrite_racing_creator(tmp_path: Path, monkeypatch):
    destination = tmp_path / "artifact.json"
    real_link = os.link

    def create_competitor_then_link(source, target):
        Path(target).write_text("competitor\n", encoding="utf-8")
        real_link(source, target)

    monkeypatch.setattr(os, "link", create_competitor_then_link)
    with pytest.raises(CmtkError) as error:
        write_json_atomic(destination, {"ours": True})

    assert error.value.reason_code == "OUTPUT-TARGET-EXISTS"
    assert destination.read_text(encoding="utf-8") == "competitor\n"
    assert list(tmp_path.glob(".artifact.json.*")) == []
