"""Application configuration for the AutoInspect-X backend (Phase B).

Settings are driven by environment variables (and a local ``.env`` when
present), matching the names declared in ``.env.example``. No secret value is
ever logged; ``groq_api_key`` is consumed server-side only.

Model artefacts are never hard-coded: ``model_path`` / ``model_version`` are
resolved from ``MODEL_PATH`` / ``MODEL_VERSION`` (ADR 0003 / ML guidelines).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration resolved from environment + ``.env``."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    environment: str = "development"
    log_level: str = "info"

    api_url: str = "http://localhost:8000"

    # Strict browser-origin allowlist for CORS (frontend at apps/web). Default is
    # the Next.js dev server; overwrite with CORS_ORIGINS (JSON list) for other
    # origins. Never "*" — the API is meant for the demo frontend only.
    cors_origins: list[str] = ["http://localhost:3000"]

    # Backed by GROQ_AUTO_INSPECT_API_KEY (see .env.example). Consumed
    # server-side only; never exposed to the browser or logs.
    groq_api_key: str = Field(default="", validation_alias="GROQ_AUTO_INSPECT_API_KEY")
    model_path: Path | None = None
    model_version: str | None = None

    # When True, a synthetic cost estimate may be surfaced — always inside an
    # explicitly labelled "DEMO / SYNTHETIC ESTIMATE — NOT A REAL QUOTE" state.
    allow_synthetic_estimate: bool = False

    # Local storage roots (phases C/K). Supabase/S3/Postgres replace these
    # later behind the storage interfaces without touching domain logic.
    storage_root: Path = Path("storage")
    training_root: Path = Path("data/training")

    # SQLite today; e.g. "sqlite:///storage/app.db". Empty -> <storage_root>/app.db
    # (see storage.resolve_database_path). A Postgres URL requires an ADR.
    database_url: str = ""

    # Directive for consented user data under <training_root>/<dataset_version>.
    training_dataset_version: str = "user-consented-v1"


@lru_cache
def get_settings() -> Settings:
    return Settings()
