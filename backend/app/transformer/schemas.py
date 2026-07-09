from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    evidence_name: str = Field(
        description="Name of the evidence item. It must match an item in available_data, missing_data, or evidence added by request flags."
    )
    source_type: EvidenceSourceType = Field(
        default="unknown",
        description="Source category of the evidence."
    )
    timestamp_relation: EvidenceTimestampRelation = Field(
        default="unknown",
        description="Whether the evidence was captured before, during, or after the event. Stored for future scoring refinement."
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
                        "verified": True
                    },
                    {
                        "evidence_name": "COMTRADE waveform",
                        "source_type": "comtrade",
                        "timestamp_relation": "during_event",
                        "verified": True
                    },
                    {
                        "evidence_name": "DGA report",
                        "source_type": "lab",
                        "timestamp_relation": "after_event",
                        "verified": True
                    },
                    {
                        "evidence_name": "Visual inspection",
                        "source_type": "field_inspection",
                        "timestamp_relation": "after_event",
                        "verified": False
                    }
                ],
                "notes": "Relay target shows differential operation. DGA abnormal. No inrush signature observed."
            }
        }
    )

    asset_id: str = Field(default="Transformer T1")
    voltage_level: str | None = Field(default=None)
    event_description: str = Field(default="Transformer differential relay trip")
    relay_name: str | None = Field(default=None)

    available_data: list[str] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)

    comtrade_available: bool = Field(default=False)
    dga_available: bool = Field(default=False)
    buchholz_alarm: bool | None = Field(default=None)

    oil_temperature_c: float | None = Field(default=None)
    load_percent: float | None = Field(default=None)

    relay_targets: list[str] = Field(default_factory=list)
    dga_status: DGAStatus = Field(default="not_available")
    comtrade_summary: COMTRADESummary = Field(default="not_available")

    evidence_metadata: list[EvidenceMetadata] = Field(default_factory=list)

    notes: str | None = Field(default=None)

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
