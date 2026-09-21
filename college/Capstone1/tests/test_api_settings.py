"""Settings-resolution tests (Phase B, no dataset required)."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps.api.settings import Settings


def test_defaults() -> None:
    # _env_file=None: assert the code defaults independent of any local .env.
    settings = Settings(_env_file=None)  # type: ignore[call-arg]
    assert settings.environment == "development"
    assert settings.log_level == "info"
    assert isinstance(settings.groq_api_key, str)
    assert settings.groq_model == "openai/gpt-oss-20b"
    assert settings.model_path is None
    assert settings.model_version is None
    assert settings.storage_root == Path("storage")
    assert settings.training_root == Path("data/training")


def test_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "model.pt"))
    settings = Settings()
    assert settings.environment == "test"
    assert settings.model_path == tmp_path / "model.pt"


def test_groq_key_reads_authoritative_env_alias(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROQ_AUTO_INSPECT_API_KEY", "sk-test")
    assert Settings().groq_api_key == "sk-test"


def test_model_path_casts_to_path() -> None:
    settings = Settings(model_path=Path("/var/models/cardd_baseline_ce.pt"))
    assert settings.model_path == Path("/var/models/cardd_baseline_ce.pt")
