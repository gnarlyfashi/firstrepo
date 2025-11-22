"""Pydantic models for B-PKG artifacts."""
from enum import Enum
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field, validator


class BloomLevel(str, Enum):
    """Bloom's taxonomy levels with a coarse grouping."""

    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"

    @property
    def rank(self) -> int:
        order = [
            BloomLevel.REMEMBER,
            BloomLevel.UNDERSTAND,
            BloomLevel.APPLY,
            BloomLevel.ANALYZE,
            BloomLevel.EVALUATE,
            BloomLevel.CREATE,
        ]
        return order.index(self)


class ConceptNode(BaseModel):
    """A node in the prerequisite graph."""

    name: str = Field(..., description="Human-readable concept or skill name")
    type: str = Field(..., description="Concept, Skill, or Tool as defined by ontology")
    bloom: BloomLevel
    description: Optional[str] = Field(None, description="Optional summary or definition")
    source_spans: List[str] = Field(
        default_factory=list,
        description="Supporting snippets or citations grounding the node",
    )

    @validator("name")
    def normalize_name(cls, value: str) -> str:  # noqa: N805
        normalized = value.strip()
        if not normalized:
            raise ValueError("concept name cannot be empty")
        return normalized


class EdgeConfidence(BaseModel):
    """Directed prerequisite relation with a confidence score."""

    source: str = Field(..., description="Prerequisite concept name")
    target: str = Field(..., description="Dependent concept name")
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Model probability that source is a prerequisite for target",
    )
    rationale: Optional[str] = Field(
        None, description="Chain-of-thought reasoning or justification"
    )

    @property
    def edge(self) -> Tuple[str, str]:
        return (self.source, self.target)


class GraphArtifact(BaseModel):
    """Container capturing the evolving graph and metadata."""

    concepts: List[ConceptNode]
    edges: List[EdgeConfidence]
    warnings: List[str] = Field(default_factory=list)
