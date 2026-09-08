"""Inference exceptions (Phase D, ADR 0003).

Inference failures are explicit and typed: the API must never construct a
silent fallback prediction (ADR 0003) — a missing artefact raises, loudly.
"""

from __future__ import annotations


class InferenceError(Exception):
    """Base class for inference-layer failures."""


class ModelLoadError(InferenceError):
    """The checkpoint could not be read as a valid inference artefact."""


class ModelVersionError(InferenceError):
    """The checkpoint does not match the configured artefact contract."""
