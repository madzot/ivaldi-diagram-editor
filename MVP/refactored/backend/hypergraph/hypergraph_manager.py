from __future__ import annotations

from queue import Queue
from typing import TYPE_CHECKING

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
                    removed_node_outputs = node.get_node_children()
                    hypergraph.remove_node(id)
                    break
        # check if new hyper graphs were created
        source_nodes: list[Node] = _hypergraph.get_source_nodes() + removed_node_outputs
        source_nodes_groups: list[list[Node]] = list() # list of all source nodes groups
        for source_node in source_nodes:
            group: list[Node] = list()
            for next_source_node in source_nodes:
                if source_node != next_source_node and source_node.is_connected_to(next_source_node):
                    group.append(next_source_node)
            group = sorted(group, key=lambda node: node.id)
            if group not in source_nodes_groups:
                source_nodes_groups.append(group)

        # if after deleting node hype graph split to two or more hyper graphs we need to handle that
        if len(source_nodes_groups) > 1: # If group count isn`t 1, so there occurred new hyper graphs
            HypergraphManager.remove_hypergraph(_hypergraph) # remove old hypergraph

            for group in source_nodes_groups:
                new_hypergraph = Hypergraph(canvas_id=_hypergraph.get_canvas_id())
                new_hypergraph.add_hypergraph_sources(group)
                new_hypergraph.update_source_nodes_descendants()
                new_hypergraph.update_edges()
                HypergraphManager.add_hypergraph(new_hypergraph)


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
    def _get_node_by_id(id: int):
        for hypergraph in HypergraphManager.hypergraphs:
            for node in hypergraph.get_all_nodes():
                if node.id == id:
                    return node

    @staticmethod
    def union_nodes(node: Node, unite_with_id: int):
        unite_with = HypergraphManager._get_node_by_id(unite_with_id)

        node_hypergraph: Hypergraph = HypergraphManager.get_graph_by_node_id(node.id)
        node.union(unite_with)

        unite_with_hypergraph: Hypergraph = HypergraphManager.get_graph_by_node_id(unite_with.id)  # always exits, because node is always forms a hypergraph
        HypergraphManager.combine_hypergraphs([node_hypergraph, unite_with_hypergraph])

    @staticmethod
    def connect_node_with_input(node: Node, hyper_edge_id: int):
        """
        After hypergraph creation is done, make connectivity of node, with node/hyper edge and
        theirs hyper graphs.
        In this case to given node (first arg) input should be added node|hyper edge
        """
        node_hypergraph: Hypergraph = HypergraphManager.get_graph_by_node_id(node.id)
        connect_to_hypergraph: Hypergraph = HypergraphManager.get_graph_by_hyper_edge_id(hyper_edge_id)

        if connect_to_hypergraph is None:
            hyper_edge = HyperEdge(hyper_edge_id)
        else:
            hyper_edge = connect_to_hypergraph.get_hyper_edge_by_id(hyper_edge_id)
        # box = hyper edge
        hyper_edge.append_target_node(node)
        node.append_input(hyper_edge)
        if connect_to_hypergraph is None:  # It is autonomous box
            node_hypergraph.add_edge(hyper_edge)
        else:  # It is box that already have some connections => forms hypergraph
            HypergraphManager.combine_hypergraphs([node_hypergraph, connect_to_hypergraph])

    @staticmethod
    def connect_node_with_output(node: Node, hyper_edge_id: int):
        """
        After hypergraph creation is done, make connectivity of node, with node/hyper edge and
        theirs hyper graphs.
        In this case to given node (first arg) output should be added node|hyper edge
        """
        node_hypergraph: Hypergraph = HypergraphManager.get_graph_by_node_id(node.id)
        connect_to_hypergraph: Hypergraph = HypergraphManager.get_graph_by_hyper_edge_id(hyper_edge_id)

        if connect_to_hypergraph is None:
            hyper_edge = HyperEdge(hyper_edge_id)
        else:
            hyper_edge = connect_to_hypergraph.get_hyper_edge_by_id(hyper_edge_id)
         # box = hyper edge
        hyper_edge.append_source_node(node)
        node.append_output(hyper_edge)
        if connect_to_hypergraph is None:  # It is autonomous box
            HypergraphManager.add_hypergraph(node_hypergraph) # IS IT NEEDED?? TODO
        else:  # It is box that already have some connections => forms hypergraph
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
