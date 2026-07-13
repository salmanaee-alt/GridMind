from app.knowledge.transformer import (
    TRANSFORMER_KNOWLEDGE,
)


def test_transformer_knowledge_contains_three_objects():
    assert len(TRANSFORMER_KNOWLEDGE) == 3


def test_transformer_knowledge_ids_are_unique():
    ids = [
        item.knowledge_id
        for item in TRANSFORMER_KNOWLEDGE
    ]

    assert len(ids) == len(set(ids))


def test_internal_fault_object_exists():
    knowledge = next(
        item
        for item in TRANSFORMER_KNOWLEDGE
        if item.knowledge_id == "TR-EKO-0001"
    )

    assert knowledge.title == "Internal Transformer Fault"
    assert knowledge.domain == "transformer"
    assert knowledge.category == "failure_mode"
    assert len(knowledge.references) >= 1
    assert len(knowledge.validation_cases) >= 1
    assert len(knowledge.evidence_requirements) >= 1
    assert len(knowledge.relationships) >= 1


def test_inrush_object_exists():
    knowledge = next(
        item
        for item in TRANSFORMER_KNOWLEDGE
        if item.knowledge_id == "TR-EKO-0002"
    )

    assert knowledge.title == "Magnetizing Inrush"


def test_ct_saturation_object_exists():
    knowledge = next(
        item
        for item in TRANSFORMER_KNOWLEDGE
        if item.knowledge_id == "TR-EKO-0003"
    )

    assert knowledge.title == "CT Saturation"


def test_all_transformer_knowledge_objects_are_structurally_complete():
    for knowledge in TRANSFORMER_KNOWLEDGE:
        assert len(knowledge.revision_history) >= 1
        assert len(knowledge.physical_principles) >= 1
        assert len(knowledge.known_limitations) >= 1


def test_transformer_knowledge_relationships_reference_existing_objects():
    knowledge_ids = {
        item.knowledge_id
        for item in TRANSFORMER_KNOWLEDGE
    }

    for knowledge in TRANSFORMER_KNOWLEDGE:
        for relationship in knowledge.relationships:
            assert relationship.target_knowledge_id in knowledge_ids
            assert (
                relationship.target_knowledge_id
                != knowledge.knowledge_id
            )


def test_transformer_validation_case_ids_are_unique():
    case_ids = [
        validation_case.case_id
        for knowledge in TRANSFORMER_KNOWLEDGE
        for validation_case in knowledge.validation_cases
    ]

    assert len(case_ids) == len(set(case_ids))


def test_transformer_references_are_unique_within_each_object():
    for knowledge in TRANSFORMER_KNOWLEDGE:
        reference_keys = [
            (
                reference.reference_type,
                reference.organization,
                reference.document_id,
                reference.clause,
            )
            for reference in knowledge.references
        ]

        assert len(reference_keys) == len(set(reference_keys))


def test_transformer_knowledge_contains_no_blank_text_entries():
    for knowledge in TRANSFORMER_KNOWLEDGE:
        assert knowledge.title.strip()
        assert knowledge.definition.strip()

        for principle in knowledge.physical_principles:
            assert principle.strip()

        for limitation in knowledge.known_limitations:
            assert limitation.strip()

        for evidence in knowledge.evidence_requirements:
            assert evidence.evidence_name.strip()
            assert evidence.rationale.strip()

        for relationship in knowledge.relationships:
            assert relationship.description.strip()

        for reference in knowledge.references:
            assert reference.organization.strip()
            assert reference.document_id.strip()
            assert reference.title.strip()

        for validation_case in knowledge.validation_cases:
            assert validation_case.case_id.strip()
            assert validation_case.description.strip()
            assert validation_case.expected_outcome.strip()


def test_transformer_knowledge_collection_is_read_only_tuple():
    assert isinstance(TRANSFORMER_KNOWLEDGE, tuple)


def test_transformer_knowledge_objects_remain_draft_until_human_approval():
    for knowledge in TRANSFORMER_KNOWLEDGE:
        assert knowledge.status == "draft"


def test_transformer_evidence_names_are_unique_within_each_object():
    for knowledge in TRANSFORMER_KNOWLEDGE:
        evidence_names = [
            evidence.evidence_name
            for evidence in knowledge.evidence_requirements
        ]

        assert len(evidence_names) == len(set(evidence_names))


def test_transformer_relationships_are_unique_within_each_object():
    for knowledge in TRANSFORMER_KNOWLEDGE:
        relationship_keys = [
            (
                relationship.relationship_type,
                relationship.target_knowledge_id,
            )
            for relationship in knowledge.relationships
        ]

        assert len(relationship_keys) == len(
            set(relationship_keys)
        )


def test_transformer_revision_version_matches_object_version():
    for knowledge in TRANSFORMER_KNOWLEDGE:
        assert knowledge.revision_history[-1].version == (
            knowledge.version
        )


def test_internal_fault_and_inrush_use_weakening_relationships():
    internal_fault = next(
        item
        for item in TRANSFORMER_KNOWLEDGE
        if item.knowledge_id == "TR-EKO-0001"
    )
    inrush = next(
        item
        for item in TRANSFORMER_KNOWLEDGE
        if item.knowledge_id == "TR-EKO-0002"
    )

    internal_to_inrush = next(
        relationship
        for relationship in internal_fault.relationships
        if relationship.target_knowledge_id == "TR-EKO-0002"
    )
    inrush_to_internal = next(
        relationship
        for relationship in inrush.relationships
        if relationship.target_knowledge_id == "TR-EKO-0001"
    )

    assert internal_to_inrush.relationship_type == "weakens"
    assert inrush_to_internal.relationship_type == "weakens"
