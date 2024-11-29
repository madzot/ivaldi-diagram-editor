from __future__ import annotations

from pickle import NEXT_BUFFER
from queue import Queue
from typing import TYPE_CHECKING

from networkx.algorithms.components import is_connected

from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.box import Box
from MVP.refactored.connection import Connection
from MVP.refactored.spider import Spider

if TYPE_CHECKING:
    from MVP.refactored.custom_canvas import CustomCanvas


class HypergraphManager:
    hypergraphs: set[Hypergraph] = set()

    @staticmethod
    def get_graph_by_node_id(node_id: int) -> Hypergraph | None:
        for hypergraph in HypergraphManager.hypergraphs:
            for node in hypergraph.nodes:
                if node.id == node_id:
                    return hypergraph
        return None


    @staticmethod
    def get_graphs_by_canvas_id(canvas_id: int) -> set[Hypergraph]:
        graphs: set[Hypergraph] = set()
        for graph in HypergraphManager.hypergraphs:
            if graph.get_canvas_id() == canvas_id:
                graphs.add(graph)
        return graphs

    @staticmethod
    def add_hypergraph(hypergraph: Hypergraph):
        HypergraphManager.hypergraphs.add(hypergraph)

    @staticmethod
    def modify_canvas_hypergraph(canvas: CustomCanvas) -> None:
        # TODO
        hypergraph = HypergraphManager.get_graphs_by_canvas_id(canvas.id)

        if hypergraph:
            HypergraphManager.hypergraphs.remove(hypergraph)

        HypergraphManager._create_hypergraphs_from_canvas(canvas)

    @staticmethod
    def _create_hypergraphs_from_canvas(canvas: CustomCanvas) -> None:
        # TODO: fix this hypergraph creation to note that many hypergraphs can be created from one canvas
        hypergraph = Hypergraph(canvas.id)
        for box in canvas.boxes:
            node = Node(box.id)
            for connection in box.connections:
                if connection.side == "left" and connection.has_wire:
                    node.add_input(connection.wire.id)
                elif connection.has_wire:
                    node.add_output(connection.wire.id)
            hypergraph.add_node(node)

        if hypergraph._is_valid():
            HypergraphManager.hypergraphs.add(hypergraph)
            print("Valid hypergraph created")
            print(hypergraph.__str__())
        else:
            print("Invalid hypergraph not created")

    @staticmethod
    def create_hypergraphs_from_canvas(canvas: CustomCanvas) -> None:
        hypergraphs_on_canvas = HypergraphManager.get_graphs_by_canvas_id(canvas.id)
        all_existing_nodes: set[tuple[Node, Hypergraph]] = set()
        for hypergraph in hypergraphs_on_canvas:
            for node in hypergraph.get_all_nodes():
                all_existing_nodes.add((node, hypergraph))

        is_independent_graph = True
        hypergraph = Hypergraph(canvas.id)
        for canvas_input in canvas.inputs:
            if canvas_input.box is None: # None if connection is diagram input/output
                source_node = Node(canvas_input.id)
                hypergraph.add_source_node(source_node)

                boxes_to_visit: Queue[tuple[Node, Box|Connection]] = Queue()
                for end_connection in HypergraphManager._get_end_connections(canvas_input):  # iterating children of input (might be the output of diagram or box)
                    boxes_to_visit.put((source_node, end_connection))

                while not boxes_to_visit.empty():
                    node_from, node_to = boxes_to_visit.get()

                    node = Node(node_to.id, box_function=node_to.box_function)
                    is_all_children_are_explored = False

                    for existing_node, existing_node_hypergraph in all_existing_nodes:
                        if existing_node == node:
                            existing_node_hypergraph.add_source_node(source_node)
                            node = existing_node
                            is_all_children_are_explored = True
                            is_independent_graph = False
                            break

                    node.add_parent(node_from)
                    node_from.add_child(node)

                    if isinstance(node_to, Box) and not is_all_children_are_explored: # If this node already exists in other graph,
                        # we don`t need to add his children because they already exists
                        for connection in node_to.connections:
                            if connection.side == "right":
                                for end_connection in HypergraphManager._get_end_connections(connection):
                                    boxes_to_visit.put((node, end_connection))

        if is_independent_graph:
            HypergraphManager.add_hypergraph(hypergraph)


    @staticmethod
    def _get_end_connections(connection: Connection) -> list[Box | Connection]:
        if connection.has_wire and connection.wire.end_connection is not None:
            end_connection = connection.wire.end_connection
            if isinstance(end_connection, Spider):
                connections: list = []
                for connection in end_connection.connections:
                    if connection.side == "right":
                        connections.extend(HypergraphManager._get_end_connections(connection)) # if from spider to spider, need recursion
            else:
                if end_connection.box is not None:
                    return [end_connection.box]
                else:
                    return [end_connection]  # output of the diagram
        return []

