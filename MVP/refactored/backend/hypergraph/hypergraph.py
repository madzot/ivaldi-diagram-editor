from __future__ import annotations

from queue import Queue
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge

from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge

if TYPE_CHECKING:
    from MVP.refactored.backend.hypergraph.node import Node


class Hypergraph(HyperEdge):
    """Hypergraph class."""

    def __init__(self, hypergraph_id=None, canvas_id=None):
        super().__init__(hypergraph_id)
        self.canvas_id = canvas_id
        self.hypergraph_source: list[Node] = []
        self.nodes: dict[int, Node] = {}
        self.edges: dict[int, HyperEdge] = {}

    def get_all_hyper_edges(self) -> set:
        return set(self.edges.values())

    def get_all_nodes(self) -> set[Node]:
        return set(self.nodes.values())

    def get_hypergraph_source(self) -> list[Node]:
        return self.hypergraph_source

    def remove_node(self, node_to_remove_id: int):
        self.nodes[node_to_remove_id].remove_self()
        self.nodes.pop(node_to_remove_id)

    def contains_node(self, node: Node) -> bool:
        return node in self.nodes.values()

    def add_hypergraph_source(self, node: Node):
        self.hypergraph_source.append(node)

    def add_hypergraph_sources(self, nodes: list[Node]):
        self.hypergraph_source.extend(nodes)

    def set_hypergraph_sources(self, nodes: list[Node]):
        self.hypergraph_source = nodes

    def get_node_by_input(self, input_id: int) -> HyperEdge | None:
        # TODO rewrite, input now is wire id => Node id, and Node is hyperedge
        return None

    def get_node_by_output(self, output_id: int) -> HyperEdge | None:
        # TODO rewrite, output now is wire id => Node id, and Node is hyperedge
        return None

    def get_canvas_id(self) -> int:
        return self.canvas_id

    def set_canvas_id(self, canvas_id: int) -> None:
        self.canvas_id = canvas_id

    def _is_valid(self) -> bool:
        # TODO
        return True

    def to_dict(self) -> dict:
        """Return a dictionary representation of the hypergraph."""
        hypergraph_dict = super().to_dict()
        hypergraph_dict["nodes"] = [node.to_dict() for node in self.nodes]
        return hypergraph_dict

    def __str__(self) -> str:
        result = f"Hypergraph: {self.id}\n"

        hyper_edges = self.get_all_hyper_edges()
        result += f"Hyper edges({len(hyper_edges)}): " + ", ".join(
            str(hyper_edge.id) for hyper_edge in hyper_edges) + "\n"

        vertices = self.get_all_nodes()
        result += f"Vertices({len(vertices)}): " + ", ".join(
            f"{vertex.id}({len(vertex.get_all_directly_connected_to())})" for vertex in vertices) + "\n"

        result += "Connections:\n"
        visited = set()
        for vertex in vertices:
            if vertex not in visited:
                visited.add(vertex)
                for node in vertex.get_all_directly_connected_to():
                    visited.add(node)
                inputs = f"|" + "|".join(f"{hyper_edge}" for hyper_edge in vertex.get_inputs())
                outputs = f"|" + "|".join(f"{hyper_edge}" for hyper_edge in vertex.get_outputs())
                result += f"{inputs}<-{vertex.id}->{outputs}\n"

        return result

    def __eq__(self, other):
        if not isinstance(other, Hypergraph):
            return False
        return other.id == self.id

    def __hash__(self):
        return super().__hash__()
3