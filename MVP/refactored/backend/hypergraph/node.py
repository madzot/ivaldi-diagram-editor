from __future__ import annotations

from importlib import import_module
from os import remove

from MVP.refactored.backend.box_functions.box_function import BoxFunction


class Node:

    def __init__(self, node_id=None, inputs=None, outputs=None, box_function: BoxFunction = None):
        if node_id is None:
            node_id = id(self)
        if inputs is None:
            inputs = []
        if outputs is None:
            outputs = []
        self.id = node_id
        self.inputs = inputs
        self.outputs = outputs
        # key is node, value is number of edges between self node and parent node
        self._parent_nodes: dict[Node, int] = dict()
        # same here
        self._children_nodes: dict[Node, int] = dict()
        # if box_function is null it can be input/output in diagram or user didn`t specified box function
        self.box_function: BoxFunction|None = box_function

    def _get_children(self):
        module = import_module("MVP.refactored.backend.hypergraph.hypergraph_manager")
        HypergraphManager = getattr(module, "HypergraphManager")
        hypergraph = HypergraphManager.get_graph_by_node_id(self.id)
        return hypergraph.get_node_children_by_node(self)

    def _get_parents(self):
        module = import_module("MVP.refactored.backend.hypergraph.hypergraph_manager")
        HypergraphManager = getattr(module, "HypergraphManager")
        hypergraph = HypergraphManager.get_graph_by_node_id(self.id)
        return hypergraph.get_node_parents_by_node(self)

    def get_children(self) -> list:
        return list(self._children_nodes.keys())

    def get_parents(self) -> set:
        return set(self._parent_nodes.keys())

    def is_node_child(self, child: Node) -> bool:
        return child in self._children_nodes

    def is_node_parent(self, parent: Node) -> bool:
        return parent in self._parent_nodes

    def get_child_by_id(self, child_id: int) -> Node | None:
        for child in self._children_nodes.keys():
            if child.id == child_id:
                return child
        return None

    def get_parent_by_id(self, parent_id: int) -> Node | None:
        for parent in self._parent_nodes.keys():
            if parent.id == parent_id:
                return parent
        return None

    def add_child(self, child: Node, edge_count=1):
        if child in self._children_nodes:
            self._children_nodes[child] += edge_count
            child._parent_nodes[self] += edge_count
        else:
            self._children_nodes[child] = edge_count
            child._parent_nodes[self] = edge_count

    def add_parent(self, parent: Node, edge_count=1):
        if parent in self._parent_nodes:
            self._parent_nodes[parent] += edge_count
            parent._children_nodes[self] += edge_count
        else:
            self._parent_nodes[parent] = edge_count
            parent._children_nodes[self] = edge_count


    def remove_child(self, child_to_remove: Node):
        if child_to_remove in self._children_nodes:
            del self._children_nodes[child_to_remove]
            child_to_remove.remove_parent(self)

    def remove_parent(self, parent_to_remove: Node):
        if parent_to_remove in self._parent_nodes:
            del self._parent_nodes[parent_to_remove]
            parent_to_remove.remove_child(self)

    def remove_self(self):
        for parent in self._parent_nodes.keys():
            parent.remove_child(self)
        for child in self._children_nodes.keys():
            child.remove_parent(self)
        self._parent_nodes.clear()
        self._children_nodes.clear()

    def remove_parent_edges(self, parent_to_remove: Node, edge_count=1):
        if parent_to_remove in self._parent_nodes:
            edge_count_with_parent = self._parent_nodes[parent_to_remove]
            edge_count_with_parent -= edge_count
            if edge_count_with_parent > 0:
                self._parent_nodes[parent_to_remove] = edge_count_with_parent
            else:
                self.remove_parent(parent_to_remove)

    def remove_child_edges(self, child_to_remove: Node, edge_count=1):
        if child_to_remove in self._children_nodes:
            edge_count_with_child = self._children_nodes[child_to_remove]
            edge_count_with_child -= edge_count
            if edge_count_with_child > 0:
                self._children_nodes[child_to_remove] = edge_count_with_child
            else:
                self.remove_child(child_to_remove)

    def set_box_function(self, function: BoxFunction):
        self.box_function = function

    def get_box_function(self) -> BoxFunction:
        return self.box_function

    def add_input(self, input_id: int) -> None:
        if input_id in self.inputs or input_id in self.outputs:
            raise ValueError("Input already exists")

        self.inputs.append(input_id)

    def remove_input(self, input_id: int) -> None:
        self.inputs.remove(input_id)

    def add_output(self, output_id: int) -> None:
        if output_id in self.inputs or output_id in self.outputs:
            raise ValueError("Output already exists")

        self.outputs.append(output_id)

    def remove_output(self, output_id: int) -> None:
        self.outputs.remove(output_id)

    def _is_valid(self) -> bool:
        return len(self.inputs) > 0 and len(self.outputs) > 0

    def is_valid(self) -> bool:
        return self._children_nodes or self._parent_nodes

    def has_input(self, input_id) -> bool:
        return input_id in self.inputs

    def has_output(self, output_id) -> bool:
        return output_id in self.outputs

    def to_dict(self) -> dict:
        """Return a dictionary representation of the node."""
        return {
            "id": self.id,
            "inputs": self.inputs,
            "outputs": self.outputs,
        }

    def __str__(self) -> str:
        """Return a string representation of the node."""
        return (f"Node ID: {self.id}\n"
                f"Inputs: {self.inputs}\n"
                f"Outputs: {self.outputs}")

    def __eq__(self, other):
        if not isinstance(other, Node):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)


def test_node_str():
    # Create sample nodes
    node1 = Node(node_id=0, inputs=[0], outputs=[1, 2])
    print(str(node1))
