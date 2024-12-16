from __future__ import annotations

from typing import TYPE_CHECKING

from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.connection import Connection

if TYPE_CHECKING:
    from MVP.refactored.backend.hypergraph.node import Node

class HyperEdge:

    def __init__(self, hyper_edge_id=None, box_function: BoxFunction = None):
        if hyper_edge_id is None:
            hyper_edge_id = id(self)
        self.id = hyper_edge_id
        # if box_function is null it can be input/output in diagram or user didn`t specified box function
        self.box_function: BoxFunction|None = box_function

        self.source_nodes: dict[int, Node] = dict() # key is connection index, it neede for keeping the right queue
        self.target_nodes: dict[int, Node] = dict()


    def get_source_nodes(self) -> list[Node]:
        """
        :return Ordered list of source nodes(vertices):
        """
        return [item[1] for item in sorted(self.source_nodes.items(), key=lambda item: item[0])]

    def get_target_nodes(self) -> list[Node]:
        """
        :return Ordered list of target nodes(vertices):
        """
        return [item[1] for item in sorted(self.target_nodes.items(), key=lambda item: item[0])]

    def set_source_node(self, conn_index: int, node: Node):
        self.source_nodes[conn_index] = node

    def set_target_node(self, conn_index: int, node: Node):
        self.target_nodes[conn_index] = node

    # def get_source_nodes_with_conn_indexes(self) -> dict_items[int, Node]:
    #     return self.source_nodes.items()
    #
    # def get_target_nodes_with_conn_indexes(self) -> dict_items[int, Node]:
    #     return self.target_nodes.items()

    def get_source_node_connection_index(self, node: Node) -> int|None:
        for conn_index, source_node in self.source_nodes.items():
            if source_node == node:
                return conn_index
        return None

    def get_target_node_connection_index(self, node: Node) -> int|None:
        for conn_index, target_node in self.target_nodes.items():
            if target_node == node:
                return conn_index
        return None

    def remove_source_node(self, conn_index: int):
        if conn_index in self.source_nodes:
            del self.source_nodes[conn_index]

    def remove_target_node(self, conn_index: int):
        if conn_index in self.target_nodes:
            del self.target_nodes[conn_index]

    def remove_self(self):
        pass




    def get_children(self) -> list:
        return list(self._children_nodes.keys())

    def get_parents(self) -> set:
        return set(self._parent_nodes.keys())

    def is_node_child(self, child: HyperEdge) -> bool:
        return child in self._children_nodes

    def is_node_parent(self, parent: HyperEdge) -> bool:
        return parent in self._parent_nodes

    def get_child_by_id(self, child_id: int) -> HyperEdge | None:
        for child in self._children_nodes.keys():
            if child.id == child_id:
                return child
        return None

    def get_parent_by_id(self, parent_id: int) -> HyperEdge | None:
        for parent in self._parent_nodes.keys():
            if parent.id == parent_id:
                return parent
        return None

    def add_child(self, child: HyperEdge, edge_count=1):
        if child in self._children_nodes:
            self._children_nodes[child] += edge_count
            child._parent_nodes[self] += edge_count
        else:
            self._children_nodes[child] = edge_count
            child._parent_nodes[self] = edge_count

    def add_parent(self, parent: HyperEdge, edge_count=1):
        if parent in self._parent_nodes:
            self._parent_nodes[parent] += edge_count
            parent._children_nodes[self] += edge_count
        else:
            self._parent_nodes[parent] = edge_count
            parent._children_nodes[self] = edge_count


    def remove_child(self, child_to_remove: HyperEdge):
        if child_to_remove in self._children_nodes:
            del self._children_nodes[child_to_remove]
            child_to_remove.remove_parent(self)

    def remove_parent(self, parent_to_remove: HyperEdge):
        if parent_to_remove in self._parent_nodes:
            del self._parent_nodes[parent_to_remove]
            parent_to_remove.remove_child(self)

    def _remove_self(self):
        for parent in self._parent_nodes.keys():
            parent.remove_child(self)
        for child in self._children_nodes.keys():
            child.remove_parent(self)
        self._parent_nodes.clear()
        self._children_nodes.clear()

    def remove_parent_edges(self, parent_to_remove: HyperEdge, edge_count=1):
        if parent_to_remove in self._parent_nodes:
            edge_count_with_parent = self._parent_nodes[parent_to_remove]
            edge_count_with_parent -= edge_count
            if edge_count_with_parent > 0:
                self._parent_nodes[parent_to_remove] = edge_count_with_parent

                parent_to_remove._children_nodes[self] = edge_count_with_parent
            else:
                self.remove_parent(parent_to_remove)

    def remove_child_edges(self, child_to_remove: HyperEdge, edge_count=1):
        if child_to_remove in self._children_nodes:
            edge_count_with_child = self._children_nodes[child_to_remove]
            edge_count_with_child -= edge_count
            if edge_count_with_child > 0:
                self._children_nodes[child_to_remove] = edge_count_with_child

                child_to_remove._parent_nodes[self] = edge_count_with_child
            else:
                self.remove_child(child_to_remove)

    def set_box_function(self, function: BoxFunction):
        self.box_function = function

    def get_box_function(self) -> BoxFunction:
        return self.box_function

    def is_valid(self) -> bool:
        return self._children_nodes or self._parent_nodes


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
        if not isinstance(other, HyperEdge):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)


def test_node_str():
    # Create sample nodes
    node1 = HyperEdge(hyper_edge_id=0)
    print(str(node1))
