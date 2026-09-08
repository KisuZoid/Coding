"""Health/liveness router (Phase B)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from apps.api import __version__
from apps.api.settings import Settings, get_settings
from apps.api.shared.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    """Report service liveness and the resolved environment."""
    return HealthResponse(
        status="ok",
        service="autoinspect-api",
        environment=settings.environment,
        version=__version__,
    )
