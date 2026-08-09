from __future__ import annotations

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class EngineMetadata(BaseModel):
    """
    Immutable metadata describing an engine.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    name: str = Field(
        min_length=1,
    )

    version: str = Field(
        min_length=1,
    )

    description: str = Field(
        min_length=1,
    )

    category: str = Field(
        min_length=1,
    )

    experimental: bool = False

    author: str | None = None

    tags: tuple[str, ...] = ()