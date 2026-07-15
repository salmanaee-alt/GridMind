from __future__ import annotations

from dataclasses import dataclass

from app.capabilities.base import (
    EngineeringCapability,
)
from app.capabilities.contracts import (
    CAPABILITY_ABI_VERSION,
)
from app.capabilities.manifest import (
    CapabilityManifest,
)


@dataclass(frozen=True)
class CapabilityRegistration:
    capability: EngineeringCapability
    manifest: CapabilityManifest


class CapabilityRegistry:
    def __init__(self) -> None:
        self._registrations_by_id: dict[
            str,
            CapabilityRegistration,
        ] = {}

    def register(
        self,
        *,
        capability: EngineeringCapability,
        manifest: CapabilityManifest,
    ) -> None:
        if not isinstance(
            capability,
            EngineeringCapability,
        ):
            raise TypeError(
                "CapabilityRegistry accepts "
                "EngineeringCapability instances only."
            )

        if not isinstance(
            manifest,
            CapabilityManifest,
        ):
            raise TypeError(
                "CapabilityRegistry accepts "
                "CapabilityManifest instances only."
            )

        metadata = capability.metadata()

        if metadata.abi_version != CAPABILITY_ABI_VERSION:
            raise ValueError(
                "Capability metadata ABI version is incompatible "
                f"with the current ABI {CAPABILITY_ABI_VERSION}."
            )

        fields_to_match = (
            "capability_id",
            "name",
            "version",
            "abi_version",
            "shadow_only",
            "affects_decision",
        )

        for field_name in fields_to_match:
            metadata_value = getattr(
                metadata,
                field_name,
            )
            manifest_value = getattr(
                manifest,
                field_name,
            )

            if metadata_value != manifest_value:
                raise ValueError(
                    "Capability metadata and manifest "
                    f"{field_name} values must match."
                )

        capability_id = manifest.capability_id

        if capability_id in self._registrations_by_id:
            raise ValueError(
                f"Capability ID {capability_id!r} is already "
                "registered."
            )

        self._registrations_by_id[
            capability_id
        ] = CapabilityRegistration(
            capability=capability,
            manifest=manifest,
        )

    def get(
        self,
        capability_id: str,
    ) -> CapabilityRegistration | None:
        return self._registrations_by_id.get(
            capability_id
        )

    def exists(
        self,
        capability_id: str,
    ) -> bool:
        return capability_id in self._registrations_by_id

    def all(
        self,
    ) -> tuple[CapabilityRegistration, ...]:
        return tuple(
            self._registrations_by_id.values()
        )
