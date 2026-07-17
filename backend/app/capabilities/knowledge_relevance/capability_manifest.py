from app.capabilities.contracts import (
    CAPABILITY_ABI_VERSION,
)
from app.capabilities.knowledge_relevance.capability import (
    KNOWLEDGE_RELEVANCE_CAPABILITY_ID,
)
from app.capabilities.manifest import (
    CapabilityManifest,
)


KNOWLEDGE_RELEVANCE_CAPABILITY_MANIFEST = (
    CapabilityManifest(
        capability_id=(
            KNOWLEDGE_RELEVANCE_CAPABILITY_ID
        ),
        name="Knowledge Relevance",
        version="1.0.0",
        abi_version=CAPABILITY_ABI_VERSION,
        domain="knowledge",
        requires=(
            "engineering_knowledge_registry",
            "domain",
            "asset_type",
            "investigation_stage",
            "max_results",
        ),
        produces=(
            "knowledge_relevance_result",
        ),
        shadow_only=True,
        affects_decision=False,
        status="experimental",
        author="GridMind AI",
    )
)