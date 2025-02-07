from __future__ import annotations


from typing import TYPE_CHECKING

from MVP.refactored.backend.box_functions.box_function import BoxFunction

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

    def swap_id(self, new_id: int):
        self.id = new_id

    def remove_all_source_nodes(self):
        self.source_nodes.clear()

    def remove_all_target_nodes(self):
        self.target_nodes.clear()

    def remove_source_connection_by_index(self, conn_index: int):
        """NB! It deletes connection and all connection with index more that current connection index,
        their connection decreases.
        """
        if conn_index in self.source_nodes:
            del self.source_nodes[conn_index]
        for key in self.source_nodes.keys():
            if key > conn_index:
                self.source_nodes[key - 1] = self.source_nodes[key]
                del self.source_nodes[key]

    def remove_target_connection_by_index(self, conn_index: int):
        """NB! It deletes connection and all connection with index more that current connection index,
        their connection decreases.
        """
        if conn_index in self.source_nodes:
            del self.target_nodes[conn_index]
        for key in self.target_nodes.keys():
            if key > conn_index:
                self.target_nodes[key - 1] = self.target_nodes[key]
                del self.target_nodes[key]

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
        if conn_index in self.source_nodes:
            self.set_source_node(conn_index + 1, self.source_nodes[conn_index])
        self.source_nodes[conn_index] = node

    def set_target_node(self, conn_index: int, node: Node):
        if conn_index in self.target_nodes:
            self.set_target_node(conn_index + 1, self.target_nodes[conn_index])
        self.target_nodes[conn_index] = node

    def append_target_node(self, node: Node):
        self.target_nodes[len(self.target_nodes)] = node

    def append_source_node(self, node: Node):
        self.source_nodes[len(self.source_nodes)] = node

    def append_source_nodes(self, nodes: list[Node]):
        for node in nodes:
            self.append_source_node(node)

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

    def remove_source_node_by_connection_index(self, conn_index: int):
        if conn_index in self.source_nodes:
            del self.source_nodes[conn_index]

    def remove_target_node_by_connection_index(self, conn_index: int):
        if conn_index in self.target_nodes:
            del self.target_nodes[conn_index]

    def remove_source_node_by_reference(self, node: Node):
        connection_index = self.get_source_node_connection_index(node)
        if connection_index:
            del self.source_nodes[connection_index]

    def remove_target_node_by_reference(self, node: Node):
        connection_index = self.get_target_node_connection_index(node)
        if connection_index:
            del self.target_nodes[connection_index]

    def remove_self(self):
        pass

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
        return (f"Hyper edge ID: {self.id}\n"
                f"Inputs: {self.get_source_nodes()}\n"
                f"Outputs: {self.get_target_nodes()}")

    def __eq__(self, other):
        if not isinstance(other, HyperEdge):
            return False
        return other.id == self.id

    def __hash__(self):
        return hash(self.id)
