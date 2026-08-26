from __future__ import annotations

from typing import Any


class CmtkError(RuntimeError):
    """A stable, machine-readable toolkit error."""

    def __init__(
        self,
        reason_code: str,
        message: str,
        *,
        status: str = "BLOCKED",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.reason_code = reason_code
        self.message = message
        self.status = status
        self.details = details or {}

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0.0",
            "status": self.status,
            "reason_code": self.reason_code,
            "message": self.message,
            "details": self.details,
        }
