from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Concept:
    """A node within the learning graph."""

    id: str
    label: str
    bloom_level: Optional[str] = None
    type: Optional[str] = None
    confidence: Optional[float] = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Edge:
    """A directed relationship between two concepts."""

    source: str
    target: str
    label: Optional[str] = None
    type: Optional[str] = None
    confidence: Optional[float] = None
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphArtifact:
    """A serializable representation of a graph produced by the pipeline."""

    concepts: List[Concept] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphArtifact":
        concept_objs = [Concept(**concept) for concept in data.get("concepts", [])]
        edge_objs = [Edge(**edge) for edge in data.get("edges", [])]
        return cls(concepts=concept_objs, edges=edge_objs)

    @classmethod
    def from_json(cls, json_str: str) -> "GraphArtifact":
        import json

        data = json.loads(json_str)
        return cls.from_dict(data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "concepts": [asdict(concept) for concept in self.concepts],
            "edges": [asdict(edge) for edge in self.edges],
        }

    def to_json(self, *, indent: int = 2) -> str:
        import json

        return json.dumps(self.to_dict(), indent=indent)
