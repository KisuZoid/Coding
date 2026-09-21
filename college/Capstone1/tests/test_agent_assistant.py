"""Phase H + ADR 0011: assistant service (stub + LangChain wrapper)."""

from __future__ import annotations

from typing import Any

import pytest
from langchain_core.messages import BaseMessage

from apps.api.agent.assistant import (
    AssistantUnavailableError,
    LangChainGroqAssistant,
    StubAssistant,
    build_assistant,
    evidence_payload,
)
from apps.api.settings import Settings


def _evidence() -> dict[str, Any]:
    return {
        "classes_present": {"1": "dent", "2": "scratch"},
        "per_class_area_ratio_image": {"1": 0.02, "2": 0.10},
        "num_instances": 3,
        "low_confidence": False,
        "mean_confidence": 0.81,
    }


class _FakeChat:
    """Deterministic LangChain-like object; records what it received."""

    def __init__(self, reply: str = "Deterministic assistant reply.") -> None:
        self.calls: list[list[BaseMessage]] = []
        self._reply = reply

    def invoke(self, messages: list[BaseMessage]) -> Any:
        self.calls.append(list(messages))
        from langchain_core.messages import AIMessage

        return AIMessage(content=self._reply)


# --------------------------------------------------------------------------- #
# Stub (offline double)
# --------------------------------------------------------------------------- #


def test_stub_explanation_echoes_evidence_only() -> None:
    text = StubAssistant().damages_explanation(_evidence())
    assert "dent" in text and "scratch" in text
    assert "10.0%" in text  # 0.10 -> 10.0% of image frame
    assert "verified damage extent" not in text  # not low-confidence
    assert "cost" not in text.lower()


def test_stub_explanation_marks_low_confidence_as_preliminary() -> None:
    text = StubAssistant().damages_explanation({**_evidence(), "low_confidence": True})
    assert "preliminary" in text.lower()


def test_stub_explanation_empty_classes_is_honest() -> None:
    text = StubAssistant().damages_explanation({"classes_present": {}, "low_confidence": False})
    assert "did not clearly detect" in text


def test_stub_retake_guidance_maps_reasons() -> None:
    text = StubAssistant().retake_guidance(["TOO_BLURRY", "TOO_DARK"])
    assert "TOO_BLURRY" in text
    assert "focus" in text
    assert "lighting" in text
    assert "cost" not in text.lower()


def test_stub_chat_reply_asks_for_photo_without_evidence() -> None:
    text = StubAssistant().chat_reply([{"role": "user", "content": "hi"}], None)
    assert "photo" in text.lower()


def test_stub_chat_reply_recaps_with_evidence() -> None:
    text = StubAssistant().chat_reply(
        [{"role": "user", "content": "what did you find?"}], _evidence()
    )
    assert "dent" in text and "scratch" in text


def test_stub_provider_label() -> None:
    assert StubAssistant().provider == "stub"


# --------------------------------------------------------------------------- #
# LangChain wrapper
# --------------------------------------------------------------------------- #


def test_chain_explanation_passes_system_prompt_and_evidence() -> None:
    chat: Any = _FakeChat()
    assistant = LangChainGroqAssistant(chat)
    reply = assistant.damages_explanation(_evidence())
    assert reply == "Deterministic assistant reply."
    messages = chat.calls[0]
    system = messages[0].content
    assert "NEVER invent damage" in system
    assert evidence_payload(_evidence()) in messages[1].content


def test_chain_chat_reply_builds_history() -> None:
    chat: Any = _FakeChat()
    assistant = LangChainGroqAssistant(chat)
    assistant.chat_reply(
        [
            {"role": "user", "content": "u1"},
            {"role": "assistant", "content": "a1"},
            {"role": "user", "content": "u2"},
        ],
        _evidence(),
    )
    contents = [str(m.content) for m in chat.calls[0]]
    assert contents[0].startswith("You are a professional automotive")
    assert "u1" in contents and "a1" in contents and "u2" in contents
    assert any("inspection evidence" in c for c in contents)


def test_chain_retake_guidance() -> None:
    chat: Any = _FakeChat("Retake it in better light.")
    assistant = LangChainGroqAssistant(chat)
    reply = assistant.retake_guidance(["EXCESSIVE_GLARE"])
    assert reply == "Retake it in better light."
    assert "EXCESSIVE_GLARE" in chat.calls[0][1].content


def test_chain_empty_reply_raises() -> None:
    chat: Any = _FakeChat(reply="   ")
    assistant = LangChainGroqAssistant(chat)
    with pytest.raises(AssistantUnavailableError):
        assistant.damages_explanation(_evidence())


def test_chain_invoke_exception_raises_unavailable() -> None:
    class _Boom:
        def invoke(self, messages: list[BaseMessage]) -> Any:  # noqa: ARG002
            raise ConnectionError("network down")

    boomer: Any = _Boom()
    assistant = LangChainGroqAssistant(boomer)
    with pytest.raises(AssistantUnavailableError):
        assistant.chat_reply([{"role": "user", "content": "hi"}], None)


# --------------------------------------------------------------------------- #
# Factory wiring
# --------------------------------------------------------------------------- #


def test_build_assistant_stub_without_key() -> None:
    assert isinstance(build_assistant(Settings(groq_api_key="", groq_model="m")), StubAssistant)


def test_build_assistant_chain_with_key(monkeypatch: pytest.MonkeyPatch) -> None:
    # Constructs a real ChatGroq object, but no request is made.
    monkeypatch.setenv("GROQ_AUTO_INSPECT_API_KEY", "sk-test")
    assistant = build_assistant(Settings(groq_model="m"))
    assert isinstance(assistant, LangChainGroqAssistant)
