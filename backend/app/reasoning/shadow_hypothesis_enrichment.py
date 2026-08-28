from __future__ import annotations

from copy import deepcopy
from typing import Any


def enrich_hypothesis_with_shadow_support(
    *,
    hypothesis: dict[str, Any],
    target_hypothesis: str | None = None,
    support: str,
    source: str,
) -> dict[str, Any]:
    enriched = deepcopy(hypothesis)

    if (
        target_hypothesis is not None
        and hypothesis.get("hypothesis")
        != target_hypothesis
    ):
        return enriched

    supporting_evidence = list(
        enriched.get("supporting_evidence", [])
    )

    if support not in supporting_evidence:
        supporting_evidence.append(support)

    enriched["supporting_evidence"] = (
        supporting_evidence
    )

    provenance = list(
        enriched.get(
            "shadow_support_provenance",
            [],
        )
    )

    provenance_entry = {
        "support": support,
        "source": source,
    }

    if provenance_entry not in provenance:
        provenance.append(
            provenance_entry
        )

    enriched[
        "shadow_support_provenance"
    ] = provenance

    return enriched