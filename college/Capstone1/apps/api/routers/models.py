from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Request

from apps.api.container import Container
from apps.api.shared.schemas import ModelInfo, ModelsResponse

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=ModelsResponse)
def list_models(request: Request) -> ModelsResponse:
    container = cast(Container, request.app.state.container)
    return ModelsResponse(
        models=[ModelInfo.model_validate(info) for info in container.model_infos()],
        default_model_id=container.default_model_id(),
    )
