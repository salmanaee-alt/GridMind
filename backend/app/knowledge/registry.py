from __future__ import annotations

from collections.abc import Iterable

from app.knowledge.schema import (
    EngineeringKnowledgeObject,
)


class EngineeringKnowledgeRegistry:
    def __init__(
        self,
        initial_knowledge: (
            Iterable[EngineeringKnowledgeObject] | None
        ) = None,
    ) -> None:
        self._knowledge_by_id: dict[
            str,
            EngineeringKnowledgeObject,
        ] = {}

        if initial_knowledge is not None:
            for knowledge in initial_knowledge:
                self.register(knowledge)

    def register(
        self,
        knowledge: EngineeringKnowledgeObject,
    ) -> None:
        if not isinstance(
            knowledge,
            EngineeringKnowledgeObject,
        ):
            raise TypeError(
                "Registry accepts EngineeringKnowledgeObject "
                "instances only."
            )

        knowledge_id = knowledge.knowledge_id

        if knowledge_id in self._knowledge_by_id:
            raise ValueError(
                f"Knowledge ID {knowledge_id!r} is already "
                "registered."
            )

        self._knowledge_by_id[knowledge_id] = knowledge

    def get(
        self,
        knowledge_id: str,
    ) -> EngineeringKnowledgeObject | None:
        return self._knowledge_by_id.get(knowledge_id)

    def exists(
        self,
        knowledge_id: str,
    ) -> bool:
        return knowledge_id in self._knowledge_by_id

    def all(
        self,
    ) -> tuple[EngineeringKnowledgeObject, ...]:
        return tuple(self._knowledge_by_id.values())

    def by_domain(
        self,
        domain: str,
    ) -> tuple[EngineeringKnowledgeObject, ...]:
        return tuple(
            knowledge
            for knowledge in self._knowledge_by_id.values()
            if knowledge.domain == domain
        )

    def by_category(
        self,
        category: str,
    ) -> tuple[EngineeringKnowledgeObject, ...]:
        return tuple(
            knowledge
            for knowledge in self._knowledge_by_id.values()
            if knowledge.category == category
        )

    def by_status(
        self,
        status: str,
    ) -> tuple[EngineeringKnowledgeObject, ...]:
        return tuple(
            knowledge
            for knowledge in self._knowledge_by_id.values()
            if knowledge.status == status
        )
