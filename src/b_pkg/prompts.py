"""Prompt templates for LangChain LLM calls."""
from langchain.prompts import ChatPromptTemplate


CONCEPT_EXTRACTION = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an ontology-guided extractor that identifies candidate concepts, skills, and tools from course texts."
            " Use the Bloom-Structured Prerequisite Graph schema."
            " Return JSON with fields: name, type (Concept/Skill/Tool), short description, and supporting citations from the provided text.",
        ),
        (
            "human",
            "Course segment:\n{context}\n\nList concise candidate nodes with citations and avoid generic terms.",
        ),
    ]
)


BLOOM_CLASSIFICATION = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You classify concepts into Bloom's Taxonomy levels: Remember, Understand, Apply, Analyze, Evaluate, Create."
            " Consider whether the concept is factual knowledge, conceptual understanding, procedural skill, or creative synthesis."
            " Answer with JSON containing name, bloom_level, and a one-sentence rationale.",
        ),
        (
            "human",
            "Concept entry: {concept}\nOptional definition: {definition}\nPrior graph neighbors: {neighbors}",
        ),
    ]
)


PREREQUISITE_SCORING = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You evaluate whether one node is a prerequisite for another."
            " Provide chain-of-thought reasoning about temporal/logical order and return a confidence score in [0,1]."
            " Penalize symmetric 'related to' cases. Use provided evidence only; do not rely on external knowledge.",
        ),
        (
            "human",
            "Source node: {source}\nTarget node: {target}\nEvidence: {evidence}\n"
            "Explain if understanding source is required before target and output JSON: {{\n"
            "  \"reasoning\": <string>,\n  \"confidence\": <0-1 float>\n}}",
        ),
    ]
)
