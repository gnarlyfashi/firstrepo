"""LangGraph-compatible node functions for the prerequisite workflow."""
from __future__ import annotations

import json
from typing import Iterable, List

from langchain_core.runnables import Runnable

from ..models import BloomLevel, ConceptNode, EdgeConfidence
from ..prompts import BLOOM_CLASSIFICATION, CONCEPT_EXTRACTION, PREREQUISITE_SCORING
from ..validation import DagValidator, prune_cycles, transitive_reduction
from .graph_state import GraphState


def _decode_json(blob) -> List[dict]:
    if blob is None:
        return []
    if isinstance(blob, list):
        return blob
    if hasattr(blob, "content"):
        blob = blob.content
    if isinstance(blob, str):
        try:
            return json.loads(blob)
        except json.JSONDecodeError:
            return []
    return []


def concept_extraction_node(state: GraphState, llm: Runnable) -> GraphState:
    """Extract candidate concepts/skills/tools from raw text."""
    response = (CONCEPT_EXTRACTION | llm).invoke({"context": state.source_text})
    entries = _decode_json(response)
    for entry in entries:
        try:
            node = ConceptNode(
                name=entry.get("name", ""),
                type=entry.get("type", "Concept"),
                bloom=BloomLevel.REMEMBER,
                description=entry.get("short_description"),
                source_spans=entry.get("citations", []) or entry.get("sources", []),
            )
            state.concepts.append(node)
        except Exception as exc:  # noqa: BLE001
            state.add_warning(f"Failed to parse concept entry {entry}: {exc}")
    state.add_log(f"Extracted {len(entries)} candidate nodes")
    return state


def bloom_classification_node(state: GraphState, llm: Runnable) -> GraphState:
    """Assign Bloom levels to extracted concepts."""
    updated: List[ConceptNode] = []
    for concept in state.concepts:
        payload = {
            "concept": concept.name,
            "definition": concept.description or "",
            "neighbors": [edge.target for edge in state.edges if edge.source == concept.name],
        }
        response = (BLOOM_CLASSIFICATION | llm).invoke(payload)
        data = _decode_json(response)
        entry = data[0] if data else {}
        bloom_value = entry.get("bloom_level", concept.bloom.value if isinstance(concept.bloom, BloomLevel) else concept.bloom)
        try:
            concept.bloom = BloomLevel(bloom_value.lower()) if isinstance(bloom_value, str) else concept.bloom
        except Exception:  # noqa: BLE001
            state.add_warning(f"Could not classify bloom level for {concept.name}; keeping default")
        if rationale := entry.get("rationale"):
            concept.description = concept.description or rationale
        updated.append(concept)
    state.concepts = updated
    state.add_log("Updated Bloom classifications")
    return state


def prerequisite_scoring_node(state: GraphState, llm: Runnable, candidate_pairs: Iterable[tuple[str, str]]) -> GraphState:
    """Score directed prerequisite edges for candidate pairs."""
    count = 0
    for source, target in candidate_pairs:
        count += 1
        evidence = "; ".join(
            [span for concept in state.concepts if concept.name in (source, target) for span in concept.source_spans]
        )
        response = (PREREQUISITE_SCORING | llm).invoke(
            {"source": source, "target": target, "evidence": evidence or "Provided course text."}
        )
        data = _decode_json(response)
        entry = data[0] if data else {}
        confidence = float(entry.get("confidence", 0.0))
        rationale = entry.get("reasoning") or entry.get("rationale")
        state.edges.append(EdgeConfidence(source=source, target=target, confidence=confidence, rationale=rationale))
    state.add_log(f"Scored {count} prerequisite pairs")
    return state


def dag_enforcement_node(state: GraphState) -> GraphState:
    """Enforce DAG constraints with pruning and transitive reduction."""
    original_count = len(state.edges)
    state.edges = prune_cycles(state.edges)
    state.edges = transitive_reduction(state.edges)
    validator = DagValidator(state.edges)
    try:
        ordering = validator.topological_order()
        state.add_log(f"Topological order established with {len(ordering)} nodes")
    except Exception as exc:  # noqa: BLE001
        state.add_warning(f"Topological sort failed: {exc}")
    state.add_log(f"Pruned edges from {original_count} to {len(state.edges)}")
    return state
