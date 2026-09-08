"""Phase H: deterministic Groq service (rule-based), no network."""

from __future__ import annotations

from apps.api.agent.groq_service import ExtractionIntent, RuleBasedGroqService
from apps.api.storage.records import ConsentDecision


def test_greeting_intent() -> None:
    ex = RuleBasedGroqService().extract("Hello!")
    assert ex.intent is ExtractionIntent.GREETING


def test_incident_and_location() -> None:
    ex = RuleBasedGroqService().extract("I crashed into a wall and hit the bumper")
    assert ex.intent in (ExtractionIntent.INCIDENT, ExtractionIntent.DAMAGE_LOCATION)
    assert ex.damage_location == "bumper"


def test_consent_yes() -> None:
    ex = RuleBasedGroqService().extract("yes, you can use my photo")
    assert ex.intent is ExtractionIntent.CONSENT_YES
    assert ex.consent is ConsentDecision.GRANTED


def test_consent_no() -> None:
    ex = RuleBasedGroqService().extract("no, don't use my data")
    assert ex.intent is ExtractionIntent.CONSENT_NO


def test_bare_yes_counts_as_consent_granted() -> None:
    ex = RuleBasedGroqService().extract("yes")
    assert ex.intent is ExtractionIntent.CONSENT_YES
    assert ex.consent is ConsentDecision.GRANTED


def test_bare_no_counts_as_consent_declined() -> None:
    ex = RuleBasedGroqService().extract("no")
    assert ex.intent is ExtractionIntent.CONSENT_NO
    assert ex.consent is ConsentDecision.DECLINED


def test_city_and_finish() -> None:
    ex = RuleBasedGroqService().extract("I'd get it repaired in Mumbai. Done.")
    assert ex.repair_city and ex.repair_city.startswith("mumbai")


def test_unknown_sentence_is_other_or_finish() -> None:
    ex = RuleBasedGroqService().extract("it's super cloudy today")
    assert ex.intent in (ExtractionIntent.OTHER, ExtractionIntent.FINISH)


def test_explain_never_pretends_quote_exists() -> None:
    unavailable = RuleBasedGroqService().explain({"cost_status": "DATA_UNAVAILABLE"})
    assert "not" in unavailable and "quote" in unavailable
    demo = RuleBasedGroqService().explain({"cost_status": "SYNTHETIC_ESTIMATE"})
    assert "NOT a real quote" in demo
