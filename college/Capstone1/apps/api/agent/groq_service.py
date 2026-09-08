"""Groq-backed language service (Phase H).

Two interchangeable implementations behind one protocol:

- ``GroqLLMService`` — calls the Groq chat API with a strict JSON system prompt.
  The Groq API key is read server-side only; network calls are never made in
  tests (a stub is injected).
- ``RuleBasedGroqService`` — deterministic keyword/bag extraction used when no
  key is configured and as the always-available fallback. It is not smarter
  than a lookup table, and never pretends otherwise.

Nothing here stores chat-history or personal data.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol

from apps.api.storage.records import ConsentDecision


class ExtractionIntent(StrEnum):
    GREETING = "GREETING"
    INCIDENT = "INCIDENT"
    DAMAGE_LOCATION = "DAMAGE_LOCATION"
    VEHICLE = "VEHICLE"
    REPAIR_LOCATION = "REPAIR_LOCATION"
    INSURANCE = "INSURANCE"
    PHOTO_PROVIDED = "PHOTO_PROVIDED"
    CONSENT_YES = "CONSENT_YES"
    CONSENT_NO = "CONSENT_NO"
    FINISH = "FINISH"
    OTHER = "OTHER"


@dataclass
class Extraction:
    intent: ExtractionIntent
    raw_text: str
    incident: str | None = None
    damage_location: str | None = None
    vehicle_make: str | None = None
    vehicle_model: str | None = None
    vehicle_year: int | None = None
    repair_city: str | None = None
    insurance_claim: bool | None = None
    consent: ConsentDecision | None = None
    finish: bool = False
    entities: dict[str, Any] = field(default_factory=dict)


class GroqService(Protocol):
    def extract(self, message: str) -> Extraction:
        """Classify intent and pull the entities we care about."""
        ...

    def explain(self, payload: dict[str, Any]) -> str:
        """Turn analysis/repair/cost facts into a short plain-language reply."""
        ...


_INCIDENT_WORDS = (
    "collided",
    "collision",
    "hit",
    "crashed",
    "crash",
    "scraped",
    "scrape",
    "bumped",
    "bump",
    "dented",
    "dented",
    "accident",
    "rear-ended",
    "rear end",
    "impact",
    "smashed",
)
_DAMAGE_PANELS = {
    "bonnet": "bonnet",
    "hood": "bonnet",
    "bumper": "bumper",
    "front bumper": "bumper",
    "rear bumper": "bumper",
    "door": "door",
    "front door": "door",
    "rear door": "door",
    "fender": "fender",
    "quarter": "quarter panel",
    "wing": "fender",
    "roof": "roof",
    "window": "window",
    "windscreen": "windshield",
    "lit": "headlight",
    "headlight": "headlight",
    "tail light": "tail light",
    "mirror": "mirror",
    "side mirror": "mirror",
    "side": "side panel",
    "trunk": "trunk",
    "boot": "trunk",
}


class RuleBasedGroqService:
    """Deterministic keyword extraction; the honest default when no LLM key set."""

    def extract(self, message: str) -> Extraction:
        text = re.sub(r"[\s,.;:!?()]+", " ", message.strip().lower())
        ex = Extraction(intent=ExtractionIntent.OTHER, raw_text=message)

        if re.search(r"\b(hi|hello|hey|good (morning|afternoon|evening))\b", text):
            ex.intent = ExtractionIntent.GREETING
        yes_rx = r"\b(yes|sure|go ahead|ok(ay)?|fine)\b.*\b(photo|image|train|data)\b"
        no_rx = r"\b(no|don't|do not|not +ok(ay)?)\b.*\b(photo|image|train|data)\b"
        consent_yes = re.search(yes_rx, text) or re.search(r"\buse my photo", text)
        consent_no = re.search(no_rx, text) or re.search(r"\bdon't use", text)
        if consent_yes:
            ex.intent = ExtractionIntent.CONSENT_YES
            ex.consent = ConsentDecision.GRANTED
        elif consent_no:
            ex.intent = ExtractionIntent.CONSENT_NO
            ex.consent = ConsentDecision.DECLINED
        elif ex.intent in (ExtractionIntent.OTHER, ExtractionIntent.GREETING) and re.fullmatch(
            r"(yes|yeah|yep|sure|go ahead|ok|okay|fine)", text
        ):
            # Bare affirmative — the typical reply to the consent question.
            ex.intent = ExtractionIntent.CONSENT_YES
            ex.consent = ConsentDecision.GRANTED
        elif ex.intent in (ExtractionIntent.OTHER, ExtractionIntent.GREETING) and re.fullmatch(
            r"(no|nope|not really|not yet)", text
        ):
            ex.intent = ExtractionIntent.CONSENT_NO
            ex.consent = ConsentDecision.DECLINED

        if ex.intent in (ExtractionIntent.OTHER, ExtractionIntent.GREETING) and any(
            word in text for word in _INCIDENT_WORDS
        ):
            ex.intent = ExtractionIntent.INCIDENT
            for word in ("collided", "crashed", "hit", "scraped", "bumped"):
                if word in text:
                    ex.incident = f"vehicle {word} during an incident"
                    break

        panel = next((_DAMAGE_PANELS[w] for w in _DAMAGE_PANELS if w in text), None)
        if panel and ex.intent in (
            ExtractionIntent.OTHER,
            ExtractionIntent.GREETING,
            ExtractionIntent.INCIDENT,
        ):
            ex.damage_location = panel
            ex.intent = ExtractionIntent.DAMAGE_LOCATION

        make_year = re.search(r"(\d{4})\s+([a-z]+)", text)
        year: int | None = int(make_year.group(1)) if make_year else None
        if year:
            ex.vehicle_year = year
        m = re.search(r"(?:my|the|our)?\s*([a-z][a-z0-9 -]{2,})\s*\b(model|mk|series)\b", text)
        if m:
            ex.vehicle_make = m.group(1).strip()
        brands = (
            "honda",
            "toyota",
            "maruti",
            "hyundai",
            "mg",
            "kia",
            "tata",
            "mahindra",
            "ford",
            "vw",
            "skoda",
        )
        for brand in brands:
            if brand in text:
                ex.vehicle_make = ex.vehicle_make or brand
                break
        model_hint = re.search(r"\b(suv|sedan|hatch|creta|ciaz|swift|city|baleno)\b", text)
        if model_hint:
            ex.vehicle_model = model_hint.group(1)

        city = re.search(r"(?:in|at|near)\s+([a-z][a-z ]{1,40})", text)
        if city:
            ex.repair_city = city.group(1).strip().rstrip(".,;:!?")

        if re.search(r"\b(insurance|claim|insurer)\b", text):
            ex.intent = ExtractionIntent.INSURANCE
            no_claim = r"\b(no|skipping|skip|without)\b"
            ex.insurance_claim = not bool(re.search(no_claim, text))
        gender_rx = r"\b(male|female|transgender|driver's|driver)\b"
        if re.search(gender_rx, text) and ex.insurance_claim is None:
            ex.insurance_claim = False

        photo_rx = r"\b(photo|image|upload|pic|picture)\b"
        if ex.intent == ExtractionIntent.OTHER and re.search(photo_rx, text):
            ex.intent = ExtractionIntent.PHOTO_PROVIDED
        finish_rx = r"\b(done|finish|stop|that's it|that is it|no more|bye)\b"
        if re.search(finish_rx, text) and ex.intent == ExtractionIntent.OTHER:
            ex.intent = ExtractionIntent.FINISH
            ex.finish = True

        ex.entities = {
            "incident": ex.incident,
            "damage_location": ex.damage_location,
            "vehicle_make": ex.vehicle_make,
            "vehicle_model": ex.vehicle_model,
            "vehicle_year": ex.vehicle_year,
            "repair_city": ex.repair_city,
            "insurance_claim": ex.insurance_claim,
        }
        return ex

    def explain(self, payload: dict[str, Any]) -> str:
        classes = payload.get("classes_present", {}) or {}
        names = ", ".join(classes.values()) if classes else "no visible damage"
        parts = [f"Damage check found: {names}."]
        if payload.get("repair_action"):
            rule = payload["repair_action"]
            parts.append(
                f"Suggested action (a preliminary demonstration rule, not a final "
                f"decision): {rule}."
            )
        if payload.get("cost_status") and payload["cost_status"] != "DATA_UNAVAILABLE":
            parts.append("A demo estimate was produced — it is NOT a real quote.")
        elif payload.get("cost_status") == "DATA_UNAVAILABLE":
            parts.append(
                "A real quote is not available because no validated cost "
                "data exists for this damage."
            )
        if payload.get("consent"):
            parts.append(
                "Would you be okay with us keeping this photo for improving the model? (yes / no)"
            )
        return " ".join(parts)


_GROQ_SYSTEM_PROMPT = (
    "You extract inspection entities from a car-damage chat. Return strict JSON "
    "with keys: intent (one of the intents in this list: GREETING|INCIDENT|"
    "DAMAGE_LOCATION|VEHICLE|REPAIR_LOCATION|INSURANCE|PHOTO_PROVIDED|"
    "CONSENT_YES|CONSENT_NO|FINISH|OTHER), incident (string or null), "
    "damage_location (panel string or null), vehicle_make, vehicle_model, "
    "vehicle_year (int or null), repair_city, insurance_claim (bool or null), "
    "consent (GRANTED|DECLINED|null), finish (bool). No extra text."
)


class GroqLLMService:
    """Real LLM service; never used in tests (no network) and never fabricated."""

    def __init__(
        self, api_key: str, model: str = "llama-3.3-70b-versatile", timeout: float = 20.0
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._timeout = timeout
        self._fallback = RuleBasedGroqService()
        self._client: Any | None = None

    def _ensure_client(self) -> Any:
        if self._client is None:
            from groq import Groq  # local import keeps tests import-safe

            self._client = Groq(api_key=self._api_key, timeout=self._timeout)
        return self._client

    def extract(self, message: str) -> Extraction:
        try:
            client = self._ensure_client()
            resp = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": _GROQ_SYSTEM_PROMPT},
                    {"role": "user", "content": message},
                ],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            content = (resp.choices[0].message.content or "").strip()
            return self._parse(content, message)
        except Exception:
            return self._fallback.extract(message)

    @staticmethod
    def _parse(content: str, raw: str) -> Extraction:
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            m = re.search(r"\{.*\}", content, re.DOTALL)
            data = json.loads(m.group(0)) if m else {}
        intent = ExtractionIntent(data.get("intent", "OTHER"))
        consent = ConsentDecision(data["consent"]) if data.get("consent") else None
        year = data.get("vehicle_year")
        return Extraction(
            intent=intent,
            raw_text=raw,
            incident=data.get("incident"),
            damage_location=data.get("damage_location"),
            vehicle_make=data.get("vehicle_make"),
            vehicle_model=data.get("vehicle_model"),
            vehicle_year=int(year) if isinstance(year, (int, float)) else None,
            repair_city=data.get("repair_city"),
            insurance_claim=data.get("insurance_claim"),
            consent=consent,
            finish=bool(data.get("finish", False)),
            entities=data,
        )

    def explain(self, payload: dict[str, Any]) -> str:
        return self._fallback.explain(payload)


def build_groq_service(settings: Any) -> GroqService:
    """Real LLM when a Groq key is configured; deterministic rule otherwise."""
    if settings.groq_api_key:
        return GroqLLMService(settings.groq_api_key)
    return RuleBasedGroqService()
