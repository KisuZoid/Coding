"""Typed API error categories for the AutoInspect-X backend.

Every failure the client can hit is mapped to a stable machine-readable
``code`` plus a safe human ``message``. Internal details (real exceptions and
tracebacks) are logged server-side only and never serialised into responses, so
no secrets or internals can leak through the API boundary.

Codes:
- ``SESSION_NOT_FOUND`` / ``SESSION_CLOSED`` / ``SESSION_EXPIRED`` — lifecycle.
- ``NO_UPLOADED_PHOTO`` — analyze called before a photo was uploaded.
- ``BAD_UPLOAD`` — the uploaded binary was rejected by the image store.
- ``MODEL_UNAVAILABLE`` — segmentation engine could not be built (missing
  checkpoint / arch mismatch / wrong version).
- ``INFERENCE_FAILED`` — model ran but the forward pass failed.
- ``LLM_UNAVAILABLE`` — production LangChain/Groq call failed.
"""

from __future__ import annotations

from typing import Any, NamedTuple


class APIErrorCode:
    """Stable error category values surfaced in ``detail.code``."""

    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    SESSION_CLOSED = "SESSION_CLOSED"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    NO_UPLOADED_PHOTO = "NO_UPLOADED_PHOTO"
    BAD_UPLOAD = "BAD_UPLOAD"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    INFERENCE_FAILED = "INFERENCE_FAILED"
    LLM_UNAVAILABLE = "LLM_UNAVAILABLE"


class APIProblem(NamedTuple):
    """HTTP status + payload pair for a typed failure."""

    status_code: int
    code: str
    message: str


def problem(status_code: int, code: str, message: str) -> APIProblem:
    """Build a typed problem; message must be safe (never leak internals)."""
    return APIProblem(status_code=status_code, code=code, message=message)


def detail(prob: APIProblem) -> dict[str, Any]:
    """Serialisable FastAPI ``detail`` body for an ``HTTPException``."""
    return {"code": prob.code, "message": prob.message}
