from __future__ import annotations

from queue import Queue
from typing import Self
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge

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

    def get_hypergraph_source_nodes(self) -> list[Self]:
        visited: set[Node] = set()
        source_nodes: set[Node] = set()
        queue: Queue[Node] = Queue()
        visited.add(self)
        if len(self.get_input_hyper_edges()) == 0:
            source_nodes.add(self)
        for hyper_edge in self.get_input_hyper_edges() + self.get_output_hyper_edges():
            for node in hyper_edge.get_source_nodes() + hyper_edge.get_target_nodes():
                queue.put(node)
        while not queue.empty():
            node: Node = queue.get()
            visited.add(node)
            if len(node.get_input_hyper_edges()) == 0:
                source_nodes.add(node)
            else:
                for hyper_edge in self.get_input_hyper_edges() + self.get_output_hyper_edges():
                    for hyper_edge_node in hyper_edge.get_source_nodes() + hyper_edge.get_target_nodes():
                        if hyper_edge_node not in visited:
                            queue.put(hyper_edge_node)
        return list(source_nodes)

    def get_hypergraph_target_nodes(self) -> list[Self]:
        visited: set[Node] = set()
        target_nodes: list[Node] = list()
        queue: Queue[Node] = Queue()
        visited.add(self)
        if len(self.get_output_hyper_edges()) == 0:
            target_nodes.append(self)
        for hyper_edge in self.get_input_hyper_edges() + self.get_output_hyper_edges():
            for node in hyper_edge.get_source_nodes() + hyper_edge.get_target_nodes():
                queue.put(node)
        while not queue.empty():
            node: Node = queue.get()
            visited.add(node)
            if len(node.get_output_hyper_edges()) == 0:
                target_nodes.append(node)
            else:
                for hyper_edge in self.get_input_hyper_edges() + self.get_output_hyper_edges():
                    for hyper_edge_node in hyper_edge.get_source_nodes() + hyper_edge.get_target_nodes():
                        if hyper_edge_node not in visited:
                            queue.put(hyper_edge_node)
        return target_nodes

    def get_children_nodes(self) -> list[Self]:
        children_nodes: set[Node] = set()
        for output_hyper_edge in self.get_output_hyper_edges():
            for node in output_hyper_edge.get_target_nodes():
                children_nodes.add(node)
                for directly_connected_to in node.get_united_with_nodes():
                    children_nodes.add(directly_connected_to)
        return list(children_nodes)

    def get_parent_nodes(self) -> list[Self]:
        parent_nodes: set[Node] = set()
        for input_hyper_edge in self.get_input_hyper_edges():
            for node in input_hyper_edge.get_source_nodes():
                parent_nodes.add(node)
                for directly_connected_to in node.get_united_with_nodes():
                    parent_nodes.add(directly_connected_to)
        return list(parent_nodes)

    def remove_self(self):
        for connected_to_node in self.directly_connected_to:
            connected_to_node.directly_connected_to.remove(self)
        self.directly_connected_to.clear()
        for input in self.inputs:
            input.remove_target_node_by_reference(self)
        for output in self.outputs:
            output.remove_source_node_by_reference(self)

        self.inputs.clear()
        self.outputs.clear()

    def union(self, other: Self):
        self.directly_connected_to.append(other)
        other.directly_connected_to.append(self)

    def is_connected_to(self, target_node: Self) -> bool:
        if self == target_node:
            return True
        visited: set[Node] = set()
        queue: Queue[Node] = Queue()
        visited.add(self)
        for hyper_edge in self.get_input_hyper_edges() + self.get_output_hyper_edges():
            for node in hyper_edge.get_source_nodes() + hyper_edge.get_target_nodes():
                if node not in visited:
                    queue.put(node)
        while not queue.empty():
            node: Node = queue.get()
            visited.add(node)
            if node == target_node:
                return True
            for hyper_edge in node.get_input_hyper_edges() + node.get_output_hyper_edges():
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

    def get_input_hyper_edges(self) -> list[HyperEdge]:
        inputs = []
        visited = set()
        queue = Queue()
        visited.add(self)
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

    def get_united_with_nodes(self) -> list[Node]:
        united_with_nodes: set[Node] = set()
        visited: set = set()
        queue: Queue[Node] = Queue()
        visited.add(self)
        for directly_connected_to_node in self.directly_connected_to:
            queue.put(directly_connected_to_node)
        while not queue.empty():
            node: Node = queue.get()
            if node not in visited:
                united_with_nodes.add(node)
            visited.add(node)
            for directly_connected_to_node in node.directly_connected_to:
                if directly_connected_to_node not in visited:
                    queue.put(directly_connected_to_node)
        return list(united_with_nodes)

    def get_directly_connected_to(self) -> list[Node]:
        return self.directly_connected_to

    def get_output_hyper_edges(self) -> list[HyperEdge]:
        outputs: set[HyperEdge] = set()
        visited = set()
        queue = Queue()
        visited.add(self)
        outputs.update(self.outputs)
        for other in self.directly_connected_to:
            queue.put(other)

        while not queue.empty():
            node = queue.get()
            if node not in visited:
                visited.add(node)
                outputs.update(node.outputs)
                for other in node.directly_connected_to:
                    queue.put(other)
        return list(outputs)

    def get_node_children(self) -> list[Node]:
        children: set[Node] = set()
        for hyper_edge in self.get_output_hyper_edges():
            for target_node in hyper_edge.get_target_nodes():
                children.add(target_node)
                children.union(target_node.get_united_with_nodes())
        return list(children)

    def remove_input(self, input: HyperEdge):
        if input in self.inputs:
            self.inputs.remove(input)

    def remove_output(self, output: HyperEdge):
        if output in self.outputs:
            self.outputs.remove(output)

    def to_dict(self) -> dict:
        """Return a dictionary representation of the node."""
        # return {
        #     "id": self.id,
        #     "inputs": [node_input.to_dict() for node_input in self.inputs],
        #     "outputs": [node_output.to_dict() for node_output in self.outputs],
        # } # TODO: change this to directly connected nodes

    def __eq__(self, __value):
        if type(self) == type(__value):
            if self.id == __value.id:
                return True
            for directly_connected_to in self.get_united_with_nodes():
                if directly_connected_to.id == __value.id:
                    return True
        return False

    def __hash__(self):
        return hash(self.id)
