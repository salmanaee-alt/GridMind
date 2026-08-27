from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.transformer.physics_contracts import (
    HarmonicCurrentMeasurement,
    TransformerDifferentialPhysicsContext,
    TransformerElectricalMeasurements,
    DifferentialCharacteristicSettings,
)

from app.transformer.ct_saturation_contracts import (
    CTSaturationIndicators,
)

from app.transformer.through_fault_context import (
    ThroughFaultContext,
)

DGAStatus = Literal[
    "not_available",
    "normal",
    "abnormal",
    "critical",
    "alarm",
    "high_gas",
    "fault_gas_detected",
]

COMTRADESummary = Literal[
    "not_available",
    "inrush_detected",
    "no_inrush",
    "ct_saturation",
    "ct_circuit_issue",
    "normal_waveform",
    "unknown",
]

BreakerStatus = Literal[
    "unknown",
    "open",
    "closed",
    "tripped",
    "failed_to_open",
]


MAX_COLLECTION_ITEMS = 100
MAX_SHORT_TEXT_LENGTH = 200
MAX_EVIDENCE_TEXT_LENGTH = 500
MAX_EVENT_DESCRIPTION_LENGTH = 2000
MAX_NOTES_LENGTH = 5000

ShortText = Annotated[
    str,
    StringConstraints(max_length=MAX_SHORT_TEXT_LENGTH),
]

EvidenceText = Annotated[
    str,
    StringConstraints(max_length=MAX_EVIDENCE_TEXT_LENGTH),
]

EvidenceSourceType = Literal[
    "relay",
    "comtrade",
    "lab",
    "field_inspection",
    "operator",
    "scada",
    "maintenance",
    "unknown",
]

EvidenceTimestampRelation = Literal[
    "before_event",
    "during_event",
    "after_event",
    "not_applicable",
    "unknown",
]


class EvidenceMetadata(BaseModel):
    evidence_name: EvidenceText = Field(
        description="Name of the evidence item. It must match an item in available_data, missing_data, or evidence added by request flags."
    )
    source_type: EvidenceSourceType = Field(
        default="unknown",
        description="Source category of the evidence."
    )
    timestamp_relation: EvidenceTimestampRelation = Field(
        default="unknown",
        description="Whether the evidence was captured before, during, or after the event. Used by timestamp-aware evidence quality scoring."
    )
    evidence_age_days: int | None = Field(
        default=None,
        ge=0,
        description="Age of the evidence in days. Used for evidence freshness scoring. None means unknown."
    )
    verified: bool = Field(
        default=False,
        description="Whether this evidence has been verified. Used by metadata-aware evidence quality scoring."
    )


class TransformerDifferentialTripRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "T1",
                "voltage_level": "230/13.8 kV",
                "event_description": "Transformer tripped by differential relay",
                "relay_name": "87T",
                "available_data": [
                    "Relay event report",
                    "Differential relay targets"
                ],
                "missing_data": [
                    "Visual inspection"
                ],
                "comtrade_available": True,
                "dga_available": True,
                "buchholz_alarm": False,
                "oil_temperature_c": 72,
                "load_percent": 65,
                "relay_targets": ["87T differential operated"],
                "dga_status": "abnormal",
                "comtrade_summary": "no_inrush",
                "evidence_metadata": [
                    {
                        "evidence_name": "Relay event report",
                        "source_type": "relay",
                        "timestamp_relation": "during_event",
                        "evidence_age_days": 0,
                        "verified": True
                    },
                    {
                        "evidence_name": "COMTRADE waveform",
                        "source_type": "comtrade",
                        "timestamp_relation": "during_event",
                        "evidence_age_days": 0,
                        "verified": True
                    },
                    {
                        "evidence_name": "DGA report",
                        "source_type": "lab",
                        "timestamp_relation": "after_event",
                        "evidence_age_days": 2,
                        "verified": True
                    },
                    {
                        "evidence_name": "Visual inspection",
                        "source_type": "field_inspection",
                        "timestamp_relation": "after_event",
                        "evidence_age_days": 1,
                        "verified": False
                    }
                ],
                "notes": "Relay target shows differential operation. DGA abnormal. No inrush signature observed."
            }
        }
    )

    asset_id: ShortText = Field(
        default="Transformer T1"
    )
    voltage_level: ShortText | None = Field(
        default=None
    )
    event_description: str = Field(
        default="Transformer differential relay trip",
        max_length=MAX_EVENT_DESCRIPTION_LENGTH,
    )
    relay_name: ShortText | None = Field(
        default=None
    )

    available_data: list[EvidenceText] = Field(
        default_factory=list,
        max_length=MAX_COLLECTION_ITEMS,
    )
    missing_data: list[EvidenceText] = Field(
        default_factory=list,
        max_length=MAX_COLLECTION_ITEMS,
    )

    comtrade_available: bool = Field(default=False)
    dga_available: bool = Field(default=False)
    buchholz_alarm: bool | None = Field(default=None)

    oil_temperature_c: float | None = Field(default=None)
    load_percent: float | None = Field(default=None)

    hv_breaker_status: BreakerStatus = Field(
        default="unknown",
        description="HV side breaker status after the transformer differential trip."
    )
    lv_breaker_status: BreakerStatus = Field(
        default="unknown",
        description="LV side breaker status after the transformer differential trip."
    )

    relay_targets: list[EvidenceText] = Field(
        default_factory=list,
        max_length=MAX_COLLECTION_ITEMS,
    )
    dga_status: DGAStatus = Field(default="not_available")
    comtrade_summary: COMTRADESummary = Field(default="not_available")

    physics_measurements: TransformerElectricalMeasurements | None = Field(
        default=None,
        description=(
            "Optional raw electrical measurements for shadow-only "
            "transformer physics calculations."
        ),
    )

    physics_context: TransformerDifferentialPhysicsContext | None = Field(
        default=None,
        description=(
            "Optional transformer differential physics context. "
            "Shadow-only and does not affect engineering decisions."
        ),
    )

    differential_characteristic_settings: (
    DifferentialCharacteristicSettings | None
    ) = Field(

        default=None,
        description=(
            "Optional relay differential characteristic "
            "settings for shadow-only physics evaluation."
        ),
    )

    ct_saturation_indicators: (
        CTSaturationIndicators | None
    ) = Field(
        default=None,
        description=(
            "Optional CT saturation indicators for "
            "shadow-only engineering evaluation."
        ),
    )

    through_fault_context: (
        ThroughFaultContext | None
    ) = Field(
        default=None,
        description=(
            "Optional through-fault and protection sequence "
            "context for shadow-only engineering evaluation."
        ),
    )

    harmonic_measurement: HarmonicCurrentMeasurement | None = Field(
        default=None,
        description=(
            "Optional harmonic current measurement for shadow-only "
            "harmonic physics evaluation."
        ),
    )

    evidence_metadata: list[EvidenceMetadata] = Field(
        default_factory=list,
        max_length=MAX_COLLECTION_ITEMS,
    )

    notes: str | None = Field(
        default=None,
        max_length=MAX_NOTES_LENGTH,
    )

    @model_validator(mode="after")
    def validate_evidence_metadata_names(self) -> "TransformerDifferentialTripRequest":
        allowed_evidence_names = set(self.available_data + self.missing_data)

        if self.comtrade_available:
            allowed_evidence_names.add("COMTRADE waveform")

        if self.dga_available:
            allowed_evidence_names.add("DGA report")

        if self.buchholz_alarm is not None:
            allowed_evidence_names.add("Buchholz relay status")

        if self.oil_temperature_c is not None:
            allowed_evidence_names.add("Oil temperature")

        if self.load_percent is not None:
            allowed_evidence_names.add("Load before trip")

        seen_metadata_names: set[str] = set()
        duplicate_metadata_names: list[str] = []

        for item in self.evidence_metadata:
            evidence_name = item.evidence_name

            if (
                evidence_name in seen_metadata_names
                and evidence_name not in duplicate_metadata_names
            ):
                duplicate_metadata_names.append(evidence_name)

            seen_metadata_names.add(evidence_name)

        if duplicate_metadata_names:
            raise ValueError(
                "evidence_metadata must contain unique evidence_name "
                "values. Duplicate names: "
                f"{duplicate_metadata_names}"
            )

        invalid_metadata_names = [
            item.evidence_name
            for item in self.evidence_metadata
            if item.evidence_name not in allowed_evidence_names
        ]

        if invalid_metadata_names:
            raise ValueError(
                "Each evidence_metadata.evidence_name must match an item in available_data, missing_data, or evidence added by request flags. "
                f"Invalid evidence metadata names: {invalid_metadata_names}"
            )

        return self
