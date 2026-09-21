"""Shared test fixtures.

Pydantic-settings reads `.env` at Settings-construction time and, for fields
declared with a `validation_alias`, prefers the aliased (env) source over init
kwargs. To keep every test deterministic and offline we blank the Groq
credentials for the whole suite; individual tests that need a specific value
re-`monkeypatch.setenv` it themselves.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _offline_groq(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROQ_AUTO_INSPECT_API_KEY", "")
