import pytest
from pydantic import ValidationError

from app.knowledge.schema import (
    EngineeringKnowledgeObject,
    EngineeringReference,
    EngineeringRelationship,
    EvidenceRequirement,
    KnowledgeRevision,
    ValidationCase,
)


def build_valid_eko(
    *,
    status: str = "draft",
) -> EngineeringKnowledgeObject:
    return EngineeringKnowledgeObject(
        knowledge_id="TR-EKO-0001",
        title="Internal Transformer Fault",
        domain="transformer",
        category="failure_mode",
        version="1.0.0",
        status=status,
        definition=(
            "An electrical or mechanical fault occurring "
            "inside the transformer protection zone."
        ),
        physical_principles=(
            "Fault current produces abnormal differential current.",
        ),
        evidence_requirements=(
            EvidenceRequirement(
                evidence_name="Differential relay event report",
                evidence_role="supporting",
                rationale=(
                    "Confirms differential element operation "
                    "and associated relay targets."
                ),
            ),
        ),
        relationships=(
            EngineeringRelationship(
                relationship_type="related_to",
                target_knowledge_id="TR-EKO-0002",
                description=(
                    "Must be differentiated from magnetizing inrush."
                ),
            ),
        ),
        references=(
            EngineeringReference(
                reference_type="standard",
                organization="IEEE",
                document_id="C37.91",
                title=(
                    "Guide for Protecting Power Transformers"
                ),
                clause=None,
            ),
        ),
        validation_cases=(
            ValidationCase(
                case_id="TR-VAL-0001",
                description=(
                    "Differential trip with corroborating "
                    "internal-fault evidence."
                ),
                expected_outcome=(
                    "Knowledge object remains applicable."
                ),
            ),
        ),
        known_limitations=(
            "Relay operation alone does not prove an internal fault.",
        ),
        revision_history=(
            KnowledgeRevision(
                version="1.0.0",
                change_summary="Initial schema validation record.",
                changed_by="GridMind Engineering",
            ),
        ),
    )


def test_engineering_knowledge_object_accepts_valid_structure():
    eko = build_valid_eko()

    assert eko.knowledge_id == "TR-EKO-0001"
    assert eko.status == "draft"
    assert len(eko.evidence_requirements) == 1
    assert len(eko.relationships) == 1
    assert len(eko.references) == 1
    assert len(eko.validation_cases) == 1
    assert len(eko.revision_history) == 1


def test_engineering_knowledge_object_rejects_invalid_id():
    with pytest.raises(ValidationError):
        EngineeringKnowledgeObject(
            knowledge_id="invalid-id",
            title="Invalid object",
            domain="transformer",
            category="failure_mode",
            version="1.0.0",
            status="draft",
            definition="Invalid identifier test.",
        )


def test_engineering_knowledge_schema_forbids_unknown_fields():
    payload = build_valid_eko().model_dump()
    payload["uncontrolled_rule"] = "if relay trips, declare fault"

    with pytest.raises(ValidationError):
        EngineeringKnowledgeObject(**payload)


def test_engineering_knowledge_object_is_read_only():
    eko = build_valid_eko()

    with pytest.raises(ValidationError):
        eko.title = "Modified title"


def test_approved_knowledge_requires_reference_and_validation_case():
    payload = build_valid_eko().model_dump()
    payload["status"] = "approved"
    payload["references"] = ()
    payload["validation_cases"] = ()

    with pytest.raises(
        ValidationError,
        match="approved knowledge",
    ):
        EngineeringKnowledgeObject(**payload)


def test_relationship_target_requires_valid_knowledge_id():
    with pytest.raises(ValidationError):
        EngineeringRelationship(
            relationship_type="supports",
            target_knowledge_id="bad-target",
            description="Invalid target identifier.",
        )


def test_schema_models_reject_empty_required_text():
    with pytest.raises(ValidationError):
        EvidenceRequirement(
            evidence_name="",
            evidence_role="required",
            rationale="Required evidence.",
        )

    with pytest.raises(ValidationError):
        ValidationCase(
            case_id="",
            description="Validation case.",
            expected_outcome="Expected result.",
        )


def test_nested_schema_models_are_read_only():
    reference = EngineeringReference(
        reference_type="standard",
        organization="IEC",
        document_id="60076",
        title="Power transformers",
        clause=None,
    )

    revision = KnowledgeRevision(
        version="1.0.0",
        change_summary="Initial revision.",
        changed_by="GridMind Engineering",
    )

    with pytest.raises(ValidationError):
        reference.title = "Changed title"

    with pytest.raises(ValidationError):
        revision.version = "2.0.0"


def test_approved_knowledge_requires_revision_history():
    payload = build_valid_eko().model_dump()
    payload["status"] = "approved"
    payload["revision_history"] = ()

    with pytest.raises(
        ValidationError,
        match="revision history",
    ):
        EngineeringKnowledgeObject(**payload)


def test_engineering_knowledge_rejects_blank_list_entries():
    payload = build_valid_eko().model_dump()
    payload["physical_principles"] = (
        "Valid principle.",
        "   ",
    )

    with pytest.raises(
        ValidationError,
        match="blank entries",
    ):
        EngineeringKnowledgeObject(**payload)

    payload = build_valid_eko().model_dump()
    payload["known_limitations"] = (
        "",
    )

    with pytest.raises(
        ValidationError,
        match="blank entries",
    ):
        EngineeringKnowledgeObject(**payload)
