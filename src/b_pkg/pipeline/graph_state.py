"""State container used across LangGraph workflow."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from ..models import ConceptNode, EdgeConfidence, GraphArtifact


@dataclass
class GraphState:
    """Mutable state threaded through LangGraph nodes."""

    source_text: str
    concepts: List[ConceptNode] = field(default_factory=list)
    edges: List[EdgeConfidence] = field(default_factory=list)
    log: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_artifact(self) -> GraphArtifact:
        return GraphArtifact(concepts=self.concepts, edges=self.edges, warnings=self.warnings)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_log(self, message: str) -> None:
        self.log.append(message)

    @property
    def summary(self) -> str:
        return f"concepts={len(self.concepts)}, edges={len(self.edges)}, warnings={len(self.warnings)}"
