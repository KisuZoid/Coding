"""LangGraph workflow for an inspection turn (Phase G).

Implements the mandated pipeline nodes — understand_request,
check_context_ready, photo_intake, photo_validation, damage_analysis,
feature_extraction, compare_user_vs_model, downstream_prediction,
cost_availability, repair_decision_validation, result_validation,
final_explanation, and the collection/consent/finish helpers.

The graph is turn-based: every POST /chat runs the graph once from START. Nodes
that need an answer from the user set ``waiting_for`` + ``reply`` and halt to
END; the state is persisted and the next turn resumes from the same label.
Everything is deterministic and stubbed (rule-based) unless a Groq key is
configured, so the demo works offline and tests never hit the network.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from langgraph.graph import END, START, StateGraph

from apps.api.agent.groq_service import (
    ExtractionIntent,
    GroqService,
)
from apps.api.agent.state import InspectionState
from apps.api.cost.cost_estimator import CostEstimator
from apps.api.inspection.consent_service import ConsentService
from apps.api.inspection.context import (
    DamageLocation,
    IncidentInfo,
    InspectionContext,
    RepairLocation,
    VehicleInfo,
)
from apps.api.repair.repair_estimator import RepairEstimator
from apps.api.storage.records import ConsentDecision
from ml.inference.features import DamageFeatures

_IMPL = {
    "DAMAGE_LOCATION": "damage_location",
    "REPAIR_LOCATION": "repair_city",
    "INSURANCE": "insurance_claim",
}
_QUESTIONS = {
    "DAMAGE_LOCATION": (
        "Which part of the car is damaged? (e.g. bumper, bonnet, door, side panel)"
    ),
    "REPAIR_LOCATION": (
        "Have you thought about where you'd get this repaired? A city name is enough."
    ),
    "INSURANCE": "Are you planning an insurance claim?",
}
_OPTIONAL_FIELDS = [(key, _IMPL[key], _QUESTIONS[key]) for key in _IMPL]

_FIRST_QUESTION = "Let's start — what happened to your vehicle?"


@dataclass
class Services:
    groq: GroqService
    repair_estimator: RepairEstimator
    cost_estimator: CostEstimator
    consent: ConsentService
    allow_synthetic: bool = False


def _last_user_text(state: InspectionState) -> str:
    for msg in reversed(state.get("messages", [])):
        if msg.get("role") == "user":
            return msg.get("content", "")
    return ""


def _skip(text: str) -> bool:
    lowered = text.lower().strip()
    return bool(lowered) and any(
        w in lowered for w in ("skip", "not sure", "don't know", "move on", "next", "let's move")
    )


def _build_context(state: dict[str, Any] | InspectionState) -> InspectionContext:
    return InspectionContext(
        session_id=str(state.get("session_id", "")),
        incident=IncidentInfo(summary=state.get("incident") or None),
        damage_location=DamageLocation(panel=state.get("damage_location") or None),
        vehicle=VehicleInfo(
            make=state.get("vehicle_make"),
            model=state.get("vehicle_model"),
            year=state.get("vehicle_year"),
        ),
        repair_location=RepairLocation(city=state.get("repair_city") or None),
        insurance_claim=state.get("insurance_claim"),
    )


def _features_from_summary(summary: dict[str, Any]) -> DamageFeatures:
    """Minimal honest reconstruction for repair/cost/consent.

    DamageFeatures instances hold numpy/column arrays that don't round-trip
    through JSON, so the persisted summary keeps scalar facts only; the
    mask is rebuilt as a single background pixel placeholder (never claimed
    to be real mask output).
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


def _halt(_state: InspectionState, reply: str, waiting_for: str | None) -> dict[str, Any]:
    return {"reply": reply, "waiting_for": waiting_for, "halt": True}


# --------------------------------------------------------------------------- #
# Entry / understanding
# --------------------------------------------------------------------------- #


def understand_request(_state: InspectionState, _services: Services) -> dict[str, Any]:
    return {}


def route_entry(state: InspectionState) -> str:
    if state.get("halt"):
        return END
    wf = state.get("waiting_for")
    if wf:
        return {
            "INCIDENT": "collect_incident",
            "DAMAGE_LOCATION": "collect_damage_location",
            "REPAIR_LOCATION": "collect_repair_location",
            "INSURANCE": "collect_insurance",
            "PHOTO": "photo_intake",
            "CONSENT": "consent_prompt",
            "FINISH": "finalize_session",
        }.get(wf, "collect_incident")
    if state.get("image_asset_id") is not None and state.get("analysis") is not None:
        return "photo_validation"
    return "check_context_ready"


# --------------------------------------------------------------------------- #
# Context readiness
# --------------------------------------------------------------------------- #


def check_context_ready(state: InspectionState, services: Services) -> dict[str, Any]:
    if not (state.get("incident") or "").strip():
        return _ask_for_incident(state, services)
    return _ask_for_optional_or_photo(state)


def _ask_for_incident(state: InspectionState, services: Services) -> dict[str, Any]:
    """Harvest incident/damage from the latest message in the same turn, so the
    first real answer doesn't bounce through two question rounds."""
    text = _last_user_text(state).strip()
    try:
        ex = services.groq.extract(text)
    except Exception:
        ex = None
    harvestable = ex is not None and ex.intent in (
        ExtractionIntent.INCIDENT,
        ExtractionIntent.DAMAGE_LOCATION,
        ExtractionIntent.VEHICLE,
        ExtractionIntent.REPAIR_LOCATION,
        ExtractionIntent.INSURANCE,
    )
    incident_val = ex.incident if ex else None
    if not harvestable:
        return _halt(state, _FIRST_QUESTION, "INCIDENT")
    incident_val = incident_val or text
    update: dict[str, Any] = {"incident": incident_val}
    if ex and ex.damage_location:
        update["damage_location"] = ex.damage_location
    return update


def _ask_for_optional_or_photo(state: InspectionState) -> dict[str, Any]:
    cursor = state.get("optional_cursor", 0)
    if cursor < len(_OPTIONAL_FIELDS):
        kind, key, question = _OPTIONAL_FIELDS[cursor]
        if state.get(key) is None:
            return _halt(state, question, kind)
        return {"optional_cursor": cursor + 1}

    if state.get("image_asset_id") is None:
        return _halt(
            state,
            "Thanks. Could you upload a clear photo of the damage so I can take a look?",
            "PHOTO",
        )

    if state.get("analysis") is None:
        return _halt(
            state,
            "I've received your photo — analysing it now. Share any other details "
            "and I'll summarise the damage once ready.",
            "PHOTO",
        )
    return {}


def route_after_context(state: InspectionState) -> str:
    if state.get("halt") or state.get("waiting_for"):
        return END
    if state.get("optional_cursor", 0) < len(_OPTIONAL_FIELDS):
        return "check_context_ready"
    return "photo_validation"


# --------------------------------------------------------------------------- #
# Collectors (turn-based)
# --------------------------------------------------------------------------- #


def collect_incident(state: InspectionState, services: Services) -> dict[str, Any]:
    text = _last_user_text(state)
    try:
        ex = services.groq.extract(text)
    except Exception:
        ex = None
    val = (ex.incident or text.strip()) if ex else text.strip()
    if not val:
        return _halt(state, _FIRST_QUESTION, "INCIDENT")
    update: dict[str, Any] = {"incident": val, "waiting_for": None}
    if ex and ex.damage_location and state.get("damage_location") is None:
        update["damage_location"] = ex.damage_location
    return update


def collect_damage_location(state: InspectionState, services: Services) -> dict[str, Any]:
    text = _last_user_text(state)
    if _skip(text):
        return {"optional_cursor": state.get("optional_cursor", 0) + 1, "waiting_for": None}
    try:
        panel = services.groq.extract(text).damage_location
    except Exception:
        panel = None
    val = panel or text.strip() if panel is None else panel
    return {
        **({"damage_location": val} if val else {}),
        "optional_cursor": state.get("optional_cursor", 0) + 1,
        "waiting_for": None,
    }


def collect_repair_location(state: InspectionState, services: Services) -> dict[str, Any]:
    text = _last_user_text(state)
    if _skip(text):
        return {"optional_cursor": state.get("optional_cursor", 0) + 1, "waiting_for": None}
    try:
        city = services.groq.extract(text).repair_city
    except Exception:
        city = None
    val = text.strip() if city is None else city
    return {
        **({"repair_city": val} if val else {}),
        "optional_cursor": state.get("optional_cursor", 0) + 1,
        "waiting_for": None,
    }


def collect_insurance(state: InspectionState, services: Services) -> dict[str, Any]:
    text = _last_user_text(state)
    if _skip(text) or text.lower().strip() in ("", "no", "none", "n/a"):
        return {
            "insurance_claim": False,
            "optional_cursor": state.get("optional_cursor", 0) + 1,
            "waiting_for": None,
        }
    try:
        decided = services.groq.extract(text).insurance_claim
    except Exception:
        decided = None
    update: dict[str, Any] = {}
    if decided is not None:
        update["insurance_claim"] = bool(decided)
    update["optional_cursor"] = state.get("optional_cursor", 0) + 1
    update["waiting_for"] = None
    return update


def photo_intake(_state: InspectionState) -> dict[str, Any]:
    return {"waiting_for": None}


# --------------------------------------------------------------------------- #
# Mandated pipeline nodes
# --------------------------------------------------------------------------- #


def photo_validation(state: InspectionState) -> dict[str, Any]:
    """Photo accepted; forward to analysis (quality is set by /analyze)."""
    if state.get("analysis") is None:
        return _halt(state, "Analysing your photo — please give me a moment.", "PHOTO")
    if state.get("feature_summary"):
        return {}
    return {}


def route_photo_validation(state: InspectionState) -> str:
    if state.get("halt"):
        return END
    return "damage_analysis"


def damage_analysis(state: InspectionState) -> dict[str, Any]:
    """Run analysis, but a retake is only requested for hard capture-quality
    failures (blurry/dark/glare/low-contrast, set by /analyze). Soft low model
    confidence is a flag the result screen shows, not a reason to force a
    retake-loop on a demo-grade baseline."""
    analysis = state.get("analysis")
    if analysis is None:
        return _halt(
            state,
            "I don't have a photo analysis yet — please upload the damaged part.",
            "PHOTO",
        )
    reasons = analysis.get("quality_reasons") or []
    if reasons:
        return _halt(
            state,
            "That photo is too blurry or poorly lit to analyse reliably. Could you "
            "retake it in better light, close-up, and clear of glare?",
            "PHOTO",
        )
    return {}


def route_damage_analysis(state: InspectionState) -> str:
    if state.get("halt"):
        return END
    return "feature_extraction"


def feature_extraction(state: InspectionState) -> dict[str, Any]:
    analysis = state.get("analysis") or {}
    features = analysis.get("features") or {}
    if not features:
        present = analysis.get("classes_present") or analysis.get("model_classes") or {}
        features = {
            "classes_present": present,
            "per_class_area_ratio_image": analysis.get("per_class_area_ratio_image") or {},
            "num_instances": analysis.get("num_instances") or 0,
            "damage_area_ratio_image": analysis.get("damage_area_ratio_image") or 0.0,
            "low_confidence_instances": analysis.get("low_confidence_instances") or 0,
            "width": analysis.get("width"),
            "height": analysis.get("height"),
        }
    return {"feature_summary": features}


def compare_user_vs_model(state: InspectionState) -> dict[str, Any]:
    classes = set((state.get("feature_summary") or {}).get("classes_present", {}).values())
    cmp = InspectionContext.compare_user_vs_model(
        {state.get("damage_location") or ""} - {""},
        classes,
    )
    return {"comparison": cmp.value}


def downstream_prediction(state: InspectionState, services: Services) -> dict[str, Any]:
    context = _build_context(state)
    features = _features_from_summary(state.get("feature_summary") or {})
    repair = services.repair_estimator.estimate(context, features)
    cost = services.cost_estimator.estimate(
        context, features, allow_synthetic=services.allow_synthetic
    )
    return {"repair": repair.model_dump(), "cost": cost.to_dict()}


def cost_availability(_state: InspectionState) -> dict[str, Any]:
    return {}


def repair_decision_validation(_state: InspectionState) -> dict[str, Any]:
    return {}


def result_validation(_state: InspectionState) -> dict[str, Any]:
    return {}


def final_explanation(state: InspectionState, services: Services) -> dict[str, Any]:
    summary = state.get("feature_summary") or {}
    repair = state.get("repair") or {}
    cost = state.get("cost") or {}
    payload = {
        "classes_present": summary.get("classes_present", {}),
        "repair_action": repair.get("action"),
        "cost_status": cost.get("status"),
        "consent": True,
    }
    explanation = services.groq.explain(payload)
    return _halt(
        state,
        explanation,
        "CONSENT",
    )


def consent_prompt(state: InspectionState, services: Services) -> dict[str, Any]:
    text = _last_user_text(state)
    try:
        ex = services.groq.extract(text)
        decision = ex.consent
    except Exception:
        decision = None
    if decision is None:
        return _halt(
            state,
            "Would you like to help us improve the model by keeping this photo and "
            "the anonymised damage analysis as a training sample? (yes / no)",
            "CONSENT",
        )
    if decision is ConsentDecision.DECLINED:
        return {
            "consent": ConsentDecision.DECLINED.value,
            "waiting_for": "FINISH",
            "reply": "No problem — your photo is used only for this inspection and "
            "is never kept for training.",
        }
    if decision is ConsentDecision.GRANTED:
        try:
            record = services.consent.record_decision(state["session_id"], ConsentDecision.GRANTED)
            saved = services.consent.store_training_sample(
                _build_context(state),
                _features_from_summary(state.get("feature_summary") or {}),
                consent=record,
                image_asset_id=state.get("image_asset_id") or "",
            )
            note = f" (sample stored: {saved.get('sample_id')})" if saved.get("saved") else ""
            reply = f"Thank you! Your anonymised sample has been kept for training{note}."
        except Exception:
            reply = "Thanks — I noted your consent but couldn't persist the sample right now."
        return {"consent": ConsentDecision.GRANTED.value, "waiting_for": "FINISH", "reply": reply}
    return _halt(state, "Sorry, I didn't catch that. Yes or no?", "CONSENT")


def finalize_session(state: InspectionState) -> dict[str, Any]:
    cost = state.get("cost") or {}
    if cost.get("status") == "DATA_UNAVAILABLE":
        reason = "cost data is unavailable"
    else:
        reason = "a demo estimate is shown (NOT a real quote)"
    classes = (state.get("feature_summary") or {}).get("classes_present", {})
    names = ", ".join(classes.values()) or "none clearly visible"
    repair = (state.get("repair") or {}).get("action", "manual review")
    reply = (
        f"Here's the summary:\n"
        f"• Damage found: {names}.\n"
        f"• Suggested next step: {repair} (preliminary demonstration rule).\n"
        f"• Cost: {reason}.\n"
        "Your uploaded photos are kept only for this inspection session and are "
        "deleted automatically after the session expires."
    )
    return {"finished": True, "waiting_for": None, "reply": reply, "halt": True}


# --------------------------------------------------------------------------- #
def _compile(services: Services) -> Any:
    b = StateGraph(InspectionState)

    b.add_node("understand_request", lambda s: understand_request(s, services))
    b.add_node("check_context_ready", lambda s: check_context_ready(s, services))
    b.add_node("collect_incident", lambda s: collect_incident(s, services))
    b.add_node("collect_damage_location", lambda s: collect_damage_location(s, services))
    b.add_node("collect_repair_location", lambda s: collect_repair_location(s, services))
    b.add_node("collect_insurance", lambda s: collect_insurance(s, services))
    b.add_node("photo_intake", lambda s: photo_intake(s))
    b.add_node("photo_validation", lambda s: photo_validation(s))
    b.add_node("damage_analysis", lambda s: damage_analysis(s))
    b.add_node("feature_extraction", lambda s: feature_extraction(s))
    b.add_node("compare_user_vs_model", lambda s: compare_user_vs_model(s))
    b.add_node("downstream_prediction", lambda s: downstream_prediction(s, services))
    b.add_node("cost_availability", lambda s: cost_availability(s))
    b.add_node("repair_decision_validation", lambda s: repair_decision_validation(s))
    b.add_node("result_validation", lambda s: result_validation(s))
    b.add_node("final_explanation", lambda s: final_explanation(s, services))
    b.add_node("consent_prompt", lambda s: consent_prompt(s, services))
    b.add_node("finalize_session", lambda s: finalize_session(s))

    b.add_edge(START, "understand_request")
    b.add_conditional_edges(
        "understand_request",
        route_entry,
        {
            "check_context_ready": "check_context_ready",
            "photo_validation": "photo_validation",
            "collect_incident": "collect_incident",
            "collect_damage_location": "collect_damage_location",
            "collect_repair_location": "collect_repair_location",
            "collect_insurance": "collect_insurance",
            "photo_intake": "photo_intake",
            "consent_prompt": "consent_prompt",
            "finalize_session": "finalize_session",
            END: END,
        },
    )

    for node in (
        "collect_incident",
        "collect_damage_location",
        "collect_repair_location",
        "collect_insurance",
        "photo_intake",
    ):
        b.add_edge(node, "understand_request")

    b.add_conditional_edges(
        "check_context_ready",
        route_after_context,
        {
            "check_context_ready": "check_context_ready",
            "photo_validation": "photo_validation",
            END: END,
        },
    )

    b.add_conditional_edges(
        "photo_validation", route_photo_validation, {"damage_analysis": "damage_analysis", END: END}
    )
    b.add_conditional_edges(
        "damage_analysis",
        route_damage_analysis,
        {"feature_extraction": "feature_extraction", END: END},
    )
    b.add_edge("feature_extraction", "compare_user_vs_model")
    b.add_edge("compare_user_vs_model", "downstream_prediction")
    b.add_edge("downstream_prediction", "cost_availability")
    b.add_edge("cost_availability", "repair_decision_validation")
    b.add_edge("repair_decision_validation", "result_validation")
    b.add_edge("result_validation", "final_explanation")
    b.add_edge("final_explanation", END)
    b.add_edge("consent_prompt", END)
    b.add_edge("finalize_session", END)

    return b.compile()


def build_workflow(services: Services) -> Any:
    """Return a compiled, deterministic LangGraph workflow."""
    return _compile(services)


def context_from_state(state: dict[str, Any]) -> InspectionContext:
    """Public alias used by routers to hand state facts to estimators."""
    return _build_context(state)


def features_from_summary(summary: dict[str, Any]) -> DamageFeatures:
    """Public alias so routers can feed the estimators honestly."""
    return _features_from_summary(summary or {})


def run_turn(
    workflow: Any,
    state: dict[str, Any],
    user_message: str | None = None,
) -> dict[str, Any]:
    """Run one chat turn against the persisted state; returns the new state."""
    if user_message:
        messages = list(state.get("messages", []))
        messages.append({"role": "user", "content": user_message})
        state = {**state, "messages": messages}
    state = dict(state)
    state["halt"] = False
    result = workflow.invoke(cast(InspectionState, state))
    return dict(result)
