from app.capabilities.contracts import (
    CAPABILITY_ABI_VERSION,
)
from app.capabilities.evidence_interpretation.capability import (
    EVIDENCE_INTERPRETATION_CAPABILITY_ID,
)
from app.capabilities.manifest import (
    CapabilityManifest,
)


EVIDENCE_INTERPRETATION_CAPABILITY_MANIFEST = (
    CapabilityManifest(
        capability_id=(
            EVIDENCE_INTERPRETATION_CAPABILITY_ID
        ),
        name="Evidence Interpretation",
        version="1.0.0",
        abi_version=CAPABILITY_ABI_VERSION,
        domain="transformer",
        requires=(
            "domain",
            "asset_type",
            "available_evidence",
            "investigation_stage",
        ),
        produces=(
            "evidence_interpretation_result",
        ),
        shadow_only=True,
        affects_decision=False,
        status="experimental",
        author="GridMind AI",
    )
)
