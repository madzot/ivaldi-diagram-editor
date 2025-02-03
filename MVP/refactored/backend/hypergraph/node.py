from __future__ import annotations

from collections import defaultdict
from lib2to3.pgen2.tokenize import group
from queue import Queue
from typing_extensions import Self
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge
from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager


class Node:
    def __init__(self, node_id: int = None, is_special=False):
        if node_id is None:
            node_id = id(self)
        self.id = node_id
        self.inputs: list[HyperEdge] = []
        self.outputs: list[HyperEdge] = []
        self.is_special = is_special  # if it diagram input/output
        self.is_compound = False  # if it is several nodes, for example input/output and wire => two nodes in one, spider and wire.
        self.directly_connected_to: list[Node] = []
        # Should be modified that we can determine how each node connected to another

    def get_source_nodes(self) -> list[Self]:
        visited: set[Node] = set()
        source_nodes: set[Node] = set()
        queue: Queue[Node] = Queue()
        visited.add(self)
        if len(self.get_inputs()) == 0:
            source_nodes.add(self)
        for hyper_edge in self.get_inputs() + self.get_outputs():
            for node in hyper_edge.get_source_nodes() + hyper_edge.get_target_nodes():
                queue.put(node)
        while not queue.empty():
            node: Node = queue.get()
            visited.add(node)
            if len(node.get_inputs()) == 0:
                source_nodes.add(node)
            else:
                for hyper_edge in self.get_inputs() + self.get_outputs():
                    for hyper_edge_node in hyper_edge.get_source_nodes() + hyper_edge.get_target_nodes():
                        if hyper_edge_node not in visited:
                            queue.put(hyper_edge_node)
        return list(source_nodes)

    def get_target_nodes(self) -> list[Self]:
        visited: set[Node] = set()
        target_nodes: list[Node] = list()
        queue: Queue[Node] = Queue()
        visited.add(self)
        if len(self.get_outputs()) == 0:
            target_nodes.append(self)
        for hyper_edge in self.get_inputs() + self.get_outputs():
            for node in hyper_edge.get_source_nodes() + hyper_edge.get_target_nodes():
                queue.put(node)
        while not queue.empty():
            node: Node = queue.get()
            visited.add(node)
            if len(node.get_outputs()) == 0:
                target_nodes.append(node)
            else:
                for hyper_edge in self.get_inputs() + self.get_outputs():
                    for hyper_edge_node in hyper_edge.get_source_nodes() + hyper_edge.get_target_nodes():
                        if hyper_edge_node not in visited:
                            queue.put(hyper_edge_node)
        return target_nodes

    def remove_self(self):
        # TODO check if this method works correctly
        source_nodes: list[Self] = self.get_source_nodes()
        target_nodes: list[Self] = self.get_target_nodes()
        hypergraph: Hypergraph = HypergraphManager.get_graph_by_source_node_id(source_nodes[0].id)
        for connected_to_node in self.directly_connected_to:
            connected_to_node.directly_connected_to.remove(self)
        self.directly_connected_to.clear()
        for input in self.inputs:
            input.remove_target_node_by_reference(self)
        for output in self.outputs:
            output.remove_source_node_by_reference(self)

        # TODO remove hypergraph source node


        connected_nodes: dict[Node, list[Node]] = defaultdict(list)
        for source_node in source_nodes:
            for target_node in target_nodes:
                if source_node.is_connected_to(target_node):
                    connected_nodes[source_node].append(target_node)
                    connected_nodes[target_node].append(source_node)
        connectivity: list[list[Node]] = find_connected_component(connected_nodes)
        for nodes in connectivity:
            new_hypergraph: Hypergraph = Hypergraph(hypergraph.get_canvas_id())
            new_hypergraph.append_source_nodes(nodes[0].get_source_nodes())
            HypergraphManager.add_hypergraph(new_hypergraph)

        self.inputs.clear()
        self.outputs.clear()

    def union(self, other: Self):
        self.directly_connected_to.append(other)
        other.directly_connected_to.append(self)

    def is_connected_to(self, target_node: Self) -> bool:
        if self == target_node: return True
        visited: set[Node] = set()
        queue: Queue[Node] = Queue()
        visited.add(self)
        for hyper_edge in self.get_inputs() + self.get_outputs():
            for node in hyper_edge.get_source_nodes() + hyper_edge.get_target_nodes():
                if node not in visited:
                    queue.put(node)
        while not queue.empty():
            node: Node = queue.get()
            visited.add(node)
            if node == target_node:
                return True
            for hyper_edge in node.get_inputs() + node.get_outputs():
                for hyper_edge_node in hyper_edge.get_source_nodes() + hyper_edge.get_target_nodes():
                    if hyper_edge_node not in visited:
                        queue.put(hyper_edge_node)
        return False

    def append_input(self, input: HyperEdge):
        if input not in self.inputs:
            self.inputs.append(input)

    def append_output(self, output: HyperEdge):
        if output not in self.outputs:
            self.outputs.append(output)

    def set_inputs(self, inputs: list[HyperEdge]):
        self.inputs = inputs

    def get_inputs(self) -> list[HyperEdge]:
        inputs = []
        visited = set()
        queue = Queue()
        visited.add(self.id)
        inputs.extend(self.inputs)
        for other in self.directly_connected_to:
            queue.put(other)

        while not queue.empty():
            node = queue.get()
            if node not in visited:
                visited.add(node)
                inputs.extend(node.inputs)
                for other in node.directly_connected_to:
                    queue.put(other)
        return inputs

    def get_all_directly_connected_to(self) -> list[Self]:
        visited: set = set()
        queue: Queue[Node] = Queue()
        visited.add(self)
        for directly_connected_to_node in self.directly_connected_to:
            queue.put(directly_connected_to_node)
        while not queue.empty():
            node: Node = queue.get()
            visited.add(node)
            for directly_connected_to_node in node.directly_connected_to:
                if directly_connected_to_node not in visited:
                    queue.put(directly_connected_to_node)
        return list(visited)

    def get_outputs(self) -> list[HyperEdge]:
        outputs = []
        visited = set()
        queue = Queue()
        visited.add(self.id)
        outputs.extend(self.outputs)
        for other in self.directly_connected_to:
            queue.put(other)

        while not queue.empty():
            node = queue.get()
            if node not in visited:
                visited.add(node)
                outputs.extend(node.outputs)
                for other in node.directly_connected_to:
                    queue.put(other)
        return outputs

    def remove_input(self, input: HyperEdge):
        if input in self.inputs:
            self.inputs.remove(input)

    def remove_output(self, output: HyperEdge):
        if output in self.outputs:
            self.outputs.remove(output)

    def __eq__(self, __value):
        if type(self) == type(__value):
            if self.id == __value.id:
                return True
            for directly_connected_to in self.get_all_directly_connected_to():
                if directly_connected_to.id == __value.id:
                    return True
        return False

    def __hash__(self):
        return hash(self.id)


def find_connected_component(connected_nodes_map: dict[Node, list[Node]]) -> list[list[Node]]:
    connected_components: list[list[Node]] = list()
    queue: Queue[Node] = Queue()
    visited: set[Node] = set()
    for node, connected_nodes in connected_nodes_map.items():
        connected_component: list[Node] = list()
        if node not in visited:
            connected_component.append(node)
        visited.add(node)
        for connected_node in connected_nodes:
            queue.put(connected_node)
        while not queue.empty():
            connected_node = queue.get()
            if connected_node not in visited:
                connected_component.append(connected_node)
                for connected_node_connected_node in connected_nodes_map[connected_node]:
                    queue.put(connected_node_connected_node)
        connected_components.append(connected_component)
    return connected_components
