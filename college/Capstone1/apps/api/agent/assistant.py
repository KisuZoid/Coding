"""LangChain Groq assistant for the inspection chat (ADR 0011).

Production replies are produced through LangChain: ``ChatGroq`` from
``langchain_groq`` is the model runtime (no direct ``groq`` SDK usage). The
``AssistantService`` protocol is the seam behind which tests and the keyless
CI/development path run a deterministic ``StubAssistant`` — an offline double
that never pretends to be a live model.

Honesty rules baked into the system prompt and the stub:
- repeat only damage facts present in the structured inspection evidence;
- never invent damage, severity, repair action, or (any) cost figure;
- flag low-confidence evidence as preliminary, never verified.
"""

from __future__ import annotations

import json
from typing import Any, Protocol

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

_PRIMARY_SYSTEM_PROMPT = (
    "You are a professional automotive damage inspection assistant for "
    "AutoInspect-X. You help a user understand what the computer-vision model "
    "found in the photo they uploaded, and you can answer follow-up questions "
    "about the inspection.\n\n"
    "RULES:\n"
    "- Describe ONLY what the structured inspection evidence says.\n"
    "- NEVER invent damage, severity, repair actions, costs, or part prices.\n"
    "- Cost and repair pricing are out of scope; if asked, decline briefly.\n"
    "- Evidence flagged low_confidence is preliminary — say so, never present "
    "it as verified damage.\n"
    "- If no evidence is available yet, remind the user to upload a clear "
    "photo of the damage.\n"
    "- Be concise (2-5 sentences), friendly, and factual. No emojis.\n"
)

_QUALITY_SYSTEM_PROMPT = (
    "You are a friendly automotive inspection assistant. A user uploaded a "
    "photo that failed the capture-quality gate. Give clear, practical retake "
    "guidance based on the listed reasons. Keep it to 2-4 sentences, direct "
    "and encouraging. Never mention costs, quotes, or repairs."
)


class AssistantUnavailableError(RuntimeError):
    """Raised when a production LLM call fails; routers surface it as 503."""


class AssistantService(Protocol):
    """The seam a router/graph talks to; implemented by LangChain or a stub."""

    provider: str

    def damages_explanation(self, evidence: dict[str, Any]) -> str:
        """Plain-language summary of the segmentation evidence."""
        ...

    def retake_guidance(self, reasons: list[str]) -> str:
        """Guidance for reshooting a photo that failed the quality gate."""
        ...

    def chat_reply(self, history: list[dict[str, str]], evidence: dict[str, Any] | None) -> str:
        """Reply to a follow-up turn, grounded in the stored evidence."""
        ...


def evidence_payload(evidence: dict[str, Any]) -> str:
    """Serialise the prompt-safe evidence dict for the model or the stub."""
    return json.dumps(evidence, indent=1, default=str)


# --------------------------------------------------------------------------- #
# Offline double
# --------------------------------------------------------------------------- #

_QUALITY_REASONS_GUIDANCE = {
    "TOO_BLURRY": "hold the camera steady and make sure the damage is in focus",
    "TOO_DARK": "move to better lighting so the surface is clearly visible",
    "EXCESSIVE_GLARE": "shoot at an angle that avoids direct light or reflections",
    "WRONG_ANGLE": "shoot more directly at the damaged surface",
    "DAMAGE_NOT_VISIBLE": "frame the damaged part more tightly",
    "INSUFFICIENT_CONTEXT": "step back a little so the damaged area and its "
    "surroundings are both visible",
}


class StubAssistant:
    """Deterministic offline double used without a Groq key (tests/CI/dev).

    Clearly an offline stand-in: it echoes the evidence and never fabricates
    anything the evidence does not contain. It is not a substitute for the LLM.
    """

    provider = "stub"

    def damages_explanation(self, evidence: dict[str, Any]) -> str:
        classes = evidence.get("classes_present") or {}
        ratios = evidence.get("per_class_area_ratio_image") or {}
        if not classes:
            lines = ["The model did not clearly detect any damage classes in this photo."]
        else:
            lines = []
            for name in set(classes.values()):
                cid = next((k for k, v in classes.items() if v == name), None)
                frac = float(ratios.get(str(cid)) or 0.0)
                lines.append(f"• {name} — about {frac * 100:.1f}% of the image frame")
            lines.insert(0, "Here is what the visual model identified:")
        text = "\n".join(lines)
        text += (
            "\n\nThese predictions are preliminary and not verified damage extent."
            if evidence.get("low_confidence")
            else "\n\nAsk me anything about the damage, or upload a new photo."
        )
        return text

    def retake_guidance(self, reasons: list[str]) -> str:
        raw_tips = [_QUALITY_REASONS_GUIDANCE.get(r) for r in reasons]
        tips = [t for t in raw_tips if t is not None]
        if not tips:
            tips = ["take the photo in bright, even light with the camera steady"]
        why = ", ".join(reasons) if reasons else "the photo quality was too low"
        return (
            f"I couldn't analyse that photo because it was flagged: {why}. "
            f"Please retake it — {'; '.join(tips)} — then upload it again."
        )

    def chat_reply(
        self,
        history: list[dict[str, str]],  # noqa: ARG002 - protocol signature; unused by the stub
        evidence: dict[str, Any] | None,
    ) -> str:
        if evidence and (evidence.get("classes_present") or {}):
            names = ", ".join(sorted(set((evidence["classes_present"] or {}).values())))
            low = (
                " The model's confidence is low, so treat these as preliminary."
                if evidence.get("low_confidence")
                else ""
            )
            return (
                f"To recap the model's findings: {names}.{low} Ask me anything "
                "about the damage, or upload a fresh photo for a new look."
            )
        if evidence:
            return (
                "The model found no clearly identifiable damage classes in the "
                "last photo. You can upload another angle for a second look."
            )
        return (
            "I don't have an analysed photo for this session yet. Please attach "
            "a clear photo of the damage so I can take a look."
        )


# --------------------------------------------------------------------------- #
# Production (LangChain ChatGroq)
# --------------------------------------------------------------------------- #


class LangChainGroqAssistant:
    """Production assistant backed by LangChain's ``ChatGroq``.

    Never used in tests (a stub or fake is injected). Construct it only via
    :func:`build_assistant`, which requires a configured API key.
    """

    provider = "langchain-groq"

    def __init__(self, chat: ChatGroq) -> None:
        self._chat = chat

    def damages_explanation(self, evidence: dict[str, Any]) -> str:
        return self._invoke(
            [
                SystemMessage(content=_PRIMARY_SYSTEM_PROMPT),
                HumanMessage(content="Recent inspection evidence:\n" + evidence_payload(evidence)),
            ]
        )

    def retake_guidance(self, reasons: list[str]) -> str:
        bullets = "\n".join(f"- {r}" for r in reasons) if reasons else "- generic quality issue"
        return self._invoke(
            [
                SystemMessage(content=_QUALITY_SYSTEM_PROMPT),
                HumanMessage(content="Reasons the photo was rejected:\n" + bullets),
            ]
        )

    def chat_reply(self, history: list[dict[str, str]], evidence: dict[str, Any] | None) -> str:
        messages: list[BaseMessage] = [SystemMessage(content=_PRIMARY_SYSTEM_PROMPT)]
        if evidence:
            messages.append(
                SystemMessage(content="Current inspection evidence:\n" + evidence_payload(evidence))
            )
        for turn in history:
            content = str(turn.get("content", ""))
            if turn.get("role") == "user":
                messages.append(HumanMessage(content=content))
            else:
                messages.append(AIMessage(content=content))
        return self._invoke(messages)

    def _invoke(self, messages: list[BaseMessage]) -> str:
        try:
            response = self._chat.invoke(messages)
        except Exception as exc:
            raise AssistantUnavailableError(f"assistant model call failed: {exc}") from exc
        content = response.content if isinstance(response.content, str) else str(response.content)
        text = " ".join(content.split()).strip()
        if not text:
            raise AssistantUnavailableError("assistant returned an empty reply")
        return text


_GROQ_MODEL = "openai/gpt-oss-20b"


def build_assistant(settings: Any) -> AssistantService:
    """Real LangChain assistant when a key is configured; offline stub otherwise."""
    if settings.groq_api_key:
        chat = ChatGroq(
            model=settings.groq_model or _GROQ_MODEL,
            api_key=settings.groq_api_key,
            temperature=0.3,
            max_tokens=768,
        )
        return LangChainGroqAssistant(chat)
    return StubAssistant()
