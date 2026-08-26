from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from .errors import CmtkError

_UNRESOLVED = re.compile(r"\$(?:\{[^}]+\}|[A-Za-z_][A-Za-z0-9_]*)|%[A-Za-z_][A-Za-z0-9_]*%")


def canonical_path(value: str | Path) -> Path:
    text = str(value).strip()
    if not text:
        raise CmtkError("PATH-TARGET-AMBIGUOUS", "Path is empty.")
    if text == "~" or text.startswith("~/"):
        raise CmtkError("PATH-TARGET-AMBIGUOUS", "Home-relative paths are not accepted.")
    if _UNRESOLVED.search(text):
        raise CmtkError("PATH-UNRESOLVED-VARIABLE", "Path contains an unresolved variable.")
    path = Path(text)
    if not path.is_absolute():
        path = Path.cwd() / path
    resolved = path.resolve(strict=False)
    if resolved == Path(resolved.anchor):
        raise CmtkError("PATH-TARGET-AMBIGUOUS", "Filesystem roots are not accepted as targets.")
    return resolved


def validate_allowed_roots(values: Iterable[str | Path]) -> list[Path]:
    roots = [canonical_path(value) for value in values]
    if not roots:
        raise CmtkError("PATH-TARGET-AMBIGUOUS", "At least one allowed root is required.")
    home = Path.home().resolve(strict=False)
    for root in roots:
        if root == home:
            raise CmtkError("PATH-TARGET-AMBIGUOUS", "The home directory is too broad for an allowed root.")
    return roots


def require_within_roots(path: str | Path, roots: Iterable[str | Path]) -> Path:
    resolved = canonical_path(path)
    allowed = validate_allowed_roots(roots)
    for root in allowed:
        try:
            resolved.relative_to(root)
            return resolved
        except ValueError:
            continue
    raise CmtkError(
        "PATH-OUTSIDE-ALLOWED-ROOT",
        "Resolved path is outside every allowed root.",
        details={"path": str(resolved)},
    )
