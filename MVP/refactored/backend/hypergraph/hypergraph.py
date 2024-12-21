from __future__ import annotations

from queue import Queue
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge

from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge

import networkx as nx
import matplotlib.pyplot as plt

from MVP.refactored.backend.hypergraph.node import Node


class Hypergraph(HyperEdge):
    """Hypergraph class."""

    def __init__(self, hypergraph_id=None, canvas_id=None):
        super().__init__(hypergraph_id)
        self.canvas_id = canvas_id
        self.hypergraph_source: list[Node] = []

    def get_all_hyper_edges(self) -> set:
        visited: set[HyperEdge] = set()
        all_hyper_edges: set[HyperEdge] = set()

        queue = Queue()
        for source_node in self.hypergraph_source:
            for output in source_node.get_outputs():
                queue.put(output)

        while not queue.empty():
            hyper_edge: HyperEdge = queue.get()
            visited.add(hyper_edge)
            all_hyper_edges.add(hyper_edge)
            for output in [node_hyper_edge for node in hyper_edge.get_target_nodes() for node_hyper_edge in node.get_outputs()]:
                if output not in visited:
                    queue.put(output)
        return all_hyper_edges

    def get_all_nodes(self) -> set[Node]:
        visited: set[Node] = set()
        all_nodes: set[Node] = set()

        queue = Queue()
        for source_node in self.hypergraph_source:
            queue.put(source_node)
            for node in source_node.get_all_directly_connected_to():
                queue.put(node)

        while not queue.empty():
            node: Node = queue.get()
            visited.add(node)
            all_nodes.add(node)
            for next_node in [(hyper_edge.get_target_nodes() + hyper_edge.get_source_nodes())
                              for hyper_edge in (node.get_outputs() + node.get_outputs())]:
                if next_node not in visited:
                    queue.put(next_node)
        return all_nodes

    def get_hypergraph_source(self) -> list[Node]:
        return self.hypergraph_source

    def remove_node(self, node_to_remove_id: int):
        visited = set()

        queue = Queue()
        for source_node in self.hypergraph_source:
            if source_node == node_to_remove_id:
                source_node._remove_self()
                self.hypergraph_source.remove(source_node)
                return
            queue.put(source_node)

        while not queue.empty():
            node = queue.get()
            if node.id == node_to_remove_id:
                node._remove_self()
                break
            visited.add(node)
            for child in node.children:
                if child not in visited:
                    queue.put(child)

    def contains_node(self, node: Node) -> bool:
        return node in self.nodes

    def add_hypergraph_source(self, node: Node):
        self.hypergraph_source.append(node)

    def set_hypergraph_sources(self, nodes: list[Node]):
        self.hypergraph_source = nodes

    def add_node(self, node: HyperEdge) -> None:
        if node in self.nodes:
            raise ValueError("Node already exists")
        self.nodes.append(node)
        self.set_hypergraph_io()

    def get_node_by_input(self, input_id: int) -> HyperEdge | None:
        for node in self.nodes:
            if input_id in node.inputs:
                return node
        return None

    def get_node_by_output(self, output_id: int) -> HyperEdge | None:
        for node in self.nodes:
            if output_id in node.outputs:
                return node
        return None

    def get_node_children_by_id(self, node_id: int) -> list[HyperEdge]:
        return self.get_node_children_by_node(self.get_node_by_id(node_id))

    def get_node_children_by_node(self, required_node: HyperEdge) -> list[HyperEdge]:
        children = []
        for node in self.nodes:
            if any(n in node.inputs for n in required_node.outputs): # If requiredNode outputs wire id contains another node inputs wire id
                children.append(node)
        return children

    def get_canvas_id(self) -> int:
        return self.canvas_id

    def set_canvas_id(self, canvas_id: int) -> None:
        self.canvas_id = canvas_id

    def get_node_parents_by_id(self, node_id: int) -> list[HyperEdge]:
        return self.get_node_parents_by_node(self.get_node_by_id(node_id))

    def get_node_parents_by_node(self, required_node: HyperEdge) -> list[HyperEdge]:
        parents = []
        for node in self.nodes:
            if any(n in node.outputs for n in required_node.inputs):  # If requiredNode outputs wire id contains another node inputs wire id
                parents.append(node)
        return parents

    def _is_valid(self) -> bool:
        """Validate hypergraph structure by checking input/output consistency and cycles."""
        if not self.inputs or not self.outputs or not self.nodes:
            print("Inputs, outputs, or nodes are empty")
            return False

        node_inputs = set()
        node_outputs = set()

        for node in self.nodes:
            if not node._is_valid():
                print(f"Node {node.id} is not valid")
                return False

            node_inputs.update(node.inputs)
            node_outputs.update(node.outputs)

        # Check if all node inputs are either in hypergraph inputs or match any node's outputs
        invalid_inputs = node_inputs - set(self.inputs) - node_outputs
        if invalid_inputs:
            print(f"Invalid inputs: {invalid_inputs}")
            return False

        # Check if all node outputs are either in hypergraph outputs or match any node's inputs
        invalid_outputs = node_outputs - set(self.outputs) - node_inputs
        if invalid_outputs:
            print(f"Invalid outputs: {invalid_outputs}")
            return False

        if not self.is_connected():
            print("Hypergraph is not connected")
            return False

        has_no_cycles = self.has_no_cycles()
        if not has_no_cycles:
            print("Hypergraph has cycles")
            return False

        return True

    def is_connected(self) -> bool:
        """Check if the hypergraph is connected by verifying all nodes are reachable from an arbitrary starting node."""
        visited = set()
        self.explore_connected(self.nodes[0], visited)

        return len(visited) == len(self.nodes)

    def explore_connected(self, node, visited):
        """Helper function to perform DFS for connectivity check."""
        if node in visited:
            return
        visited.add(node)

        for node_output in node.outputs:
            for other_node in self.nodes:
                if node_output in other_node.inputs and other_node not in visited:
                    self.explore_connected(other_node, visited)

        for node_input in node.inputs:
            for other_node in self.nodes:
                if node_input in other_node.outputs and other_node not in visited:
                    self.explore_connected(other_node, visited)

    def has_no_cycles(self) -> bool:
        """Check if the hypergraph has no cycles."""
        explored_nodes = set()
        current_path = set()

        for current_node in self.nodes:
            if current_node not in explored_nodes:
                if not self.depth_first_search(current_node, explored_nodes, current_path):
                    return False
        return True

    def depth_first_search(self, node, visited, current_path) -> bool:
        """Helper function to check if the hypergraph has no cycles, using depth first search."""
        if node in current_path:
            return False
        if node in visited:
            return True

        visited.add(node)
        current_path.add(node)

        for output in node.outputs:
            for other_node in self.nodes:
                if output in other_node.inputs:
                    if not self.depth_first_search(other_node, visited, current_path):
                        return False

        current_path.remove(node)
        return True

    def to_dict(self) -> dict:
        """Return a dictionary representation of the hypergraph."""
        hypergraph_dict = super().to_dict()
        hypergraph_dict["nodes"] = [node.to_dict() for node in self.nodes]
        return hypergraph_dict

    def visualize(self):
        """Visualize the hypergraph using matplotlib and networkx, returning the figure."""
        g = nx.DiGraph()
        for node in self.nodes:
            g.add_node(node.id, label="N_" + str(node.id)[-6:])
            for output in node.outputs:
                for other_node in self.nodes:
                    if output in other_node.inputs:
                        g.add_edge(node.id, other_node.id, label=str(output)[-6:])

        start_node_id = "input"
        g.add_node(start_node_id)
        for input_wire in self.inputs:
            for node in self.nodes:
                if input_wire in node.inputs:
                    g.add_edge(start_node_id, node.id, label=str(input_wire)[-6:])

        end_node_id = "output"
        g.add_node(end_node_id)
        for output_wire in self.outputs:
            for node in self.nodes:
                if output_wire in node.outputs:
                    g.add_edge(node.id, end_node_id, label=str(output_wire)[-6:])

        fig, ax = plt.subplots(figsize=(10, 5))
        pos = nx.spring_layout(g)

        nx.draw_networkx_nodes(g, pos, ax=ax, nodelist=[node.id for node in self.nodes],
                               node_size=700, node_color='lightblue', alpha=0.8)
        nx.draw_networkx_edges(g, pos, ax=ax, arrowstyle="->", arrowsize=20, edge_color="black")
        edge_labels = {(u, v): d['label'] for u, v, d in g.edges(data=True)}
        nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels, ax=ax)
        nx.draw_networkx_labels(g, pos, labels={n: g.nodes[n].get('label', n) for n in g.nodes()}, ax=ax)

        ax.set_title(f"Hypergraph ID: {self.id}")
        ax.axis('off')

        return fig

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



