from app.capabilities.contracts import (
    CAPABILITY_ABI_VERSION,
)
from app.capabilities.manifest import (
    CapabilityManifest,
)
from app.capabilities.traceable_context.capability import (
    TRACEABLE_CONTEXT_CAPABILITY_ID,
)


TRACEABLE_CONTEXT_CAPABILITY_MANIFEST = (
    CapabilityManifest(
        capability_id=(
            TRACEABLE_CONTEXT_CAPABILITY_ID
        ),
        name="Traceable Engineering Context",
        version="1.0.0",
        abi_version=CAPABILITY_ABI_VERSION,
        domain="transformer",
        requires=(
            "domain",
            "asset_type",
            "investigation_stage",
            "selected_knowledge_ids",
            "evidence_items",
        ),
        produces=(
            "traceable_engineering_context",
        ),
        shadow_only=True,
        affects_decision=False,
        status="experimental",
        author="GridMind AI",
    )
)
