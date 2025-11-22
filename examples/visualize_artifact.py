"""Minimal Streamlit app for reviewing serialized graph artifacts."""

from pathlib import Path

import streamlit as st
from pyvis.network import Network

from b_pkg import viz
from b_pkg.models import GraphArtifact


def _load_artifact_from_path(path: Path) -> GraphArtifact:
    content = path.read_text()
    return GraphArtifact.from_json(content)


def _load_artifact_from_upload(upload) -> GraphArtifact:
    return GraphArtifact.from_json(upload.read().decode("utf-8"))


def _build_html(artifact: GraphArtifact) -> str:
    graph = viz.graphartifact_to_networkx(artifact)
    styled = viz._decorate_graph_for_pyvis(graph)

    net = Network(height="650px", width="100%", directed=True)
    net.from_nx(styled)
    return net.generate_html(notebook=False, full=True)


def _default_artifact() -> GraphArtifact:
    return GraphArtifact.from_dict(
        {
            "concepts": [
                {"id": "c1", "label": "Variables", "bloom_level": "remember", "type": "concept", "confidence": 0.9},
                {"id": "c2", "label": "Loops", "bloom_level": "understand", "type": "concept", "confidence": 0.72},
                {"id": "c3", "label": "Iteration Examples", "bloom_level": "apply", "type": "skill", "confidence": 0.64},
            ],
            "edges": [
                {"source": "c1", "target": "c2", "label": "prerequisite", "confidence": 0.8},
                {"source": "c2", "target": "c3", "label": "supports", "confidence": 0.7},
            ],
        }
    )


def main() -> None:
    st.set_page_config(page_title="GraphArtifact Viewer", layout="wide")
    st.title("GraphArtifact Viewer")
    st.caption("Load a serialized GraphArtifact JSON file to inspect the generated knowledge graph.")

    with st.sidebar:
        st.header("Load artifact")
        uploaded = st.file_uploader("Upload GraphArtifact JSON", type=["json"])
        sample_toggle = st.checkbox("Use sample artifact", value=True)
        file_path = st.text_input("Artifact path (optional)", "")

    artifact: GraphArtifact | None = None
    if uploaded is not None:
        artifact = _load_artifact_from_upload(uploaded)
    elif file_path:
        artifact = _load_artifact_from_path(Path(file_path))
    elif sample_toggle:
        artifact = _default_artifact()

    if artifact is None:
        st.info("Provide an artifact via upload or path to get started.")
        return

    st.subheader("Artifact details")
    col1, col2 = st.columns(2)
    col1.metric("Concepts", len(artifact.concepts))
    col2.metric("Edges", len(artifact.edges))

    html = _build_html(artifact)
    st.components.v1.html(html, height=700, scrolling=True)


if __name__ == "__main__":
    main()
