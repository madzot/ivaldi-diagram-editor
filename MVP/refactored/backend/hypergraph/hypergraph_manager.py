from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph, id_dict_hypergraph
from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge
from MVP.refactored.backend.hypergraph.node import Node

if TYPE_CHECKING:
    pass

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', )
logger = logging.getLogger(__name__)

message_start = "\x1b[33;20m"
message_end = "\x1b[0m"

debug = lambda x: logger.debug(message_start + x + message_end)

current_count_node = 0

id_dict_node = {}

current_count_hyper_edge = 0

id_dict_hyper_edge = {}


class HypergraphManager:
    hypergraphs: set[Hypergraph] = set()

    @staticmethod
    def remove_node(id: int):  # TODO handle case, when for example (-0-+-0- -> -0+ 0-)
        """
        Removes a node from the hypergraph and handles the case where deleting the node causes the hypergraph to
        split into multiple disconnected hypergraphs.

        This function performs the following steps:
        1. Removes the specified node from its hypergraph.
        2. Checks if removing the node causes the hypergraph to split into multiple disconnected hypergraphs.
        3. If the hypergraph splits, removes the original hypergraph and creates new hypergraphs for each disconnected component.

        :param id: The unique identifier of the node to be removed.
        """
        logger.debug(message_start + f"Removing node with id {id_dict_node[id]}" + message_end)

        # removed_node_outputs = []
        _hypergraph: Hypergraph = None
        for hypergraph in HypergraphManager.hypergraphs:
            for node in hypergraph.get_all_nodes():
                if node.id == id:
                    _hypergraph = hypergraph
                    # removed_node_outputs = node.get_node_children()
                    hypergraph.remove_node(id)
                    node.remove_self()
                    break
        # check if new hyper graphs were created
        source_nodes: list[Node] = _hypergraph.get_all_nodes()
        source_nodes_groups: list[list[Node]] = list()  # list of all source nodes groups
        for source_node in source_nodes:
            group: list[Node] = list()
            for next_source_node in source_nodes:
                if source_node != next_source_node and source_node.is_connected_to(
                        next_source_node) and next_source_node not in group:
                    # TODO add single node
                    group.append(next_source_node)
            group = sorted(group, key=lambda node: node.id)
            if group not in source_nodes_groups and len(group) != 0:
                source_nodes_groups.append(group)

        logger.debug(message_start + "Source nodes are " + ", ".join(
            f"{id_dict_node[n.id]}" for n in source_nodes) + message_end)
        logger.debug(message_start + "Source node groups are " + ", ".join(
            f"[{', '.join(map(str, (id_dict_node[n.id] for n in group)))}]" for group in
            source_nodes_groups) + message_end)

        # if after deleting node hype graph split to two or more hyper graphs we need to handle that
        if len(source_nodes_groups) > 1:  # If group count isn`t 1, so there occurred new hyper graphs
            HypergraphManager.remove_hypergraph(_hypergraph)  # remove old hypergraph

            for group in source_nodes_groups:
                new_hypergraph = Hypergraph(canvas_id=_hypergraph.get_canvas_id())
                new_hypergraph.add_nodes(group)
                new_hypergraph.update_source_nodes_descendants()
                new_hypergraph.update_edges()
                HypergraphManager.add_hypergraph(new_hypergraph)

    @staticmethod
    def remove_hyper_edge(id: int):
        """
        Removes a hyper edge from the hypergraph and handles the case where deleting the edge causes the hypergraph to
        split into multiple disconnected hypergraphs.

        This function performs the following steps:
        1. Removes the specified hyper edge from its hypergraph.
        2. Checks if removing the hyper edge causes the hypergraph to split into multiple disconnected hypergraphs.
        3. If the hypergraph splits, removes the original hypergraph and creates new hypergraphs for each disconnected component.

        :param id: The unique identifier of the node to be removed.
        """
        logger.debug(message_start + f"Removing hyper edge with id {id_dict_node[id]}" + message_end)

        _hypergraph: Hypergraph = None
        deleted_hyper_edge = None
        for hypergraph in HypergraphManager.hypergraphs:
            if hypergraph.get_hyper_edge_by_id(id) is not None:
                _hypergraph = hypergraph
                deleted_hyper_edge = hypergraph.remove_hyper_edge(id) # remove hyper edge from hypergraph
                break
        # check if new hypergraph appears
        source_nodes: list[Node] = _hypergraph.get_source_nodes() + deleted_hyper_edge.get_target_nodes()
        source_nodes_groups: list[list[Node]] = list()  # list of all source nodes groups
        # TODO move duplicated code into another method?
        for source_node in source_nodes:
            group: list[Node] = list()
            for next_source_node in source_nodes:
                if source_node != next_source_node and source_node.is_connected_to(next_source_node):
                    group.append(next_source_node)
            group = sorted(group, key=lambda node: node.id)
            if group not in source_nodes_groups:
                source_nodes_groups.append(group)

        logger.debug(message_start + "Source nodes are " + ", ".join(
            f"{id_dict_node[n.id]}" for n in source_nodes) + message_end)
        logger.debug(message_start + "Source node groups are " + ", ".join(
            f"[{', '.join(map(str, (id_dict_node[n.id] for n in group)))}]" for group in
            source_nodes_groups) + message_end)
        # if after deleting node hype graph split to two or more hyper graphs we need to handle that
        if len(source_nodes_groups) > 1:  # If group count isn`t 1, so there occurred new hyper graphs
            HypergraphManager.remove_hypergraph(_hypergraph)  # remove old hypergraph

            for group in source_nodes_groups:
                new_hypergraph = Hypergraph(canvas_id=_hypergraph.get_canvas_id())
                new_hypergraph.add_hypergraph_sources(group)
                new_hypergraph.update_source_nodes_descendants()
                new_hypergraph.update_edges()
                HypergraphManager.add_hypergraph(new_hypergraph)

    @staticmethod
    def swap_hyper_edge_id(prev_id: int, new_id: int):
        """
        Replaces a hyper edge ID in the corresponding hypergraph.

        :param prev_id: The current hyper edge ID.
        :param new_id: The new hyper edge ID.
        """
        logger.debug(message_start + f"Swapping hyper edge id from {prev_id} to {new_id}" + message_end)

        hypergraph: Hypergraph = HypergraphManager.get_graph_by_hyper_edge_id(prev_id)
        hypergraph.swap_hyper_edge_id(prev_id, new_id)

    @staticmethod
    def create_new_node(id: int, canvas_id: int) -> Node:
        """
        Create new hypergraph, when spider/diagram input/diagram output/wire is created.

        :return: created node
        """
        global current_count_node
        id_dict_node[id] = current_count_node
        current_count_node += 1
        logger.debug(message_start + f"Creating new node with id {id_dict_node[id]}" + message_end)


        new_hypergraph: Hypergraph = Hypergraph(canvas_id=canvas_id)
        new_node = Node(id)

        new_hypergraph.add_hypergraph_source(new_node)
        HypergraphManager.add_hypergraph(new_hypergraph)
        return new_node

    @staticmethod
    def _get_node_by_id(id: int):
        for hypergraph in HypergraphManager.hypergraphs:
            for node in hypergraph.get_all_nodes():
                if node.id == id:
                    return node

    @staticmethod
    def union_nodes(node: Node, unite_with_id: int):
        logger.debug(message_start + f"Union node with id {id_dict_node[node.id]} with other node with id {id_dict_node[unite_with_id]}" + message_end)

        unite_with = HypergraphManager._get_node_by_id(unite_with_id)
        unite_with_hypergraph: Hypergraph = HypergraphManager.get_graph_by_node_id(unite_with.id)  # always exits, because node is always forms a hypergraph
        node_hypergraph: Hypergraph = HypergraphManager.get_graph_by_node_id(node.id)

        node.union(unite_with)
        if not node_hypergraph == unite_with_hypergraph:
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
            global current_count_hyper_edge
            id_dict_hyper_edge[hyper_edge_id] = current_count_hyper_edge
            current_count_hyper_edge += 1
        else:
            hyper_edge = connect_to_hypergraph.get_hyper_edge_by_id(hyper_edge_id)
        logger.debug(message_start + f"Connecting to node with id {id_dict_node[node.id]} input a hyper edge with id {id_dict_hyper_edge[hyper_edge_id]}" + message_end)
        # box = hyper edge
        hyper_edge.append_target_node(node)
        node.append_input(hyper_edge)
        if connect_to_hypergraph is None:  # It is autonomous box
            node_hypergraph.add_edge(hyper_edge)
        elif not node_hypergraph == connect_to_hypergraph:
            # if node's and hyper edge's hypergraph is the same, it means that new wire between spider and the box is added
            # nothing to combine
            # It is box that already have some connections => forms hypergraph
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
            global current_count_hyper_edge
            id_dict_hyper_edge[hyper_edge_id] = current_count_hyper_edge
            current_count_hyper_edge += 1
        else:
            hyper_edge = connect_to_hypergraph.get_hyper_edge_by_id(hyper_edge_id)
        logger.debug(message_start + f"Connecting to node with id {id_dict_node[node.id]} output a hyper edge with id {id_dict_hyper_edge[hyper_edge_id]}" + message_end)
        # box = hyper edge
        hyper_edge.append_source_node(node)
        node.append_output(hyper_edge)
        if connect_to_hypergraph is None:  # It is autonomous box
            node_hypergraph.add_edge(hyper_edge)
        elif not node_hypergraph == connect_to_hypergraph:
            # if node's and hyper edge's hypergraph is the same, it means that new wire between spider and the box is added
            # nothing to combine
            # It is box that already have some connections => forms hypergraph
            HypergraphManager.combine_hypergraphs([node_hypergraph, connect_to_hypergraph])

    @staticmethod
    def combine_hypergraphs(hypergraphs: list[Hypergraph]):
        """Combine two or more hypergraphs.

        NB!!!
        When combining hypergraphs from different canvases, new hypegraph will have canvas id from first element!!!
        """

        logger.debug(message_start + f"Combining hypergraps with following ids: " + ", ".join(map(lambda x: str(id_dict_hypergraph[x.id]), hypergraphs)) + message_end)

        combined_hypergraph = Hypergraph(canvas_id=hypergraphs[0].canvas_id)
        for hypergraph in hypergraphs:
            combined_hypergraph.add_nodes(hypergraph.get_hypergraph_source())  # adding source node
            combined_hypergraph.update_edges()
            combined_hypergraph.update_source_nodes_descendants()
            HypergraphManager.remove_hypergraph(hypergraph)
        HypergraphManager.add_hypergraph(combined_hypergraph)

    @staticmethod
    def get_graph_by_node_id(node_id: int) -> Hypergraph|None:
        for hypergraph in HypergraphManager.hypergraphs:
            if node_id in hypergraph.nodes:
                return hypergraph
        return None

    @staticmethod
    def get_graph_by_hyper_edge_id(hyper_edge_id: int) -> Hypergraph | None:
        for hypergraph in HypergraphManager.hypergraphs:
            if hyper_edge_id in hypergraph.edges:
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
        logger.debug(message_start + f"Adding hypergraph with id {id_dict_hypergraph[hypergraph.id]}" + message_end)

        HypergraphManager.hypergraphs.add(hypergraph)

    @staticmethod
    def remove_hypergraph(hypergraph: Hypergraph):
        logger.debug(message_start + f"Removing hypergraph with id {id_dict_hypergraph[hypergraph.id]}" + message_end)
        HypergraphManager.hypergraphs.remove(hypergraph)
