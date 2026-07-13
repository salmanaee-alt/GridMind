from app.knowledge.schema import (
    EngineeringKnowledgeObject,
    EngineeringReference,
    EngineeringRelationship,
    EvidenceRequirement,
    KnowledgeRevision,
    ValidationCase,
)


INTERNAL_TRANSFORMER_FAULT = EngineeringKnowledgeObject(
    knowledge_id="TR-EKO-0001",
    title="Internal Transformer Fault",
    domain="transformer",
    category="failure_mode",
    version="1.0.1",
    status="draft",
    definition=(
        "An electrical fault, or a mechanical defect with "
        "electrically or diagnostically observable effects, "
        "occurring within the transformer protection zone."
    ),
    physical_principles=(
        "An internal electrical fault can create differential "
        "current between the transformer terminal current "
        "measurements.",
        "Internal faults may produce thermal, dielectric, "
        "mechanical, and gas-generation effects depending on "
        "fault type and severity.",
        "Protection operation alone does not prove an internal "
        "fault and must be evaluated with corroborating evidence.",
    ),
    evidence_requirements=(
        EvidenceRequirement(
            evidence_name="Differential relay event report",
            evidence_role="required",
            rationale=(
                "Establishes which protection elements operated "
                "and records the relay event sequence."
            ),
        ),
        EvidenceRequirement(
            evidence_name="COMTRADE waveform",
            evidence_role="supporting",
            rationale=(
                "Supports evaluation of differential current, "
                "restraint current, harmonic content, and timing."
            ),
        ),
        EvidenceRequirement(
            evidence_name="DGA report",
            evidence_role="supporting",
            rationale=(
                "May provide corroborating evidence of thermal "
                "or electrical activity inside the transformer."
            ),
        ),
        EvidenceRequirement(
            evidence_name="Buchholz relay status",
            evidence_role="supporting",
            rationale=(
                "Gas accumulation or oil surge indication may "
                "support an internal-fault hypothesis."
            ),
        ),
        EvidenceRequirement(
            evidence_name="Magnetizing inrush indicators",
            evidence_role="contradicting",
            rationale=(
                "Strong inrush evidence may provide an alternative "
                "explanation for differential protection operation."
            ),
        ),
    ),
    relationships=(
        EngineeringRelationship(
            relationship_type="weakens",
            target_knowledge_id="TR-EKO-0002",
            description=(
                "Strong magnetizing-inrush evidence weakens an "
                "internal-fault-only interpretation but does not "
                "prove that the phenomena cannot coexist."
            ),
        ),
        EngineeringRelationship(
            relationship_type="related_to",
            target_knowledge_id="TR-EKO-0003",
            description=(
                "CT saturation can distort measured currents and "
                "must be considered during differential-trip review."
            ),
        ),
    ),
    references=(
        EngineeringReference(
            reference_type="guide",
            organization="IEEE",
            document_id="C37.91",
            title="Guide for Protecting Power Transformers",
            clause=None,
        ),
        EngineeringReference(
            reference_type="standard",
            organization="IEC",
            document_id="60076-1",
            title="Power transformers - General",
            clause=None,
        ),
        EngineeringReference(
            reference_type="standard",
            organization="IEC",
            document_id="60599",
            title=(
                "Mineral oil-filled electrical equipment in service - "
                "Guidance on the interpretation of dissolved and free gases analysis"
            ),
            clause=None,
        ),
    ),
    validation_cases=(
        ValidationCase(
            case_id="TR-VAL-0001",
            description=(
                "Differential trip with corroborating waveform, "
                "gas-relay, and diagnostic evidence."
            ),
            expected_outcome=(
                "The knowledge object is applicable as an internal "
                "fault diagnostic reference."
            ),
        ),
        ValidationCase(
            case_id="TR-VAL-0002",
            description=(
                "Differential trip with strong energization and "
                "inrush indicators but no internal-fault evidence."
            ),
            expected_outcome=(
                "The object remains relevant but its applicability "
                "is limited by the competing inrush explanation."
            ),
        ),
    ),
    known_limitations=(
        "Differential relay operation alone is not proof of an "
        "internal transformer fault.",
        "Some incipient internal faults may not produce immediately "
        "conclusive waveform or gas evidence.",
        "Dissolved-gas evidence depends on fault energy, gas-generation "
        "rate, oil circulation, sampling time, and sampling quality.",
    ),
    revision_history=(
        KnowledgeRevision(
            version="1.0.0",
            change_summary=(
                "Initial internal transformer fault knowledge object."
            ),
            changed_by="GridMind Engineering",
        ),
        KnowledgeRevision(
            version="1.0.1",
            change_summary=(
                "Demoted to draft pending specialist review; refined "
                "diagnostic observability, relationship semantics, "
                "DGA reference, and known limitations."
            ),
            changed_by="GridMind Engineering",
        ),
    ),
)


MAGNETIZING_INRUSH = EngineeringKnowledgeObject(
    knowledge_id="TR-EKO-0002",
    title="Magnetizing Inrush",
    domain="transformer",
    category="operating_phenomenon",
    version="1.0.1",
    status="draft",
    definition=(
        "A transient magnetizing-current condition that can occur "
        "during transformer energization or voltage recovery when "
        "the resulting flux trajectory drives the core into saturation."
    ),
    physical_principles=(
        "Residual flux and the energization point on the voltage "
        "wave can drive the magnetic core into transient saturation.",
        "The resulting current can be large, asymmetric, and rich "
        "in harmonic and non-periodic components.",
        "Inrush is an operating phenomenon and is not by itself "
        "evidence of an internal transformer fault.",
    ),
    evidence_requirements=(
        EvidenceRequirement(
            evidence_name="Energization event timing",
            evidence_role="required",
            rationale=(
                "Establishes whether the differential current began "
                "during transformer energization."
            ),
        ),
        EvidenceRequirement(
            evidence_name="COMTRADE waveform",
            evidence_role="supporting",
            rationale=(
                "Allows review of current asymmetry, waveform shape, "
                "harmonic content, and decay."
            ),
        ),
        EvidenceRequirement(
            evidence_name="Relay harmonic restraint status",
            evidence_role="supporting",
            rationale=(
                "Shows whether the relay identified or restrained "
                "an inrush-like condition."
            ),
        ),
        EvidenceRequirement(
            evidence_name="Internal fault diagnostic evidence",
            evidence_role="contradicting",
            rationale=(
                "Corroborating internal-fault evidence weakens an "
                "inrush-only explanation."
            ),
        ),
    ),
    relationships=(
        EngineeringRelationship(
            relationship_type="weakens",
            target_knowledge_id="TR-EKO-0001",
            description=(
                "Strong inrush evidence weakens an internal-fault-only "
                "interpretation but does not exclude simultaneous "
                "internal-fault evidence."
            ),
        ),
        EngineeringRelationship(
            relationship_type="related_to",
            target_knowledge_id="TR-EKO-0003",
            description=(
                "High transient current may coexist with CT "
                "measurement distortion and must be distinguished "
                "from CT saturation effects."
            ),
        ),
    ),
    references=(
        EngineeringReference(
            reference_type="guide",
            organization="IEEE",
            document_id="C37.91",
            title="Guide for Protecting Power Transformers",
            clause=None,
        ),
        EngineeringReference(
            reference_type="standard",
            organization="IEC",
            document_id="60076-1",
            title="Power transformers - General",
            clause=None,
        ),
    ),
    validation_cases=(
        ValidationCase(
            case_id="TR-VAL-0003",
            description=(
                "Transformer energization followed by asymmetric "
                "differential current and inrush restraint evidence."
            ),
            expected_outcome=(
                "The knowledge object is applicable as an inrush "
                "diagnostic reference."
            ),
        ),
    ),
    known_limitations=(
        "Second-harmonic content alone is not sufficient to prove "
        "magnetizing inrush.",
        "Modern transformer designs and switching conditions may "
        "produce inrush signatures that differ from simplified "
        "textbook patterns.",
        "Harmonic-restraint behavior depends on relay design, settings, "
        "waveform characteristics, and the duration of the transient.",
    ),
    revision_history=(
        KnowledgeRevision(
            version="1.0.0",
            change_summary=(
                "Initial magnetizing inrush knowledge object."
            ),
            changed_by="GridMind Engineering",
        ),
        KnowledgeRevision(
            version="1.0.1",
            change_summary=(
                "Demoted to draft pending specialist review; refined "
                "energization scope, relationship semantics, and "
                "harmonic-restraint limitations."
            ),
            changed_by="GridMind Engineering",
        ),
    ),
)


CT_SATURATION = EngineeringKnowledgeObject(
    knowledge_id="TR-EKO-0003",
    title="CT Saturation",
    domain="transformer",
    category="measurement_phenomenon",
    version="1.0.1",
    status="draft",
    definition=(
        "A condition in which a current transformer cannot reproduce "
        "the primary current accurately because its magnetic core "
        "is driven into saturation."
    ),
    physical_principles=(
        "High current magnitude, DC offset, remanence, connected "
        "burden, and CT capability influence saturation.",
        "Saturation distorts the secondary-current waveform and may "
        "create magnitude and phase errors.",
        "Unequal CT saturation can produce false differential current "
        "during high through-fault current."
    ),
    evidence_requirements=(
        EvidenceRequirement(
            evidence_name="COMTRADE waveform",
            evidence_role="required",
            rationale=(
                "Supports examination of waveform clipping, asymmetry, "
                "secondary-current distortion, and saturation timing."
            ),
        ),
        EvidenceRequirement(
            evidence_name="External fault evidence",
            evidence_role="supporting",
            rationale=(
                "A high through-fault current provides a plausible "
                "operating condition for CT saturation."
            ),
        ),
        EvidenceRequirement(
            evidence_name="CT ratio and class data",
            evidence_role="supporting",
            rationale=(
                "Supports assessment of CT capability relative to "
                "fault current and connected burden."
            ),
        ),
        EvidenceRequirement(
            evidence_name="Independent internal fault evidence",
            evidence_role="contradicting",
            rationale=(
                "Corroborating transformer internal-fault evidence "
                "weakens a CT-saturation-only explanation."
            ),
        ),
    ),
    relationships=(
        EngineeringRelationship(
            relationship_type="related_to",
            target_knowledge_id="TR-EKO-0001",
            description=(
                "CT saturation may imitate or distort differential "
                "current associated with an internal-fault hypothesis."
            ),
        ),
        EngineeringRelationship(
            relationship_type="related_to",
            target_knowledge_id="TR-EKO-0002",
            description=(
                "Both phenomena can distort differential-current "
                "interpretation but arise from different physics."
            ),
        ),
    ),
    references=(
        EngineeringReference(
            reference_type="guide",
            organization="IEEE",
            document_id="C37.91",
            title="Guide for Protecting Power Transformers",
            clause=None,
        ),
        EngineeringReference(
            reference_type="standard",
            organization="IEC",
            document_id="61869-2",
            title=(
                "Instrument transformers - Additional requirements "
                "for current transformers"
            ),
            clause=None,
        ),
    ),
    validation_cases=(
        ValidationCase(
            case_id="TR-VAL-0004",
            description=(
                "External high-current fault with distorted CT "
                "secondary waveform and apparent differential current."
            ),
            expected_outcome=(
                "The knowledge object is applicable as a CT saturation "
                "diagnostic reference."
            ),
        ),
    ),
    known_limitations=(
        "Waveform distortion must be evaluated with CT data, burden, "
        "fault magnitude, and event context.",
        "CT saturation does not exclude a simultaneous transformer "
        "internal fault."
    ),
    revision_history=(
        KnowledgeRevision(
            version="1.0.0",
            change_summary=(
                "Initial CT saturation knowledge object."
            ),
            changed_by="GridMind Engineering",
        ),
        KnowledgeRevision(
            version="1.0.1",
            change_summary=(
                "Demoted to draft pending specialist engineering review."
            ),
            changed_by="GridMind Engineering",
        ),
    ),
)


TRANSFORMER_KNOWLEDGE = (
    INTERNAL_TRANSFORMER_FAULT,
    MAGNETIZING_INRUSH,
    CT_SATURATION,
)
