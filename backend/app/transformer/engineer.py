from __future__ import annotations

from uuid import uuid4

from app.capabilities.contracts import (
    CapabilityRequest,
)
from app.capabilities.knowledge import (
    KNOWLEDGE_CANDIDATE_CAPABILITY_ID,
    KNOWLEDGE_CANDIDATE_MANIFEST,
    KnowledgeCandidateCapability,
)
from app.capabilities.registry import (
    CapabilityRegistry,
)
from app.capabilities.runtime import (
    CapabilityRuntime,
)

from app.capabilities.knowledge_relevance.capability import (
    KNOWLEDGE_RELEVANCE_CAPABILITY_ID,
    KnowledgeRelevanceCapability,
)
from app.capabilities.knowledge_relevance.capability_manifest import (
    KNOWLEDGE_RELEVANCE_CAPABILITY_MANIFEST,
)

from app.brain.engineering_brain import EngineeringBrain
from app.brain.engineering_session import EngineeringSession
from app.knowledge.bootstrap import build_default_registry
from app.knowledge.context_builder import build_knowledge_context
from app.transformer.knowledge import get_transformer_event_knowledge
from app.transformer.reasoning import evaluate_differential_trip_hypotheses
from app.transformer.schemas import TransformerDifferentialTripRequest


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = value.strip()

    if not cleaned:
        return None

    return cleaned


def clean_list(values: list[str]) -> list[str]:
    cleaned_values: list[str] = []

    for value in values:
        cleaned = clean_text(value)
        if cleaned is not None:
            cleaned_values.append(cleaned)

    return cleaned_values


class TransformerEngineer:
    def investigate_differential_trip(self, request: TransformerDifferentialTripRequest) -> dict:
        knowledge = get_transformer_event_knowledge("differential_trip")

        asset_id = clean_text(request.asset_id) or "Unknown Transformer"
        voltage_level = clean_text(request.voltage_level)
        event_description = clean_text(request.event_description) or "Transformer differential relay trip"
        relay_name = clean_text(request.relay_name)
        notes = clean_text(request.notes)

        known_available = set(clean_list(request.available_data))

        if request.comtrade_available:
            known_available.add("COMTRADE waveform")

        if request.dga_available:
            known_available.add("DGA report")

        if request.buchholz_alarm is not None:
            known_available.add("Buchholz relay status")

        if request.oil_temperature_c is not None:
            known_available.add("Oil temperature")

        if request.load_percent is not None:
            known_available.add("Load before trip")

        missing_required_evidence = [
            item
            for item in knowledge["required_evidence"]
            if item not in known_available
        ]

        for item in clean_list(request.missing_data):
            if item not in missing_required_evidence:
                missing_required_evidence.append(item)

        available_evidence = sorted(list(known_available))

        evidence_metadata = [
            metadata.model_dump()
            for metadata in request.evidence_metadata
        ]

        hypothesis_evaluations = evaluate_differential_trip_hypotheses(
            available_evidence=available_evidence,
            missing_required_evidence=missing_required_evidence,
            buchholz_alarm=request.buchholz_alarm,
            comtrade_available=request.comtrade_available,
            dga_available=request.dga_available,
            oil_temperature_c=request.oil_temperature_c,
            load_percent=request.load_percent,
            relay_targets=request.relay_targets,
            dga_status=request.dga_status,
            comtrade_summary=request.comtrade_summary,
        hv_breaker_status=request.hv_breaker_status,
        lv_breaker_status=request.lv_breaker_status,        )

        session = EngineeringSession(
            title=knowledge["description"],
            metadata={
                "engineering_role": "Transformer Engineer",
                "event_type": "differential_trip",
                "risk_level": knowledge["risk_level"],
                "asset_id": asset_id,
                "voltage_level": voltage_level,
            },
        )

        knowledge_registry = build_default_registry()

        knowledge_context = build_knowledge_context(
            knowledge_registry
        )

        session.metadata["knowledge_context"] = (
            knowledge_context.model_dump()
        )

        session.metadata["knowledge_audit"] = {
            "schema_version": knowledge_context.schema_version,
            "registry_source": "default_registry",
            "knowledge_count": len(
                knowledge_context.shadow.knowledge
            ),
            "knowledge_ids": [
                item.knowledge_id
                for item in knowledge_context.shadow.knowledge
            ],
            "shadow_mode": (
                knowledge_context.shadow.enabled
            ),
            "affects_decision": (
                knowledge_context.shadow.affects_decision
            ),
        }

        capability_registry = CapabilityRegistry()

        capability_registry.register(
            capability=KnowledgeCandidateCapability(
                registry=knowledge_registry,
            ),
            manifest=KNOWLEDGE_CANDIDATE_MANIFEST,
        )

        capability_registry.register(
            capability=KnowledgeRelevanceCapability(
                registry=knowledge_registry,
            ),
            manifest=(
                KNOWLEDGE_RELEVANCE_CAPABILITY_MANIFEST
            ),
        )

        capability_runtime = CapabilityRuntime(
            registry=capability_registry,
        )

        capability_executions = []

        capability_execution = capability_runtime.invoke(
            capability_id=(
                KNOWLEDGE_CANDIDATE_CAPABILITY_ID
            ),
            request=CapabilityRequest(
                request_id=(
                    "REQ-TRANSFORMER-KNOWLEDGE-"
                    f"{uuid4().hex}"
                ),
                payload={
                    "domain": "transformer",
                },
                context={
                    "execution_mode": "shadow",
                },
            ),
        )

        candidate_result = (
            capability_execution.result.output.get(
                "knowledge_candidate_result",
                {},
            )
        )

        relevance_execution = capability_runtime.invoke(
            capability_id=(
                KNOWLEDGE_RELEVANCE_CAPABILITY_ID
            ),
            request=CapabilityRequest(
                request_id=(
                    "REQ-TRANSFORMER-RELEVANCE-"
                    f"{uuid4().hex}"
                ),
                payload={
                    "domain": "transformer",
                    "asset_type": "power_transformer",
                    "available_evidence": tuple(
                        available_evidence
                    ),
                    "missing_evidence": tuple(
                        missing_required_evidence
                    ),
                    "investigation_stage": "initial",
                    "max_results": 5,
                },
                context={
                    "execution_mode": "shadow",
                },
            ),
        )

        relevance_result = (
            relevance_execution.result.output.get(
                "knowledge_relevance_result",
                {},
            )
        )

        capability_executions.append({
            "capability_id": (
                KNOWLEDGE_CANDIDATE_CAPABILITY_ID
            ),
            "status": (
                capability_execution.result.status
            ),
            "execution_mode": "shadow",
            "affects_decision": (
                capability_execution.result.affects_decision
            ),
            "duration_ms": (
                capability_execution.duration_ms
            ),
            "candidate_count": (
                candidate_result.get(
                    "candidate_count",
                    0,
                )
            ),
            "error": (
                capability_execution.error.model_dump()
                if capability_execution.error is not None
                else None
            ),
        })

        capability_executions.append({
            "capability_id": (
                KNOWLEDGE_RELEVANCE_CAPABILITY_ID
            ),
            "status": (
                relevance_execution.result.status
            ),
            "execution_mode": "shadow",
            "affects_decision": (
                relevance_execution.result.affects_decision
            ),
            "duration_ms": (
                relevance_execution.duration_ms
            ),
            "selected_count": len(
                relevance_result.get(
                    "selected_ids",
                    (),
                )
            ),
            "ignored_count": len(
                relevance_result.get(
                    "ignored_ids",
                    (),
                )
            ),
            "error": (
                relevance_execution.error.model_dump()
                if relevance_execution.error is not None
                else None
            ),
        })

        session.metadata["capability_executions"] = (
            capability_executions
        )
        session.add_observation({
            "asset_id": asset_id,
            "voltage_level": voltage_level,
            "event": event_description,
            "relay_name": relay_name,
            "oil_temperature_c": request.oil_temperature_c,
            "load_percent": request.load_percent,
            "buchholz_alarm": request.buchholz_alarm,
            "comtrade_available": request.comtrade_available,
            "dga_available": request.dga_available,
            "relay_targets": request.relay_targets,
            "dga_status": request.dga_status,
            "comtrade_summary": request.comtrade_summary,
            "hv_breaker_status": request.hv_breaker_status,
            "lv_breaker_status": request.lv_breaker_status,            "evidence_metadata": evidence_metadata,
            "notes": notes,
            "initial_safety_position": knowledge["initial_safety_position"],
            "available_evidence": available_evidence,
            "missing_required_evidence": missing_required_evidence,
            "source": "Transformer Knowledge v0.1",
        })

        for evaluation in hypothesis_evaluations:
            session.add_hypothesis({
                "hypothesis": evaluation["hypothesis"],
                "confidence": evaluation["confidence"],
                "supporting_evidence": evaluation["supporting_evidence"],
                "missing_evidence": evaluation["missing_evidence"],
                "conflicts": evaluation.get("conflicts", []),
                               "conflicting_evidence": evaluation.get(
                    "conflicting_evidence",
                    [],
                ),
                "risk": evaluation["risk"],
                "recommended_next_action": evaluation["recommended_next_action"],
                "why_supported": evaluation.get("why_supported", []),
                "why_not_confirmed": evaluation.get("why_not_confirmed", []),
                "confidence_drivers": evaluation.get("confidence_drivers", []),
                "confidence_limiters": evaluation.get("confidence_limiters", []),
                                "confidence_limiter_details": evaluation.get(
                    "confidence_limiter_details",
                    [],
                ),
                "evidence_that_would_change_decision": evaluation.get(
                    "evidence_that_would_change_decision",
                    [],
                ),
                "decision_change_details": evaluation.get(
                    "decision_change_details",
                    [],
                ),
                "source": "Transformer Reasoning v0.10",
            })

        brain = EngineeringBrain()
        completed_session = brain.run(session)

        return {
            "role": "Transformer Engineer",
            "event_type": "differential_trip",
            "status": completed_session.status.value,
            "session": completed_session.to_dict(),
        }



