"""LangGraph workflow assembly for B-PKG generation."""
from __future__ import annotations

from typing import Callable, Iterable

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from ..models import GraphArtifact
from .graph_state import GraphState
from .nodes import (
    bloom_classification_node,
    concept_extraction_node,
    dag_enforcement_node,
    prerequisite_scoring_node,
)


def default_candidate_pairs(state: GraphState) -> Iterable[tuple[str, str]]:
    """Generate naive candidate pairs by linking every pair once."""
    names = [concept.name for concept in state.concepts]
    for i, source in enumerate(names):
        for target in names[i + 1 :]:
            yield (source, target)


def build_workflow(
    llm,
    *,
    candidate_pairs: Callable[[GraphState], Iterable[tuple[str, str]]] = default_candidate_pairs,
) -> CompiledStateGraph:
    """Create a compiled LangGraph pipeline for prerequisite generation."""
    graph = StateGraph(GraphState)

    graph.add_node("extract_concepts", lambda state: concept_extraction_node(state, llm))
    graph.add_node("classify_bloom", lambda state: bloom_classification_node(state, llm))

    def score_edges(state: GraphState) -> GraphState:
        pairs = list(candidate_pairs(state))
        return prerequisite_scoring_node(state, llm, pairs)

    graph.add_node("score_edges", score_edges)
    graph.add_node("enforce_dag", dag_enforcement_node)

    graph.set_entry_point("extract_concepts")
    graph.add_edge("extract_concepts", "classify_bloom")
    graph.add_edge("classify_bloom", "score_edges")
    graph.add_edge("score_edges", "enforce_dag")
    graph.add_edge("enforce_dag", END)

    return graph.compile()


def run_pipeline(compiled: CompiledStateGraph, source_text: str) -> GraphArtifact:
    """Execute the compiled workflow and return a GraphArtifact."""
    initial = GraphState(source_text=source_text)
    final_state: GraphState = compiled.invoke(initial)
    return final_state.to_artifact()
