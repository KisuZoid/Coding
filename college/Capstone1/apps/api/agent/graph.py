"""LangGraph turn workflow (photo-first, ADR 0011).

A minimal LangGraph: each ``POST /chat`` appends the user message to the
persisted state and runs ``START -> llm_turn -> END``. ``llm_turn`` forwards the
conversation plus the stored (prompt-safe) inspection evidence to the
``AssistantService`` and returns the reply.

Photo intake, quality gating, segmentation, and the first assistant explanation
happen in the ``/analyze`` endpoint, so this graph never waits on questionnaire
fields. Offline (no Groq key) the container wires a ``StubAssistant``, so tests
and the CI demo never touch the network.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from langgraph.graph import END, START, StateGraph

from apps.api.agent.assistant import AssistantService
from apps.api.agent.state import InspectionState
from apps.api.inspection.context import InspectionContext, VisionInfo
from ml.inference.features import DamageFeatures


@dataclass
class Services:
    assistant: AssistantService


def history_from_state(state: InspectionState) -> list[dict[str, str]]:
    return [
        {"role": str(m.get("role", "user")), "content": str(m.get("content", ""))}
        for m in state.get("messages", [])
    ]


_EVIDENCE_KEYS = (
    "classes_present",
    "per_class_area_ratio_image",
    "damage_area_ratio_image",
    "num_instances",
    "low_confidence",
    "low_confidence_instances",
    "mean_confidence",
    "model_notes",
    "quality",
)


def persist_evidence(state: dict[str, Any]) -> dict[str, Any] | None:
    """Prompt-safe subset of the stored inspection (no base64 payloads).

    Only facts the assistant may restate make it into the prompt: classes,
    area ratios, confidence flags, quality outcome, and model limitations.
    """
    inspection = state.get("inspection")
    if not isinstance(inspection, dict):
        return None
    evidence = {
        key: inspection.get(key) for key in _EVIDENCE_KEYS if inspection.get(key) is not None
    }
    evidence["width"] = inspection.get("width")
    evidence["height"] = inspection.get("height")
    return evidence


def llm_turn(state: InspectionState, services: Services) -> dict[str, Any]:
    reply = services.assistant.chat_reply(
        history=history_from_state(state),
        evidence=persist_evidence(dict(state)),
    )
    return {"reply": reply}


# --------------------------------------------------------------------------- #
def _compile(services: Services) -> Any:
    b = StateGraph(InspectionState)
    b.add_node("llm_turn", lambda s: llm_turn(s, services))
    b.add_edge(START, "llm_turn")
    b.add_edge("llm_turn", END)
    return b.compile()


def build_workflow(services: Services) -> Any:
    """Return a compiled, deterministic LangGraph workflow."""
    return _compile(services)


def context_from_state(state: dict[str, Any]) -> InspectionContext:
    """Session context used by the offline consent bookkeeping."""
    inspection_dict = cast(dict[str, Any], state.get("inspection") or {})
    raw_quality = inspection_dict.get("quality")
    quality = cast(dict[str, Any], raw_quality) if isinstance(raw_quality, dict) else {}
    return InspectionContext(
        session_id=str(state.get("session_id", "")),
        vision=VisionInfo(
            image_asset_id=state.get("image_asset_id"),
            quality_status=quality.get("status"),
            model_found_classes={
                str(k): str(v) for k, v in (inspection_dict.get("classes_present") or {}).items()
            },
            damage_area_ratio_image=inspection_dict.get("damage_area_ratio_image"),
        ),
    )


def features_from_summary(summary: dict[str, Any]) -> DamageFeatures:
    """Rebuild scalars for the consent sample record (mask is a placeholder).

    DamageFeatures instances hold numpy/column arrays that don't round-trip
    through JSON, so the persisted summary keeps scalar facts only; the mask is
    rebuilt as a single background pixel and never claimed to be real output.
    """
    import numpy as np

    return DamageFeatures(
        width=int(summary.get("width", 512)),
        height=int(summary.get("height", 512)),
        instances=[],
        damage_area_ratio_image=float(summary.get("damage_area_ratio_image", 0.0)),
        per_class_area_ratio_image={
            int(k): float(v) for k, v in summary.get("per_class_area_ratio_image", {}).items()
        },
        classes_present={int(k): str(v) for k, v in summary.get("classes_present", {}).items()},
        num_instances=int(summary.get("num_instances", 0)),
        low_confidence_instances=int(summary.get("low_confidence_instances", 0)),
        mask=np.zeros((1, 1), dtype=np.uint8),
    )


def run_turn(
    workflow: Any,
    state: dict[str, Any],
    user_message: str | None = None,
) -> dict[str, Any]:
    """Run one chat turn against the persisted state; returns the new state.

    The user message is prepended into the graph input and the assistant reply
    is appended to ``messages`` afterwards, so a successful turn always ends
    with ``role == "assistant"`` in the returned state.
    """
    if user_message:
        messages = [*state.get("messages", []), {"role": "user", "content": user_message}]
        state = {**state, "messages": messages}
    result = dict(workflow.invoke(cast(InspectionState, dict(state))))
    reply = result.get("reply")
    if reply:
        result["messages"] = [*result.get("messages", []), {"role": "assistant", "content": reply}]
    return result
