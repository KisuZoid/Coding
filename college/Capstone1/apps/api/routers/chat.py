"""Chat endpoint driving the LangGraph turn flow (photo-first).

A follow-up message runs ``run_turn`` once: the graph appends the user message
and asks the assistant service (LangChain when a key is set, offline stub
otherwise) for a reply grounded in the stored inspection evidence. No
questionnaire gating; the analysis already lives in the session state from
``/analyze``. Ordinary chat never touches the segmentation model, so it works
independently of whether a photo has been analysed.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any, cast

from fastapi import APIRouter, HTTPException, Request

from apps.api.agent.assistant import AssistantUnavailableError
from apps.api.agent.graph import run_turn
from apps.api.container import Container
from apps.api.errors import (
    APIErrorCode,
    problem,
)
from apps.api.errors import (
    detail as problem_detail,
)
from apps.api.shared.schemas import ChatRequest, ChatResponse
from apps.api.storage.records import SessionStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


def _container(request: Request) -> Container:
    return cast(Container, request.app.state.container)


def _load_state(c: Container, session_id: str) -> dict[str, Any]:
    raw = c.states.get(session_id)
    if raw:
        loaded = json.loads(raw)
        return {"session_id": session_id, **loaded}
    return {"session_id": session_id, "messages": []}


@router.post("", response_model=ChatResponse)
def chat(request: Request, body: ChatRequest) -> ChatResponse:
    c = _container(request)
    record = c.sessions.get(body.session_id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail=problem_detail(
                problem(404, APIErrorCode.SESSION_NOT_FOUND, "session not found")
            ),
        )
    if record.status is not SessionStatus.ACTIVE:
        raise HTTPException(
            status_code=410,
            detail=problem_detail(problem(410, APIErrorCode.SESSION_CLOSED, "session closed")),
        )
    if record.expires_at is not None and record.expires_at < datetime.now(UTC):
        raise HTTPException(
            status_code=410,
            detail=problem_detail(problem(410, APIErrorCode.SESSION_EXPIRED, "session expired")),
        )

    state = _load_state(c, body.session_id)
    try:
        updated = run_turn(c.workflow, state, body.message)
    except AssistantUnavailableError:
        logger.exception("LLM unavailable during chat turn")
        raise HTTPException(
            status_code=503,
            detail=problem_detail(
                problem(503, APIErrorCode.LLM_UNAVAILABLE, "assistant unavailable")
            ),
        ) from None

    reply = updated.get("reply") or ""
    c.states.save(body.session_id, json.dumps(updated, default=str))
    return ChatResponse(
        session_id=body.session_id,
        reply=reply,
        request_id=uuid.uuid4().hex,
    )
