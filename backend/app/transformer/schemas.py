from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TransformerDifferentialTripRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asset_id": "T1",
                "voltage_level": "230/13.8 kV",
                "event_description": "Transformer tripped by differential relay",
                "relay_name": "87T",
                "available_data": ["Relay event report"],
                "missing_data": [],
                "comtrade_available": False,
                "dga_available": False,
                "buchholz_alarm": None,
                "oil_temperature_c": 72,
                "load_percent": 65,
                "relay_targets": ["87T differential operated"],
                "dga_status": "not_available",
                "comtrade_summary": "not_available",
                "notes": "No smoke reported. Initial site inspection pending."
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
    dga_status: str | None = Field(default=None)
    comtrade_summary: str | None = Field(default=None)

    notes: str | None = Field(default=None)
