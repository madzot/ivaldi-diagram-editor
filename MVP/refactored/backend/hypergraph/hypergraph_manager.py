from __future__ import annotations

from queue import Queue
from typing import TYPE_CHECKING


from MVP.refactored.box import Box
from MVP.refactored.connection import Connection
from MVP.refactored.spider import Spider

if TYPE_CHECKING:
    from MVP.refactored.custom_canvas import CustomCanvas
    from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
    from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge
    from MVP.refactored.backend.hypergraph.node import Node


class HypergraphManager:
    hypergraphs: set[Hypergraph] = set()

    @staticmethod
    def remove_node(id: int):
        _hypergraph: Hypergraph = None
        for hypergraph in HypergraphManager.hypergraphs:
            for node in hypergraph.get_all_nodes():
                if node.id == id:
                    _hypergraph = hypergraph
                    hypergraph.remove_node(id)
        # check if new hyper graphs were created
        source_nodes: list[Node] = _hypergraph.get_source_nodes()
        source_nodes_groups: list[list[Node]] = list() # list of all source nodes groups
        for source_node in source_nodes:
            group: list[Node] = list()
            for next_source_node in source_nodes:
                if source_node != next_source_node and source_node.is_connected_to(next_source_node):
                    group.append(next_source_node)
            group = sorted(group, key=lambda node: node.id)
            if group not in source_nodes_groups:
                source_nodes_groups.append(group)
        #TODO create new hypergraphs from source_nodes_groups and delete exicting one

    @staticmethod
    def create_new_node(id: int, canvas_id: int) -> Node:
        """
        Create new hypergraph, when spider is created.

        :return: created node
        """
        new_hypergraph: Hypergraph = Hypergraph(canvas_id=canvas_id)
        new_node = Node(id)
        new_hypergraph.add_hypergraph_source(new_node)
        return new_node

    @staticmethod
    def connect_node_with_input(node: Node, connect_to: Node|HyperEdge):
        """
        After hypergraph creation is done, make connectivity of node, with node/hyperedge and
        theirs hyper graphs.
        In this case to given node (first arg) input should be added node|hyper edge
        """
        node_hypergraph: Hypergraph = HypergraphManager.get_graph_by_node_id(node.id)
        if isinstance(connect_to, Node): # spider or diagram input
            connect_to.union(node)
            connect_to_hypergraph : Hypergraph = HypergraphManager.get_graph_by_node_id(connect_to.id) # always exits, because node is always forms a hypergraph
            HypergraphManager.combine_hypergraphs([node_hypergraph, connect_to_hypergraph])
        else: # box
            connect_to.append_target_node(node)
            node.append_input(connect_to)
            connect_to_hypergraph: Hypergraph = HypergraphManager.get_graph_by_hyper_edge_id(connect_to.id)
            if connect_to_hypergraph is None: # It is autonomous box
                HypergraphManager.add_hypergraph(node_hypergraph)
            else: # It is box that already have some connections => forms hypergraph
                HypergraphManager.combine_hypergraphs([node_hypergraph, connect_to_hypergraph])

    @staticmethod
    def combine_hypergraphs(hypergraphs: list[Hypergraph]):
        """Combine two or more hypergraphs.

        NB!!!
        When combining hypergraphs from different canvases, new hypegraph will have canvas id from first element!!!
        """
        combined_hypergraph = Hypergraph(canvas_id=hypergraphs[0].canvas_id)
        for hypergraph in hypergraphs:
            combined_hypergraph.nodes.update(hypergraph.nodes)
            combined_hypergraph.edges.update(hypergraph.edges)
            combined_hypergraph.add_hypergraph_sources(hypergraph.get_source_nodes())

            HypergraphManager.remove_hypergraph(hypergraph)
        HypergraphManager.add_hypergraph(combined_hypergraph)

    @staticmethod
    def get_graph_by_node_id(node_id: int) -> Hypergraph|Node:
        for hypergraph in HypergraphManager.hypergraphs:
            if node_id in hypergraph.nodes:
                return hypergraph
        return None

    @staticmethod
    def get_graph_by_hyper_edge_id(hyper_edge_id: int) -> Hypergraph | None:
        for hypergraph in HypergraphManager.hypergraphs:
            for hyper_edge in hypergraph.get_all_hyper_edges():
                if hyper_edge.id == hyper_edge_id:
                    return hypergraph
        return None

    @staticmethod
    def get_graph_by_source_node_id(source_node_id: int) -> Hypergraph | None:
        for hypergraph in HypergraphManager.hypergraphs:
            for source_node in hypergraph.get_hypergraph_source():
                for source_node_union in source_node.get_all_directly_connected_to():
                    if source_node_union.id == source_node_id:
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
    def remove_hypergraph(hypergraph: Hypergraph):
        HypergraphManager.hypergraphs.remove(hypergraph)
