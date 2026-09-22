"""FastAPI application factory and uvicorn entry-point (Phases B, K wiring).

Run the API in the ``ai`` conda environment (CUDA-capable torch, fastapi,
langgraph, langchain-groq all present):

    source ~/miniconda3/etc/profile.d/conda.sh && conda activate ai
    uvicorn apps.api.main:app --reload

Uvicorn target: ``apps.api.main:app``.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api import __version__
from apps.api.container import build_container
from apps.api.routers import chat, health, inspection
from apps.api.settings import Settings, get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup hook: fail loudly (in logs) when the configured model artefact is missing.

    The engine stays lazy (tests and ``/health`` never pay the CPU load cost),
    but a missing checkpoint is surfaced here as a clear configuration error
    instead of an unexplained ``MODEL_UNAVAILABLE`` on first ``/analyze``.
    """
    checkpoint = app.state.container.resolved_model_path()
    if not checkpoint.is_file():
        logger.error(
            "segmentation checkpoint is missing at startup: %s — /analyze will return "
            "MODEL_UNAVAILABLE (HTTP 500). Set MODEL_PATH (or restore the default) to a "
            "valid git-ignored checkpoint under ml/experiments/.",
            checkpoint,
        )
    else:
        logger.info("segmentation checkpoint present at startup: %s", checkpoint)
    yield


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the FastAPI application with the given (or cached) settings."""
    settings = settings if settings is not None else get_settings()
    app = FastAPI(title="AutoInspect-X API", version=__version__, lifespan=_lifespan)
    app.state.settings = settings
    app.state.container = build_container(settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(inspection.router)
    app.include_router(chat.router)
    return app


app = create_app()
