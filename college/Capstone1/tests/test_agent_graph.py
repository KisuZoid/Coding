"""Phase G: photo-first LangGraph turn flow (offline assistant, no network)."""

from __future__ import annotations

from typing import Any

from apps.api.agent.assistant import StubAssistant
from apps.api.agent.graph import (
    Services,
    build_workflow,
    persist_evidence,
    run_turn,
)


def _base_state(session_id: str = "s1") -> dict[str, Any]:
    return {"session_id": session_id, "messages": []}


def _workflow() -> Any:
    return build_workflow(Services(assistant=StubAssistant()))


def test_empty_session_reply_asks_for_photo() -> None:
    state = run_turn(_workflow(), _base_state(), "Hi there!")
    assert "photo" in (state["reply"] or "").lower()
    messages = state.get("messages") or []
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hi there!"
    assert messages[-1]["role"] == "assistant"
    assert "waiting_for" not in state
    assert "halt" not in state


def test_follow_up_with_evidence_recaps_classes() -> None:
    wf = _workflow()
    inspection = {
        "classes_present": {"1": "dent", "2": "scratch"},
        "per_class_area_ratio_image": {"1": 0.01, "2": 0.08},
        "low_confidence": False,
        "mean_confidence": 0.78,
        "width": 512,
        "height": 512,
    }
    state = dict(
        _base_state(),
        image_asset_id="a1",
        inspection=inspection,
        messages=[{"role": "assistant", "content": "Analysis complete: dent, scratch."}],
    )
    state = run_turn(wf, state, "What did you find on the bumper?")

    reply = state["reply"] or ""
    assert "dent" in reply and "scratch" in reply
    messages = state.get("messages") or []
    assert messages[-1]["role"] == "assistant"
    # the AI explanation (set by /analyze) plus the new user+assistant turn
    assert len(messages) >= 3


def test_no_evidence_reply_does_not_invent_damage() -> None:
    state = run_turn(_workflow(), _base_state(), "Is there any hidden damage?")
    reply = state["reply"] or ""
    assert "hidden damage" not in reply.lower()
    assert "photo" in reply.lower()


def test_persist_evidence_strips_blobs_and_keeps_facts() -> None:
    raw = {
        "classes_present": {"2": "scratch"},
        "damage_area_ratio_image": 0.05,
        "low_confidence": True,
        "model_notes": ["e2e stub"],
        "quality": {"status": "VALID", "reasons": []},
        "num_instances": 2,
        "overlay_png_base64": "AAAA...ignored",
        "model_metadata": {"checkpoint_path": "ignored"},
    }
    evidence = persist_evidence({"inspection": raw})
    assert evidence is not None
    assert "overlay_png_base64" not in evidence
    assert "model_metadata" not in evidence
    assert evidence["classes_present"] == {"2": "scratch"}
    assert evidence["low_confidence"] is True


def test_persist_evidence_none_when_inspection_missing() -> None:
    assert persist_evidence({}) is None
    assert persist_evidence({"inspection": None}) is None
