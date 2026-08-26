from __future__ import annotations

from uuid import uuid4

from app.capabilities.contracts import (
    CapabilityExecutionRecord,
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
from app.capabilities.orchestrator import (
    CapabilityOrchestrator,
)

from app.capabilities.pipeline import (
    CapabilityPipelinePolicy,
    CapabilityPipelineStep,
)

from app.capabilities.knowledge_relevance.capability import (
    KNOWLEDGE_RELEVANCE_CAPABILITY_ID,
    KnowledgeRelevanceCapability,
)
from app.capabilities.knowledge_relevance.capability_manifest import (
    KNOWLEDGE_RELEVANCE_CAPABILITY_MANIFEST,
)

from app.capabilities.evidence_interpretation.capability import (
    EVIDENCE_INTERPRETATION_CAPABILITY_ID,
    EvidenceInterpretationCapability,
)
from app.capabilities.evidence_interpretation.capability_manifest import (
    EVIDENCE_INTERPRETATION_CAPABILITY_MANIFEST,
)

from app.capabilities.traceable_context.capability import (
    TRACEABLE_CONTEXT_CAPABILITY_ID,
    TraceableContextCapability,
)
from app.capabilities.traceable_context.capability_manifest import (
    TRACEABLE_CONTEXT_CAPABILITY_MANIFEST,
)

from app.transformer.physics_observation_builder import (
    build_differential_current_observation,
    build_harmonic_restraint_observation,
    build_differential_characteristic_observation,
    build_ct_saturation_observation,
    build_external_fault_discrimination_observation,
)

from app.transformer.physics import (
    calculate_differential_and_restraint_currents,
    evaluate_harmonic_physics_validity,
    evaluate_harmonic_restraint,
    normalize_current_to_ct_secondary,
    refer_current_to_voltage_side,
    summarize_differential_operating_region,
    evaluate_differential_characteristic,
)

from app.transformer.physics_contracts import (
    HarmonicRestraintSettings,
)

from app.brain.evidence_adapter import (
    physics_observation_to_evidence,
)

from app.brain.evidence_contracts import (
    EngineeringEvidence,
)
from app.brain.evidence_graph_builder import (
    build_evidence_graph,
)
from app.brain.evidence_graph_validation import (
    validate_evidence_graph,
)
from app.brain.evidence_relationship_validation import (
    validate_evidence_relationships,
)
from app.foundation.context import (
    ExecutionContext,
)

from app.reasoning.confidence_engine import (
    CONFIDENCE_REQUEST_RESOURCE_KEY,
    ConfidencePropagationEngine,
)

from app.reasoning.confidence_evidence_adapter import (
    build_confidence_request_from_evidence_graph,
)

from app.reasoning.evidence_confidence_boundary import (
    assess_evidence_confidence,
)

from app.reasoning.confidence_seed_eligibility import (
    assess_seed_eligibility,
)

from app.reasoning.confidence_calibration_policy import (
    ConfidenceCalibrationPolicy,
)

from app.transformer.ct_saturation_evaluator import (
    evaluate_ct_saturation,
)

from app.transformer.external_fault_discrimination import (
    evaluate_external_fault_discrimination,
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

        ct_saturation_result = None

        if request.ct_saturation_indicators is not None:
            ct_saturation_result = evaluate_ct_saturation(
                request.ct_saturation_indicators
            )

        hypothesis_evaluations = (
            evaluate_differential_trip_hypotheses(
                available_evidence=available_evidence,
                missing_required_evidence=(
                    missing_required_evidence
                ),
                buchholz_alarm=request.buchholz_alarm,
                comtrade_available=(
                    request.comtrade_available
                ),
                dga_available=request.dga_available,
                oil_temperature_c=(
                    request.oil_temperature_c
                ),
                load_percent=request.load_percent,
                relay_targets=request.relay_targets,
                dga_status=request.dga_status,
                comtrade_summary=request.comtrade_summary,
                hv_breaker_status=(
                    request.hv_breaker_status
                ),
                lv_breaker_status=(
                    request.lv_breaker_status
                ),
                physics_ct_saturation_status=(
                    ct_saturation_result.status
                    if ct_saturation_result is not None
                    else None
                ),
            )
        )

        session = EngineeringSession(            title=knowledge["description"],
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

        capability_registry.register(
            capability=EvidenceInterpretationCapability(),
            manifest=(
                EVIDENCE_INTERPRETATION_CAPABILITY_MANIFEST
            ),
        )

        capability_registry.register(
            capability=TraceableContextCapability(),
            manifest=(
                TRACEABLE_CONTEXT_CAPABILITY_MANIFEST
            ),
        )

        capability_runtime = CapabilityRuntime(
            registry=capability_registry,
        )

        capability_orchestrator = CapabilityOrchestrator(
            runtime=capability_runtime,
        )

        capability_policy = CapabilityPipelinePolicy(
            pipeline_id="transformer-knowledge",
            version="0.28.0",
            steps=(
                CapabilityPipelineStep(
                    capability_id=(
                        KNOWLEDGE_CANDIDATE_CAPABILITY_ID
                    ),
                ),
                CapabilityPipelineStep(
                    capability_id=(
                        KNOWLEDGE_RELEVANCE_CAPABILITY_ID
                    ),
                    depends_on=(
                        KNOWLEDGE_CANDIDATE_CAPABILITY_ID,
                    ),
                ),
                CapabilityPipelineStep(
                    capability_id=(
                        EVIDENCE_INTERPRETATION_CAPABILITY_ID
                    ),
                    depends_on=(
                        KNOWLEDGE_RELEVANCE_CAPABILITY_ID,
                    ),
                ),
            ),
        )

        capability_executions = []
        candidate_request = CapabilityRequest(
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
        )

        relevance_request = CapabilityRequest(
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
        )

        evidence_interpretation_request = CapabilityRequest(
            request_id=(
                "REQ-TRANSFORMER-EVIDENCE-"
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
            },
            context={
                "execution_mode": "shadow",
            },
        )

        (
            capability_execution,
            relevance_execution,
            evidence_interpretation_execution,
        ) = capability_orchestrator.execute_policy(
            policy=capability_policy,
            requests={
                KNOWLEDGE_CANDIDATE_CAPABILITY_ID: (
                    candidate_request
                ),
                KNOWLEDGE_RELEVANCE_CAPABILITY_ID: (
                    relevance_request
                ),
                EVIDENCE_INTERPRETATION_CAPABILITY_ID: (
                    evidence_interpretation_request
                ),
            },
        )
        candidate_result = (
            capability_execution.result.output.get(
                "knowledge_candidate_result",
                {},
            )
        )

        relevance_result = (
            relevance_execution.result.output.get(
                "knowledge_relevance_result",
                {},
            )
        )
        candidate_record = CapabilityExecutionRecord(
            capability_id=(
                KNOWLEDGE_CANDIDATE_CAPABILITY_ID
            ),
            status=(
                capability_execution.result.status
            ),
            execution_mode="shadow",
            affects_decision=(
                capability_execution.result.affects_decision
            ),
            duration_ms=(
                capability_execution.duration_ms
            ),
            error=(
                capability_execution.error.model_dump()
                if capability_execution.error is not None
                else None
            ),
        )

        candidate_audit = candidate_record.model_dump()

        candidate_audit["candidate_count"] = len(
            candidate_result.get(
                "candidates",
                (),
            )
        )

        capability_executions.append(
            candidate_audit
        )

        relevance_record = CapabilityExecutionRecord(
            capability_id=(
                KNOWLEDGE_RELEVANCE_CAPABILITY_ID
            ),
            status=(
                relevance_execution.result.status
            ),
            execution_mode="shadow",
            affects_decision=(
                relevance_execution.result.affects_decision
            ),
            duration_ms=(
                relevance_execution.duration_ms
            ),
            error=(
                relevance_execution.error.model_dump()
                if relevance_execution.error is not None
                else None
            ),
        )

        relevance_audit = relevance_record.model_dump()

        relevance_audit["selected_count"] = len(
            relevance_result.get(
                "selected_ids",
                (),
            )
        )

        relevance_audit["ignored_count"] = len(
            relevance_result.get(
                "ignored_ids",
                (),
            )
        )

        capability_executions.append(
            relevance_audit
        )

        evidence_interpretation_result = (
            evidence_interpretation_execution.result.output.get(
                "evidence_interpretation_result",
                {},
            )
        )

        traceable_context_request = CapabilityRequest(
            request_id=(
                "REQ-TRANSFORMER-TRACEABLE-"
                f"{uuid4().hex}"
            ),
            payload={
                "domain": "transformer",
                "asset_type": "power_transformer",
                "investigation_stage": "initial",
                "selected_knowledge_ids": tuple(
                    relevance_result.get(
                        "selected_ids",
                        (),
                    )
                ),
                "evidence_items": tuple(
                    {
                        "evidence": item.get(
                            "evidence",
                            "",
                        ),
                        "interpretation": item.get(
                            "interpretation",
                            "",
                        ),
                        "engineering_significance": item.get(
                            "engineering_significance",
                            "",
                        ),
                        "supporting_knowledge_ids": (),
                    }
                    for item in evidence_interpretation_result.get(
                        "interpretations",
                        (),
                    )
                ),
                "unresolved_evidence": tuple(
                    evidence_interpretation_result.get(
                        "unresolved_evidence",
                        (),
                    )
                ),
            },
            context={
                "execution_mode": "shadow",
            },
        )

        (
            traceable_context_execution,
        ) = capability_orchestrator.execute(
            executions=(
                (
                    TRACEABLE_CONTEXT_CAPABILITY_ID,
                    traceable_context_request,
                ),
            ),
        )

        traceable_context_result = (
            traceable_context_execution.result.output.get(
                "traceable_engineering_context",
                {},
            )
        )

        evidence_interpretation_record = (
            CapabilityExecutionRecord(
                capability_id=(
                    EVIDENCE_INTERPRETATION_CAPABILITY_ID
                ),
                status=(
                    evidence_interpretation_execution.result.status
                ),
                execution_mode="shadow",
                affects_decision=(
                    evidence_interpretation_execution.result.affects_decision
                ),
                duration_ms=(
                    evidence_interpretation_execution.duration_ms
                ),
                error=(
                    evidence_interpretation_execution.error.model_dump()
                    if evidence_interpretation_execution.error
                    is not None
                    else None
                ),
            )
        )

        evidence_interpretation_audit = (
            evidence_interpretation_record.model_dump()
        )

        evidence_interpretation_audit[
            "interpretation_count"
        ] = len(
            evidence_interpretation_result.get(
                "interpretations",
                (),
            )
        )

        evidence_interpretation_audit[
            "unresolved_count"
        ] = len(
            evidence_interpretation_result.get(
                "unresolved_evidence",
                (),
            )
        )

        traceable_context_record = (
            CapabilityExecutionRecord(
                capability_id=(
                    TRACEABLE_CONTEXT_CAPABILITY_ID
                ),
                status=(
                    traceable_context_execution.result.status
                ),
                execution_mode="shadow",
                affects_decision=(
                    traceable_context_execution.result.affects_decision
                ),
                duration_ms=(
                    traceable_context_execution.duration_ms
                ),
                error=(
                    traceable_context_execution.error.model_dump()
                    if traceable_context_execution.error
                    is not None
                    else None
                ),
            )
        )

        traceable_context_audit = (
            traceable_context_record.model_dump()
        )

        traceable_context_audit[
            "knowledge_count"
        ] = len(
            traceable_context_result.get(
                "knowledge_ids",
                (),
            )
        )

        traceable_context_audit[
            "evidence_count"
        ] = len(
            traceable_context_result.get(
                "evidence_items",
                (),
            )
        )

        traceable_context_audit[
            "unresolved_count"
        ] = len(
            traceable_context_result.get(
                "unresolved_evidence",
                (),
            )
        )

        traceable_context_audit[
            "traceability_complete"
        ] = traceable_context_result.get(
            "traceability_complete",
            False,
        )

        traceable_context_audit[
            "interpreted_evidence_count"
        ] = traceable_context_result.get(
            "interpreted_evidence_count",
            0,
        )

        traceable_context_audit[
            "traced_evidence_count"
        ] = traceable_context_result.get(
            "traced_evidence_count",
            0,
        )

        traceable_context_audit[
            "untraced_evidence_count"
        ] = traceable_context_result.get(
            "untraced_evidence_count",
            0,
        )

        traceable_context_audit[
            "traceability_ratio"
        ] = traceable_context_result.get(
            "traceability_ratio",
            0.0,
        )

        capability_executions.append(
            evidence_interpretation_audit
        )

        capability_executions.append(
            traceable_context_audit
        )

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
            "lv_breaker_status": request.lv_breaker_status,
            "evidence_metadata": evidence_metadata,
            "notes": notes,
            "initial_safety_position": knowledge["initial_safety_position"],
            "available_evidence": available_evidence,
            "missing_required_evidence": missing_required_evidence,
            "source": "Transformer Knowledge v0.1",
        })

        operating_region_summary = None

        if (
            request.physics_measurements is not None
            and request.physics_context is not None
        ):
            measurements = request.physics_measurements
            physics_context = request.physics_context

            if (
                measurements.hv_currents is not None
                and measurements.lv_currents is not None
                and measurements.hv_ct_ratio is not None
                and measurements.lv_ct_ratio is not None
                and measurements.hv_nominal_voltage_kv is not None
                and measurements.lv_nominal_voltage_kv is not None
                and physics_context.vector_group_compensation_applied
            ):
                hv_secondary = normalize_current_to_ct_secondary(
                    currents=measurements.hv_currents,
                    ct_ratio=measurements.hv_ct_ratio,
                )

                lv_secondary = normalize_current_to_ct_secondary(
                    currents=measurements.lv_currents,
                    ct_ratio=measurements.lv_ct_ratio,
                )

                lv_referred_to_hv = refer_current_to_voltage_side(
                    currents=lv_secondary,
                    from_voltage_kv=measurements.lv_nominal_voltage_kv,
                    to_voltage_kv=measurements.hv_nominal_voltage_kv,
                )

                differential_result = (
                    calculate_differential_and_restraint_currents(
                        hv_currents=hv_secondary,
                        lv_currents_referred_to_hv=lv_referred_to_hv,
                        context=physics_context,
                    )
                )

                differential_observation = (
                    build_differential_current_observation(
                        result=differential_result
                    )
                )

                if (
                    differential_result is not None
                    and request.differential_characteristic_settings
                    is not None
                ):
                    characteristic_result = (
                        evaluate_differential_characteristic(
                            currents=differential_result,
                            settings=(
                                request.differential_characteristic_settings
                            ),
                        )
                    )

                    operating_region_summary = (
                        summarize_differential_operating_region(
                            characteristic_result
                        )
                    )

                    characteristic_observation = (
                        build_differential_characteristic_observation(
                            result=characteristic_result,
                        )
                    )

                    session.add_observation(
                        characteristic_observation.model_dump()
                    )

                session.add_observation(
                    differential_observation.model_dump()
                )

                differential_evidence = (
                    physics_observation_to_evidence(
                        differential_observation
                    )
                )

                session.add_evidence(
                    differential_evidence.model_dump()
                )

        if (
            operating_region_summary is not None
            and ct_saturation_result is not None
        ):
            external_fault_result = (
                evaluate_external_fault_discrimination(
                    operating_region=(
                        operating_region_summary
                    ),
                    ct_saturation_status=(
                        ct_saturation_result.status
                    ),
                )
            )

            external_fault_observation = (
                build_external_fault_discrimination_observation(
                    result=external_fault_result,
                )
            )

            session.add_observation(
                external_fault_observation.model_dump()
            )

            external_fault_evidence = (
                physics_observation_to_evidence(
                    external_fault_observation
                )
            )

            session.add_evidence(
                external_fault_evidence.model_dump()
            )

        if request.harmonic_measurement is not None:
            harmonic_validity = (
                evaluate_harmonic_physics_validity(
                    measurement=request.harmonic_measurement
                )
            )

            harmonic_result = evaluate_harmonic_restraint(
                measurement=request.harmonic_measurement,
                settings=HarmonicRestraintSettings(
                    second_harmonic_threshold_percent=15.0,
                    fifth_harmonic_threshold_percent=20.0,
                ),
            )

            harmonic_observation = (
                build_harmonic_restraint_observation(
                    result=harmonic_result,
                    validity=harmonic_validity,
                )
            )

            session.add_observation(
                harmonic_observation.model_dump()
            )

            harmonic_evidence = (
                physics_observation_to_evidence(
                    harmonic_observation
                )
            )

            session.add_evidence(
                harmonic_evidence.model_dump()
            )

        if ct_saturation_result is not None:
            
            ct_saturation_observation = (
                build_ct_saturation_observation(
                    result=ct_saturation_result,
                )
            )

            session.add_observation(
                ct_saturation_observation.model_dump()
            )

            ct_saturation_evidence = (
                physics_observation_to_evidence(
                    ct_saturation_observation
                )
            )

            session.add_evidence(
                ct_saturation_evidence.model_dump()
            )

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

        engineering_evidence_objects = [
            EngineeringEvidence.model_validate(item)
            for item in session.evidence
        ]

        evidence_confidence_assessments = [
            assess_evidence_confidence(
                evidence_id=item.evidence_id,
                confidence=item.confidence,
            )
            for item in engineering_evidence_objects
        ]

        confidence_seed_eligibility_assessments = [
            assess_seed_eligibility(
                evidence_id=item.evidence_id,
                validity=item.validity,
                is_calibrated_probability=False,
            )
            for item in engineering_evidence_objects
        ]

        session.metadata[
            "confidence_seed_eligibility"
        ] = {
            "shadow_only": True,
            "affects_reasoning": False,
            "affects_decision": False,
            "assessments": [
                assessment.model_dump(
                    mode="json"
                )
                for assessment
                in confidence_seed_eligibility_assessments
            ],
        }

        session.metadata[
            "evidence_confidence_audit"
        ] = {
            "shadow_only": True,
            "affects_reasoning": False,
            "affects_decision": False,
            "assessments": [
                assessment.model_dump(
                    mode="json"
                )
                for assessment
                in evidence_confidence_assessments
            ],
        }

        evidence_graph = build_evidence_graph(
            engineering_evidence_objects
        )

        evidence_graph_validation = (
            validate_evidence_graph(
                evidence_graph
            )
        )

        evidence_relationships_validation = (
            validate_evidence_relationships(
                engineering_evidence_objects
            )
        )

        session.set_evidence_graph(
            evidence_graph.model_dump()
        )

        session.metadata["evidence_graph_validation"] = (
            evidence_graph_validation.model_dump()
        )

        session.metadata[
            "evidence_relationship_validation"
        ] = (
            evidence_relationships_validation.model_dump()
        )

        confidence_calibration_policy = (
            ConfidenceCalibrationPolicy(
                policy_id="CONF-CAL-DEFAULT",
                version="0.1",
            )
        )

        session.metadata[
            "confidence_calibration_policy"
        ] = (
            confidence_calibration_policy.model_dump(
                mode="json"
            )
        )

        confidence_seed_scores: dict[
            str,
            float,
        ] = {}

        confidence_request = (
            build_confidence_request_from_evidence_graph(
                graph=evidence_graph,
                confidence_scores=(
                    confidence_seed_scores
                ),
            )
        )

        confidence_result = (
            ConfidencePropagationEngine().execute(
                ExecutionContext(
                    resources={
                        CONFIDENCE_REQUEST_RESOURCE_KEY:
                            confidence_request,
                    }
                )
            )
        )

        session.metadata[
            "confidence_propagation"
        ] = {
            "shadow_only":
                confidence_result.shadow_only,
            "affects_reasoning":
                confidence_result.affects_reasoning,
            "affects_decision":
                confidence_result.affects_decision,
            "input_confidence_scores":
                confidence_seed_scores,
            "result":
                confidence_result.model_dump(
                    mode="json"
                ),
        }
        
        brain = EngineeringBrain()
        completed_session = brain.run(session)

        return {
            "role": "Transformer Engineer",
            "event_type": "differential_trip",
            "status": completed_session.status.value,
            "session": completed_session.to_dict(),
        }



