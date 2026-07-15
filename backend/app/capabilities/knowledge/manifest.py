from app.capabilities.contracts import (
    CAPABILITY_ABI_VERSION,
)
from app.capabilities.knowledge.capability import (
    KNOWLEDGE_CANDIDATE_CAPABILITY_ID,
)
from app.capabilities.manifest import (
    CapabilityManifest,
)


KNOWLEDGE_CANDIDATE_MANIFEST = CapabilityManifest(
    capability_id=KNOWLEDGE_CANDIDATE_CAPABILITY_ID,
    name="Knowledge Candidate Generator",
    version="1.0.0",
    abi_version=CAPABILITY_ABI_VERSION,
    domain="knowledge",
    requires=(
        "engineering_knowledge_registry",
        "domain",
    ),
    produces=(
        "knowledge_candidate_result",
    ),
    shadow_only=True,
    affects_decision=False,
    status="experimental",
    author="GridMind AI",
)
