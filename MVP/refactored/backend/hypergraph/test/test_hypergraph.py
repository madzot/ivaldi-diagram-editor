from unittest import TestCase
from unittest.mock import MagicMock

import networkx as nx
import numpy as np
from matplotlib import pyplot as plt

from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge


class TestHypergraph(TestCase):
    def setUp(self):
        # create nodes
        self.node0 = Node(0)
        self.node1 = Node(1)
        self.node2 = Node(2)
        self.node3 = Node(3)
        self.node4 = Node(4)
        self.node5 = Node(5)
        # create hyper edges
        self.edge0 = HyperEdge(100)
        self.edge1 = HyperEdge(101)
        self.edge2 = HyperEdge(102)
        self.edge3 = HyperEdge(103)
        # create hypergraph
        self.hypergraph = Hypergraph(201)

    # Tests add_node/add_nodes
    # --------------------------------------
    def test_add_single_node(self):
        self.hypergraph.add_node(self.node1)

        self.assertIn(self.node1.id, self.hypergraph.nodes)
        self.assertEqual(self.hypergraph.nodes[self.node1.id], self.node1)

    def test_add_single_node_as_source(self):
        self.hypergraph.add_node(self.node1)

        self.assertIn(self.node1.id, self.hypergraph.hypergraph_source)

    def test_add_node_with_parents(self):
        self.node2.get_parent_nodes = lambda: [self.node1]

        self.hypergraph.add_node(self.node2)

        self.assertNotIn(self.node2.id, self.hypergraph.hypergraph_source)

    def test_add_directly_connected_nodes(self):
        self.node1.get_united_with_nodes = lambda: [self.node2, self.node3]

        self.hypergraph.add_node(self.node1)

        self.assertIn(self.node2.id, self.hypergraph.nodes)
        self.assertIn(self.node3.id, self.hypergraph.nodes)

    def test_add_multiple_nodes(self):
        self.hypergraph.add_nodes([self.node1, self.node2, self.node3])

        self.assertIn(self.node1.id, self.hypergraph.nodes)
        self.assertIn(self.node2.id, self.hypergraph.nodes)
        self.assertIn(self.node3.id, self.hypergraph.nodes)

    def test_add_multiple_nodes_as_sources(self):
        self.hypergraph.add_nodes([self.node1, self.node2])

        self.assertIn(self.node1.id, self.hypergraph.hypergraph_source)
        self.assertIn(self.node2.id, self.hypergraph.hypergraph_source)

    def test_add_multiple_nodes_with_united_nodes(self):
        self.node1.get_united_with_nodes = lambda: [self.node2]
        self.node2.get_united_with_nodes = lambda: [self.node3]

        self.hypergraph.add_nodes([self.node1, self.node2])

        self.assertIn(self.node3.id, self.hypergraph.nodes)

    # Test add_hypergraph_source/add_hypergraph_sources
    # --------------------------------------
    def test_add_single_hypergraph_source(self):
        self.hypergraph.add_hypergraph_source(self.node1)

        self.assertIn(self.node1.id, self.hypergraph.hypergraph_source)

    def test_add_hypergraph_source_with_directly_connected_nodes(self):
        self.node1.get_united_with_nodes = lambda: [self.node2, self.node3]
        self.hypergraph.add_hypergraph_source(self.node1)

        self.assertIn(self.node1.id, self.hypergraph.hypergraph_source)
        self.assertIn(self.node2.id, self.hypergraph.hypergraph_source)
        self.assertIn(self.node3.id, self.hypergraph.hypergraph_source)

    def test_add_multiple_hypergraph_sources(self):
        self.node1.get_united_with_nodes = lambda: [self.node2]
        self.node2.get_united_with_nodes = lambda: [self.node3]

        self.hypergraph.add_hypergraph_sources([self.node1, self.node2])

        self.assertIn(self.node1.id, self.hypergraph.hypergraph_source)
        self.assertIn(self.node2.id, self.hypergraph.hypergraph_source)
        self.assertIn(self.node3.id, self.hypergraph.hypergraph_source)

    def test_add_multiple_hypergraph_sources_with_no_direct_connections(self):
        self.hypergraph.add_hypergraph_sources([self.node1, self.node4])

        self.assertIn(self.node1.id, self.hypergraph.hypergraph_source)
        self.assertIn(self.node4.id, self.hypergraph.hypergraph_source)

    # Test remove_node
    # --------------------------------------
    def test_remove_single_node(self):
        self.hypergraph.add_node(self.node1)
        self.hypergraph.remove_node(self.node1.id)

        self.assertNotIn(self.node1.id, self.hypergraph.nodes)

    def test_remove_source_node(self):
        self.hypergraph.add_node(self.node1)
        self.hypergraph.remove_node(self.node1.id)

        self.assertNotIn(self.node1.id, self.hypergraph.hypergraph_source)

    def test_remove_node_with_directly_connected(self):
        self.node0.get_united_with_nodes = lambda: [self.node1]
        self.node1.get_united_with_nodes = lambda: [self.node0, self.node2]
        self.node2.get_united_with_nodes = lambda: [self.node1, self.node3]
        self.node3.get_united_with_nodes = lambda: [self.node2, self.node4]
        self.node4.get_united_with_nodes = lambda: [self.node3]

        self.hypergraph.add_nodes([self.node0, self.node1, self.node2, self.node3, self.node4])
        self.hypergraph.remove_node(self.node1.id)

        self.assertNotIn(self.node0.id, self.hypergraph.nodes)
        self.assertNotIn(self.node1.id, self.hypergraph.nodes)

        self.assertNotIn(self.node0.id, self.hypergraph.hypergraph_source)
        self.assertNotIn(self.node1.id, self.hypergraph.hypergraph_source)

        self.assertIn(self.node2.id, self.hypergraph.nodes)
        self.assertIn(self.node3.id, self.hypergraph.nodes)
        self.assertIn(self.node4.id, self.hypergraph.nodes)

        self.assertIn(self.node2.id, self.hypergraph.hypergraph_source)
        self.assertIn(self.node3.id, self.hypergraph.hypergraph_source)
        self.assertIn(self.node4.id, self.hypergraph.hypergraph_source)

    def test_remove_node_does_not_affect_unconnected_nodes(self):
        self.node1.is_connected_to = lambda _: False
        self.node2.is_connected_to = lambda _: False

        self.hypergraph.add_node(self.node1)
        self.hypergraph.add_node(self.node2)
        self.hypergraph.remove_node(self.node1.id)

        self.assertNotIn(self.node1.id, self.hypergraph.nodes)
        self.assertNotIn(self.node1.id, self.hypergraph.hypergraph_source)

    def test_remove_node_calls_remove_self(self):
        self.node1.remove_self = MagicMock()

        self.hypergraph.add_node(self.node1)
        self.hypergraph.remove_node(self.node1.id)

        self.node1.remove_self.assert_called_once()

    # Test remove_hyper_edge
    # --------------------------------------
    def test_remove_single_hyper_edge(self):
        self.hypergraph.add_edge(self.edge1)
        self.hypergraph.remove_hyper_edge(self.edge1.id)

        self.assertNotIn(self.edge1.id, self.hypergraph.edges)

    def test_remove_hyper_edge_not_found(self):
        with self.assertRaises(KeyError):
            self.hypergraph.remove_hyper_edge(999)

    def test_remove_multiple_hyper_edges(self):
        self.hypergraph.add_edges([self.edge1, self.edge2, self.edge3])

        self.hypergraph.remove_hyper_edge(self.edge1.id)
        self.hypergraph.remove_hyper_edge(self.edge2.id)

        self.assertNotIn(self.edge1.id, self.hypergraph.edges)
        self.assertNotIn(self.edge2.id, self.hypergraph.edges)
        self.assertIn(self.edge3.id, self.hypergraph.edges)

    def test_remove_hyper_verify_remove_self_called(self):
        # TODO if remove_self() does nothing than test is useless
        self.edge1.remove_self = MagicMock()

        self.hypergraph.add_edge(self.edge1)
        self.hypergraph.remove_hyper_edge(self.edge1.id)

        self.edge1.remove_self.assert_called_once()

    # Test swap_hyper_edge_id
    # --------------------------------------
    def test_swap_hyper_edge_id_valid(self):
        self.hypergraph.add_edge(self.edge1)
        self.hypergraph.add_edge(self.edge2)

        self.hypergraph.swap_hyper_edge_id(self.edge1.id, self.edge2.id)

        self.assertEqual(self.hypergraph.edges[self.edge2.id], self.edge1)
        self.assertEqual(self.hypergraph.edges[self.edge1.id], self.edge2)

    def test_swap_hyper_edge_id_with_nonexistent_edge(self):
        with self.assertRaises(KeyError):
            self.hypergraph.swap_hyper_edge_id(999, self.edge2.id)
        with self.assertRaises(KeyError):
            self.hypergraph.swap_hyper_edge_id(self.edge1.id, 999)

    def test_swap_hyper_edge_id_same_id(self):
        self.hypergraph.add_edge(self.edge1)
        self.hypergraph.swap_hyper_edge_id(self.edge1.id, self.edge1.id)

        self.assertEqual(self.hypergraph.edges[self.edge1.id], self.edge1)

    def test_swap_hyper_edge_id_with_mocked_swap_id(self):
        self.edge1.swap_id = MagicMock()

        self.hypergraph.add_edge(self.edge1)
        self.hypergraph.add_edge(self.edge2)
        self.hypergraph.swap_hyper_edge_id(self.edge1.id, self.edge2.id)

        self.edge1.swap_id.assert_called_once_with(self.edge2.id)

    def test_swap_hyper_edge_id_after_removal(self):
        self.hypergraph.add_edge(self.edge1)
        self.hypergraph.add_edge(self.edge2)
        self.hypergraph.remove_hyper_edge(self.edge1.id)

        with self.assertRaises(KeyError):
            self.hypergraph.swap_hyper_edge_id(self.edge1.id, self.edge2.id)

    # Test update_source_nodes_descendants
    # --------------------------------------
    def test_update_source_nodes_descendants_single_source(self):
        self.node1.get_children_nodes = lambda: [self.node2]
        self.node1.get_united_with_nodes = lambda: [self.node3]

        self.hypergraph.add_hypergraph_source(self.node1)
        self.hypergraph.update_source_nodes_descendants()

        self.assertIn(self.node1.id, self.hypergraph.nodes)
        self.assertIn(self.node2.id, self.hypergraph.nodes)
        self.assertIn(self.node3.id, self.hypergraph.nodes)

    def test_update_source_nodes_descendants_multiple_sources(self):
        self.node1.get_children_nodes = lambda: [self.node2]
        self.node1.get_united_with_nodes = lambda: [self.node3]
        self.node2.get_children_nodes = lambda: [self.node4]
        self.node2.get_united_with_nodes = lambda: [self.node5]

        self.hypergraph.add_hypergraph_sources([self.node1, self.node2])
        self.hypergraph.update_source_nodes_descendants()

        self.assertIn(self.node1.id, self.hypergraph.nodes)
        self.assertIn(self.node2.id, self.hypergraph.nodes)
        self.assertIn(self.node3.id, self.hypergraph.nodes)
        self.assertIn(self.node4.id, self.hypergraph.nodes)
        self.assertIn(self.node5.id, self.hypergraph.nodes)

    def test_update_source_nodes_descendants_empty_source(self):
        self.hypergraph.update_source_nodes_descendants()
        self.assertEqual(len(self.hypergraph.nodes), 0)

    def test_update_source_nodes_descendants_with_complex_graph_one_source(self):
        nodes = [Node(i) for i in range(11)]

        nodes[0].get_children_nodes = lambda: []
        nodes[1].get_children_nodes = lambda: []
        nodes[2].get_children_nodes = lambda: []
        nodes[3].get_children_nodes = lambda: []
        nodes[4].get_children_nodes = lambda: []
        nodes[5].get_children_nodes = lambda: []
        nodes[6].get_children_nodes = lambda: []
        nodes[7].get_children_nodes = lambda: []
        nodes[8].get_children_nodes = lambda: []
        nodes[9].get_children_nodes = lambda: []
        nodes[10].get_children_nodes = lambda: []

        nodes[0].get_united_with_nodes = lambda: []
        nodes[1].get_united_with_nodes = lambda: []
        nodes[2].get_united_with_nodes = lambda: []
        nodes[3].get_united_with_nodes = lambda: []
        nodes[4].get_united_with_nodes = lambda: []
        nodes[5].get_united_with_nodes = lambda: []

        edge1 = HyperEdge(100)
        edge1.append_source_nodes()
        edge1.append_target_node()

        edge2 = HyperEdge(101)
        edge2.append_source_nodes()
        edge2.append_target_node()

        edge3 = HyperEdge(102)
        edge3.append_source_nodes()
        edge3.append_target_node()

        self.hypergraph.add_edge(edge1)
        self.hypergraph.add_edge(edge2)
        self.hypergraph.add_edge(edge3)
        self.hypergraph.add_hypergraph_source(nodes[0])
        self.hypergraph.update_source_nodes_descendants()

        for node in nodes:
            self.assertIn(node.id, self.hypergraph.nodes)
        for edge in self.hypergraph.edges.values():
            for node in edge.get_source_nodes() + edge.get_target_nodes():
                self.assertIn(node.id, self.hypergraph.nodes)

    def test_update_source_nodes_descendants_with_complex_graph_two_sources(self):
        nodes = [Node(i) for i in range(16)]

        nodes[0].get_children_nodes = lambda: []
        nodes[1].get_children_nodes = lambda: []
        nodes[2].get_children_nodes = lambda: []
        nodes[3].get_children_nodes = lambda: []
        nodes[4].get_children_nodes = lambda: []
        nodes[5].get_children_nodes = lambda: []
        nodes[6].get_children_nodes = lambda: []
        nodes[7].get_children_nodes = lambda: []
        nodes[8].get_children_nodes = lambda: []
        nodes[9].get_children_nodes = lambda: []
        nodes[10].get_children_nodes = lambda: []
        nodes[11].get_children_nodes = lambda: []
        nodes[12].get_children_nodes = lambda: []
        nodes[13].get_children_nodes = lambda: []
        nodes[14].get_children_nodes = lambda: []
        nodes[15].get_children_nodes = lambda: []
        nodes[16].get_children_nodes = lambda: []

        nodes[0].get_united_with_nodes = lambda: []
        nodes[1].get_united_with_nodes = lambda: []
        nodes[2].get_united_with_nodes = lambda: []
        nodes[3].get_united_with_nodes = lambda: []
        nodes[4].get_united_with_nodes = lambda: []
        nodes[5].get_united_with_nodes = lambda: []

        edge1 = HyperEdge(100)
        edge1.append_source_nodes()
        edge1.append_target_node()

        edge2 = HyperEdge(101)
        edge2.append_source_nodes()
        edge2.append_target_node()

        edge3 = HyperEdge(102)
        edge3.append_source_nodes()
        edge3.append_target_node()

        self.hypergraph.add_edge(edge1)
        self.hypergraph.add_edge(edge2)
        self.hypergraph.add_edge(edge3)
        self.hypergraph.add_hypergraph_sources([nodes[0], nodes[1]])
        self.hypergraph.update_source_nodes_descendants()

        for node in nodes:
            self.assertIn(node.id, self.hypergraph.nodes)
        for edge in self.hypergraph.edges.values():
            for node in edge.get_source_nodes() + edge.get_target_nodes():
                self.assertIn(node.id, self.hypergraph.nodes)

    # Test update_edges
    # --------------------------------------
