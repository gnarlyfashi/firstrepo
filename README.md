# Bloom-Structured Prerequisite Graph (B-PKG)

A LangChain + LangGraph scaffold for automating Bloom-structured prerequisite
knowledge graphs. The framework extracts candidate concepts, classifies them
into Bloom levels, scores prerequisite directionality, and enforces DAG
integrity with pruning and transitive reduction.

## Features
- Pydantic models for concepts, Bloom levels, and confidence-weighted edges
- Prompt templates for ontology-guided concept extraction, Bloom classification,
  and prerequisite scoring
- LangGraph pipeline that chains extraction → classification → scoring → DAG
  enforcement
- Utilities for cycle pruning, transitive reduction, and topological validation

## Quickstart
1. Install dependencies (Python 3.11+):
   ```bash
   pip install -e .
   ```
2. Create a LangChain-compatible chat model (e.g., `ChatOpenAI`) and build the
   workflow:
   ```python
   from langchain_openai import ChatOpenAI
   from b_pkg.pipeline.workflow import build_workflow, run_pipeline

   llm = ChatOpenAI(model="gpt-4o-mini")
   workflow = build_workflow(llm)
   artifact = run_pipeline(workflow, "Intro to calculus course description...")
   print(artifact)
   ```

## Repository layout
- `src/b_pkg/models.py` – schema for nodes and edges
- `src/b_pkg/prompts.py` – LangChain prompt templates
- `src/b_pkg/validation.py` – DAG validation, cycle pruning, transitive reduction
- `src/b_pkg/pipeline/` – LangGraph state, nodes, and workflow assembly

## Status
Initial scaffolding and utilities are in place; LLM configuration and retrieval
wiring can be extended per deployment.
