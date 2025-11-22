from __future__ import annotations

import os
from typing import Dict, Tuple

import networkx as nx

from .models import GraphArtifact

BLOOM_COLORS: Dict[str, str] = {
    "remember": "#5B8FF9",
    "understand": "#61DDAA",
    "apply": "#65789B",
    "analyze": "#F6BD16",
    "evaluate": "#7262FD",
    "create": "#78D3F8",
}

NODE_SHAPES: Dict[str, str] = {
    "concept": "dot",
    "skill": "triangle",
    "topic": "ellipse",
}

DEFAULT_NODE_COLOR = "#D9D9D9"
DEFAULT_EDGE_COLOR = "#6B7280"


def _normalize_confidence(confidence: float | None, *, default: float = 0.5) -> float:
    if confidence is None:
        return default
    return max(0.0, min(1.0, confidence))


def _color_with_alpha(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return hex_color
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha:.2f})"


def graphartifact_to_networkx(artifact: GraphArtifact) -> nx.DiGraph:
    """Map a :class:`GraphArtifact` into a NetworkX directed graph."""

    graph = nx.DiGraph()

    for concept in artifact.concepts:
        graph.add_node(
            concept.id,
            label=concept.label,
            bloom_level=concept.bloom_level,
            type=concept.type,
            confidence=concept.confidence,
            meta=concept.meta,
        )

    for edge in artifact.edges:
        graph.add_edge(
            edge.source,
            edge.target,
            label=edge.label,
            type=edge.type,
            confidence=edge.confidence,
            meta=edge.meta,
        )

    return graph


def _style_node_attributes(attrs: Dict[str, object]) -> Tuple[str, str]:
    bloom_key = str(attrs.get("bloom_level") or "").lower()
    node_type = str(attrs.get("type") or "").lower()
    color = BLOOM_COLORS.get(bloom_key, DEFAULT_NODE_COLOR)
    shape = NODE_SHAPES.get(node_type, "dot")
    return color, shape


def _decorate_graph_for_pyvis(graph: nx.DiGraph) -> nx.DiGraph:
    for node_id, data in graph.nodes(data=True):
        color, shape = _style_node_attributes(data)
        confidence = _normalize_confidence(data.get("confidence"))
        data.update(
            {
                "color": color,
                "shape": shape,
                "size": 15 + 10 * confidence,
                "title": _node_tooltip(data),
            }
        )

    for _u, _v, data in graph.edges(data=True):
        confidence = _normalize_confidence(data.get("confidence"))
        data.update(
            {
                "width": 1 + 4 * confidence,
                "color": _color_with_alpha(DEFAULT_EDGE_COLOR, confidence),
                "title": data.get("label") or "",
                "arrows": "to",
            }
        )

    return graph


def _node_tooltip(data: Dict[str, object]) -> str:
    parts = [f"<b>{data.get('label', data.get('id'))}</b>"]
    if data.get("bloom_level"):
        parts.append(f"Bloom: {data['bloom_level']}")
    if data.get("type"):
        parts.append(f"Type: {data['type']}")
    if data.get("confidence") is not None:
        parts.append(f"Confidence: {data['confidence']:.2f}")
    return "<br />".join(parts)


def render_pyvis(artifact: GraphArtifact, output_path: str) -> str:
    """Render an interactive HTML visualization using pyvis."""

    from pyvis.network import Network

    graph = graphartifact_to_networkx(artifact)
    styled_graph = _decorate_graph_for_pyvis(graph)

    net = Network(height="600px", width="100%", directed=True, notebook=False)
    net.from_nx(styled_graph)
    net.write_html(output_path)
    return output_path


def render_graphviz(artifact: GraphArtifact, output_path: str, *, format: str = "svg") -> str:
    """Render a static diagram using graphviz/dot."""

    import graphviz

    graph = graphartifact_to_networkx(artifact)
    dot = graphviz.Digraph(comment="GraphArtifact", format=format)
    dot.attr(rankdir="LR", nodesep="0.35", ranksep="0.45")

    for node_id, data in graph.nodes(data=True):
        color, shape = _style_node_attributes(data)
        confidence = _normalize_confidence(data.get("confidence"))
        dot.node(
            node_id,
            label=data.get("label", node_id),
            fillcolor=color,
            shape=shape,
            style="filled",
            penwidth=str(1 + 2 * confidence),
        )

    for source, target, data in graph.edges(data=True):
        confidence = _normalize_confidence(data.get("confidence"))
        dot.edge(
            source,
            target,
            label=data.get("label") or "",
            penwidth=str(1 + 2 * confidence),
            color=_color_with_alpha(DEFAULT_EDGE_COLOR, confidence),
            arrowsize=str(0.6 + 0.6 * confidence),
        )

    base, ext = os.path.splitext(output_path)
    filename = base if ext else output_path
    return dot.render(filename=filename, cleanup=True)
