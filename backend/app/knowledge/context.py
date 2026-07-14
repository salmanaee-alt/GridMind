from __future__ import annotations

from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.knowledge.schema import KnowledgeStatus


class FrozenKnowledgeContextModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


class KnowledgeReference(FrozenKnowledgeContextModel):
    knowledge_id: str = Field(
        pattern=r"^[A-Z]{2,10}-EKO-[0-9]{4,}$"
    )
    version: str = Field(
        pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$"
    )
    status: KnowledgeStatus


class KnowledgeShadow(FrozenKnowledgeContextModel):
    enabled: bool
    source: Literal["registry"]
    knowledge: tuple[
        KnowledgeReference,
        ...,
    ] = ()
    affects_decision: Literal[False] = False


class KnowledgeContext(FrozenKnowledgeContextModel):
    schema_version: str = Field(
        pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$"
    )
    shadow: KnowledgeShadow
