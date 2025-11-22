"""Graph validation and pruning utilities."""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Iterable, List, Set, Tuple

from .models import EdgeConfidence


class CycleDetectedError(ValueError):
    """Raised when a cycle is found in the prerequisite graph."""


class DagValidator:
    """Utility class to reason about DAG constraints."""

    def __init__(self, edges: Iterable[EdgeConfidence]):
        self.edges = list(edges)
        self.graph = self._build_adjacency(self.edges)

    @staticmethod
    def _build_adjacency(edges: Iterable[EdgeConfidence]) -> dict[str, Set[str]]:
        adjacency: dict[str, Set[str]] = defaultdict(set)
        for edge in edges:
            adjacency[edge.source].add(edge.target)
        return adjacency

    def detect_cycle(self) -> List[Tuple[str, str]]:
        """Return a cycle if one exists using DFS; otherwise empty list."""
        visited: Set[str] = set()
        stack: Set[str] = set()
        parent: dict[str, str] = {}

        def dfs(node: str) -> List[Tuple[str, str]]:
            visited.add(node)
            stack.add(node)
            for neighbor in self.graph.get(node, set()):
                if neighbor not in visited:
                    parent[neighbor] = node
                    cycle = dfs(neighbor)
                    if cycle:
                        return cycle
                elif neighbor in stack:
                    # reconstruct cycle path
                    path = [(node, neighbor)]
                    cur = node
                    while cur != neighbor:
                        prev = parent.get(cur)
                        if prev is None:
                            break
                        path.append((prev, cur))
                        cur = prev
                    return list(reversed(path))
            stack.remove(node)
            return []

        for node in self.graph:
            if node not in visited:
                cycle = dfs(node)
                if cycle:
                    return cycle
        return []

    def topological_order(self) -> List[str]:
        """Return a topological ordering or raise CycleDetectedError."""
        indegree: dict[str, int] = defaultdict(int)
        for src, targets in self.graph.items():
            for tgt in targets:
                indegree[tgt] += 1
            indegree.setdefault(src, 0)

        queue = deque([node for node, deg in indegree.items() if deg == 0])
        ordering: List[str] = []

        while queue:
            node = queue.popleft()
            ordering.append(node)
            for neighbor in self.graph.get(node, set()):
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)

        if len(ordering) != len(indegree):
            raise CycleDetectedError("Graph contains a cycle; topological sort failed")
        return ordering


def prune_cycles(edges: List[EdgeConfidence]) -> List[EdgeConfidence]:
    """Remove the lowest-confidence edge from each detected cycle until DAG."""
    mutable_edges = list(edges)
    while True:
        validator = DagValidator(mutable_edges)
        cycle = validator.detect_cycle()
        if not cycle:
            return mutable_edges

        cycle_edges = {(src, tgt) for src, tgt in cycle}
        candidates = [edge for edge in mutable_edges if edge.edge in cycle_edges]
        if not candidates:
            break
        weakest = min(candidates, key=lambda e: e.confidence)
        mutable_edges.remove(weakest)

    return mutable_edges


def transitive_reduction(edges: List[EdgeConfidence]) -> List[EdgeConfidence]:
    """Remove edges implied by transitive closure to simplify the DAG."""
    adjacency: dict[str, Set[str]] = defaultdict(set)
    for edge in edges:
        adjacency[edge.source].add(edge.target)

    def reachable(start: str, target: str) -> bool:
        stack = list(adjacency[start])
        seen: Set[str] = set()
        while stack:
            node = stack.pop()
            if node == target:
                return True
            if node in seen:
                continue
            seen.add(node)
            stack.extend(adjacency.get(node, set()))
        return False

    pruned: List[EdgeConfidence] = []
    for edge in edges:
        adjacency[edge.source].remove(edge.target)
        if reachable(edge.source, edge.target):
            adjacency[edge.source].add(edge.target)
            continue
        adjacency[edge.source].add(edge.target)
        pruned.append(edge)
    return pruned
