from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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
                    "COMTRADE waveform",
                    "Differential relay targets",
                    "DGA report",
                    "Buchholz relay status",
                    "Oil temperature",
                    "Load before trip"
                ],
                "missing_data": [],
                "comtrade_available": True,
                "dga_available": True,
                "buchholz_alarm": False,
                "oil_temperature_c": 72,
                "load_percent": 65,
                "relay_targets": ["87T differential operated"],
                "dga_status": "abnormal",
                "comtrade_summary": "no_inrush",
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

    notes: str | None = Field(default=None)
