from unittest import TestCase
from unittest.mock import MagicMock, patch

from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge
from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph


class TestHypergraphManager(TestCase):

    def setUp(self):
        HypergraphManager.hypergraphs.clear()
        self.sample_node = Node(1)
        self.sample_hypergraph = Hypergraph(canvas_id=123)
        self.sample_hyper_edge = HyperEdge(10)

    def tearDown(self):
        HypergraphManager.hypergraphs.clear()

    # TEST: Node creation and registration
    # ----------------------------------------------------------
    def test_create_new_node_creates_node_and_registers_hypergraph(self):
        canvas_id = 100
        node = HypergraphManager.create_new_node(id=1, canvas_id=canvas_id)

        self.assertIsInstance(node, Node)
        graph = HypergraphManager.get_graph_by_node_id(node.id)
        self.assertIsNotNone(graph)
        self.assertIn(node, graph.get_all_nodes())

    # TEST: Add and remove hypergraphs
    # ----------------------------------------------------------
    def test_add_and_remove_hypergraph(self):
        HypergraphManager.add_hypergraph(self.sample_hypergraph)
        self.assertIn(self.sample_hypergraph, HypergraphManager.hypergraphs)

        HypergraphManager.remove_hypergraph(self.sample_hypergraph)
        self.assertNotIn(self.sample_hypergraph, HypergraphManager.hypergraphs)

    # TEST: Getters
    # ----------------------------------------------------------
    def test_get_graph_by_node_id_returns_correct_hypergraph(self):
        self.sample_hypergraph.nodes = {self.sample_node.id: self.sample_node}
        HypergraphManager.add_hypergraph(self.sample_hypergraph)

        graph = HypergraphManager.get_graph_by_node_id(self.sample_node.id)
        self.assertEqual(graph, self.sample_hypergraph)

    def test_get_graph_by_source_node_id_handles_union_properly(self):
        source_node = Node(1)
        union_node = Node(999)

        source_node.get_united_with_nodes = MagicMock(return_value=[union_node])

        hypergraph = Hypergraph(canvas_id=321)
        hypergraph.get_hypergraph_source = MagicMock(return_value=[source_node])

        HypergraphManager.add_hypergraph(hypergraph)

        result = HypergraphManager.get_graph_by_source_node_id(union_node.id)
        self.assertEqual(result, hypergraph)

    def test_get_graph_by_hyper_edge_id_returns_correct_hypergraph(self):
        self.sample_hypergraph.edges = {self.sample_hyper_edge.id: self.sample_hyper_edge}
        HypergraphManager.add_hypergraph(self.sample_hypergraph)

        graph = HypergraphManager.get_graph_by_hyper_edge_id(self.sample_hyper_edge.id)
        self.assertEqual(graph, self.sample_hypergraph)

    def test_get_graphs_by_canvas_id_returns_all_matching_graphs(self):
        g1 = Hypergraph(canvas_id=5)
        g2 = Hypergraph(canvas_id=5)
        g3 = Hypergraph(canvas_id=99)

        HypergraphManager.add_hypergraph(g1)
        HypergraphManager.add_hypergraph(g2)
        HypergraphManager.add_hypergraph(g3)

        result = HypergraphManager.get_graphs_by_canvas_id(5)
        self.assertIn(g1, result)
        self.assertIn(g2, result)
        self.assertNotIn(g3, result)

    # TEST: Union Nodes
    # ----------------------------------------------------------
    def test_union_nodes_combines_hypergraphs(self):
        node_a = Node(1)
        node_b = Node(2)

        graph_a = Hypergraph(canvas_id=1)
        graph_b = Hypergraph(canvas_id=1)
        graph_a.nodes = {node_a.id: node_a}
        graph_b.nodes = {node_b.id: node_b}

        HypergraphManager.add_hypergraph(graph_a)
        HypergraphManager.add_hypergraph(graph_b)

        node_a.union = MagicMock()
        node_b.get_united_with_nodes = MagicMock(return_value=[])

        with patch.object(HypergraphManager, "_get_node_by_id", return_value=node_b):
            HypergraphManager.union_nodes(node_a, node_b.id)

        self.assertEqual(len(HypergraphManager.hypergraphs), 1)

    # TEST: Edge Connect (input/output) TODO
    # ----------------------------------------------------------
    def test_connect_node_with_input_creates_new_edge_if_none_exists(self):
        node = HypergraphManager.create_new_node(1, 999)

        graph = HypergraphManager.get_graph_by_node_id(node.id)
        print(len(graph.source_nodes))
        print(len(graph.edges))
        print(len(graph.nodes))
        HypergraphManager.connect_node_with_input(node, hyper_edge_id=111)
        graph.update_source_nodes_descendants()
        graph.update_edges()
        print(len(graph.edges))
        print(len(graph.nodes))
        self.assertTrue(any(node in edge.target_nodes for edge in graph.get_all_hyper_edges()))

    def test_connect_node_with_output_creates_new_edge_if_none_exists(self):
        node = HypergraphManager.create_new_node(2, 888)
        HypergraphManager.connect_node_with_output(node, hyper_edge_id=222)

        graph = HypergraphManager.get_graph_by_node_id(node.id)
        self.assertTrue(any(node in edge.source_nodes for edge in graph.get_all_hyper_edges()))

    # TEST: Node/Edge Removal – Requires internal graph state TODO
    # ----------------------------------------------------------
    def test_remove_node_splits_hypergraph_correctly(self):
        # Create three nodes: A -- B -- C (A connected to B, B connected to C)
        node_a = Node(1)
        node_b = Node(2)
        node_c = Node(3)

        # Simulate basic is_connected_to behavior
        node_a.is_connected_to = MagicMock(side_effect=lambda other: other.id == 2)
        node_b.is_connected_to = MagicMock(side_effect=lambda other: other.id in [1, 3])
        node_c.is_connected_to = MagicMock(side_effect=lambda other: other.id == 2)

        # Node children & united nodes empty for simplicity
        node_a.get_node_children = MagicMock(return_value=[])
        node_b.get_node_children = MagicMock(return_value=[])
        node_c.get_node_children = MagicMock(return_value=[])

        node_a.directly_connected_to = [node_b]
        node_b.directly_connected_to = [node_a, node_c]
        node_c.directly_connected_to = [node_b]

        # Create and register initial hypergraph
        hypergraph = Hypergraph(canvas_id=123)
        hypergraph.nodes = {1: node_a, 2: node_b, 3: node_c}
        hypergraph.source_nodes = {1: node_a}

        HypergraphManager.add_hypergraph(hypergraph)

        # Remove the center node (node B)
        HypergraphManager.remove_node(2)

        # Now check that two new hypergraphs have been created (A and C should be disconnected)
        self.assertEqual(len(HypergraphManager.hypergraphs), 2)

        # Each new graph should contain only one node (A or C)
        all_nodes = [list(graph.get_all_nodes()) for graph in HypergraphManager.hypergraphs]
        all_node_ids = sorted([node.id for nodes in all_nodes for node in nodes])
        self.assertEqual(all_node_ids, [1, 3])

    def test_remove_hyper_edge_splits_hypergraph_correctly(self):
        # Placeholder for future implementation
        pass

    # TEST: Swap edge ID
    # ----------------------------------------------------------
    def test_swap_hyper_edge_id_delegates_to_hypergraph(self):
        graph = Hypergraph(canvas_id=1)
        graph.swap_hyper_edge_id = MagicMock()
        graph.edges = {10: HyperEdge(10)}

        HypergraphManager.add_hypergraph(graph)

        with patch.object(HypergraphManager, "get_graph_by_hyper_edge_id", return_value=graph):
            HypergraphManager.swap_hyper_edge_id(prev_id=10, new_id=20)

        graph.swap_hyper_edge_id.assert_called_once_with(10, 20)

