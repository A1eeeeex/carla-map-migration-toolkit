from __future__ import annotations

import os

from .errors import CmtkError

EXECUTION_CONTEXTS = {
    "host-cpython",
    "source-unreal-python",
    "ue427-unreal-python",
    "carla-client-python",
    "shell-build",
}


def current_context() -> str:
    value = os.environ.get("CMTK_EXECUTION_CONTEXT", "host-cpython")
    if value not in EXECUTION_CONTEXTS:
        raise CmtkError(
            "ENV-EXECUTION-CONTEXT-MISMATCH",
            "Unknown execution context.",
            details={"actual": value, "allowed": sorted(EXECUTION_CONTEXTS)},
        )
    return value


def require_context(expected: str) -> str:
    actual = current_context()
    if actual != expected:
        raise CmtkError(
            "ENV-EXECUTION-CONTEXT-MISMATCH",
            f"This command requires {expected}.",
            details={"expected": expected, "actual": actual},
        )
    return actual
