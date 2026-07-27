from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


CurrentUnit = Literal["A"]


class ThreePhaseCurrentMeasurement(BaseModel):
    """
    Raw three-phase RMS current magnitudes.

    These are measurements only.
    No transformer-ratio, vector-group, or CT compensation
    is applied by this contract.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    phase_a: float = Field(ge=0.0)
    phase_b: float = Field(ge=0.0)
    phase_c: float = Field(ge=0.0)

    unit: CurrentUnit = "A"


class CTRatio(BaseModel):
    """
    Current-transformer primary/secondary ratio.

    Example:
        1200 / 1 A
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    primary_a: float = Field(gt=0.0)
    secondary_a: float = Field(gt=0.0)

    @property
    def ratio(self) -> float:
        return self.primary_a / self.secondary_a


class TransformerElectricalMeasurements(BaseModel):
    """
    Raw electrical measurements available for future
    transformer differential physics calculations.

    Shadow-only foundation.
    No protection decision is produced by this model.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    hv_currents: ThreePhaseCurrentMeasurement | None = None
    lv_currents: ThreePhaseCurrentMeasurement | None = None

    hv_ct_ratio: CTRatio | None = None
    lv_ct_ratio: CTRatio | None = None

    hv_nominal_voltage_kv: float | None = Field(
        default=None,
        gt=0.0,
    )
    lv_nominal_voltage_kv: float | None = Field(
        default=None,
        gt=0.0,
    )

    @model_validator(mode="after")
    def validate_measurement_pairing(
        self,
    ) -> "TransformerElectricalMeasurements":
        if (
            self.hv_currents is not None
            and self.hv_ct_ratio is None
        ):
            raise ValueError(
                "hv_ct_ratio is required when "
                "hv_currents are provided."
            )

        if (
            self.lv_currents is not None
            and self.lv_ct_ratio is None
        ):
            raise ValueError(
                "lv_ct_ratio is required when "
                "lv_currents are provided."
            )

        return self
VectorGroup = Literal[
    "unknown",
    "YNyn0",
    "Yy0",
    "Dyn1",
    "Dyn11",
    "Yd1",
    "Yd11",
]


class TransformerDifferentialPhysicsContext(BaseModel):
    """
    Configuration required before differential-current
    quantities may be considered physically comparable.

    Shadow-only. No protection decision is produced.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    vector_group: VectorGroup = "unknown"

    vector_group_compensation_applied: bool = False

    affects_decision: bool = False

    @model_validator(mode="after")
    def validate_vector_group_compensation(
        self,
    ) -> "TransformerDifferentialPhysicsContext":
        if (
            self.vector_group == "unknown"
            and self.vector_group_compensation_applied
        ):
            raise ValueError(
                "vector-group compensation cannot be "
                "declared applied when vector_group is unknown."
            )

        return self


class DifferentialCurrentResult(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    phase_a_diff_a: float = Field(ge=0.0)
    phase_b_diff_a: float = Field(ge=0.0)
    phase_c_diff_a: float = Field(ge=0.0)

    phase_a_restraint_a: float = Field(ge=0.0)
    phase_b_restraint_a: float = Field(ge=0.0)
    phase_c_restraint_a: float = Field(ge=0.0)

    affects_decision: bool = False


class DifferentialCharacteristicSettings(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    pickup_a: float = Field(gt=0.0)
    slope: float = Field(ge=0.0)

    affects_decision: bool = False


class DifferentialCharacteristicEvaluation(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    phase_a_operate: bool
    phase_b_operate: bool
    phase_c_operate: bool

    phase_a_threshold_a: float = Field(ge=0.0)
    phase_b_threshold_a: float = Field(ge=0.0)
    phase_c_threshold_a: float = Field(ge=0.0)

    affects_decision: bool = False


class HarmonicCurrentMeasurement(BaseModel):
    """
    Harmonic current magnitudes for one measured phase.

    Values represent current magnitudes only.
    No inrush, overexcitation, restraint, or trip
    conclusion is inferred by this contract.

    Shadow-only physics data.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    fundamental_a: float = Field(ge=0.0)

    second_harmonic_a: float = Field(
        default=0.0,
        ge=0.0,
    )

    fifth_harmonic_a: float = Field(
        default=0.0,
        ge=0.0,
    )

    affects_decision: bool = False


class HarmonicCurrentMeasurement(BaseModel):
    """
    Harmonic current magnitudes for one measured phase.

    Values represent current magnitudes only.
    No inrush, overexcitation, restraint, or trip
    conclusion is inferred by this contract.

    Shadow-only physics data.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    fundamental_a: float = Field(ge=0.0)

    second_harmonic_a: float = Field(
        default=0.0,
        ge=0.0,
    )

    fifth_harmonic_a: float = Field(
        default=0.0,
        ge=0.0,
    )

    affects_decision: bool = False


class HarmonicRestraintSettings(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    second_harmonic_threshold_percent: float = Field(
        gt=0.0,
    )

    fifth_harmonic_threshold_percent: float = Field(
        gt=0.0,
    )

    affects_decision: bool = False


class HarmonicRestraintEvaluation(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    second_harmonic_restraint: bool
    fifth_harmonic_restraint: bool
    any_harmonic_restraint: bool

    ratios_defined: bool

    affects_decision: bool = False


HarmonicValidityStatus = Literal[
    "valid",
    "unavailable",
    "indeterminate",
]


class HarmonicPhysicsValidity(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    status: HarmonicValidityStatus
    reason: str

    affects_decision: bool = False
    