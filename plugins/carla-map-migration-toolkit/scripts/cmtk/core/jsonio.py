from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .errors import CmtkError


def load_json(path: str | Path) -> Any:
    try:
        with Path(path).open("r", encoding="utf-8") as source:
            return json.load(source)
    except (OSError, json.JSONDecodeError) as error:
        raise CmtkError(
            "INPUT-JSON-INVALID",
            "Unable to read valid JSON input.",
            details={"path": str(path), "error": str(error)},
        ) from error


def write_json_atomic(path: str | Path, value: Any, *, replace_existing: bool = False) -> None:
    destination = Path(path)
    if destination.exists() and not replace_existing:
        raise CmtkError(
            "OUTPUT-TARGET-EXISTS",
            "Output target already exists; choose a new artifact path.",
            details={"path": str(destination)},
        )
    temporary_name: str | None = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            json.dump(value, output, ensure_ascii=False, indent=2, sort_keys=True)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        if replace_existing:
            os.replace(temporary_name, destination)
            temporary_name = None
        else:
            try:
                os.link(temporary_name, destination)
            except FileExistsError as error:
                raise CmtkError(
                    "OUTPUT-TARGET-EXISTS",
                    "Output target already exists; choose a new artifact path.",
                    details={"path": str(destination)},
                ) from error
            Path(temporary_name).unlink()
            temporary_name = None
    except CmtkError:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)
        raise
    except OSError as error:
        try:
            if temporary_name:
                Path(temporary_name).unlink(missing_ok=True)
        finally:
            raise CmtkError(
                "OUTPUT-WRITE-FAILED",
                "Unable to write the JSON artifact atomically.",
                details={"path": str(destination), "error": str(error)},
            ) from error


def render_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
