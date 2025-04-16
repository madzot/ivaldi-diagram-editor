import math

import networkx as nx
import matplotlib.pyplot as plt
from string import ascii_lowercase

from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge
from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.hypergraph.node import Node


class Visualization:

    @classmethod
    def create_visualization_of_hypergraphs(cls, canvas_id: int) -> plt.Figure:
        hypergraphs: list[Hypergraph] = HypergraphManager.get_graphs_by_canvas_id(canvas_id)
        visualizations: list[plt.Figure] = []
        for hypergraph in hypergraphs:
            visualization = cls.create_visualization_of_hypergraph(hypergraph)
            visualizations.append(visualization)
        return cls.combine_visualizations(visualizations)

    @classmethod
    def create_visualization_of_hypergraph(cls, hypergraph: Hypergraph) -> plt.Figure:
        nodes: list[Node] = hypergraph.get_all_nodes()
        edges: list[HyperEdge] = hypergraph.get_all_hyper_edges()

        g = nx.DiGraph()
        g.add_nodes_from(nodes)

        for edge in edges:
            if len(edge.get_source_nodes()) == 1 and len(edge.get_target_nodes()) == 1:
                g.add_edge(edge.get_source_nodes()[0].id, edge.get_target_nodes()[0].id)
            else:
                g.add_node(edge.id)  # hyper edge
                for source_node in edge.get_source_nodes():
                    g.add_edge(source_node.id, edge.id)
                for target_node in edge.get_target_nodes():
                    g.add_edge(edge.id, target_node.id)

        try:
            pos = nx.spring_layout(g)
        except nx.NetworkXException:
            pos = nx.kamada_kawai_layout(g)

        fig, ax = plt.subplots(figsize=(10, 10))
        fig.patch.set_facecolor('white')
        ax.axis('off')

        connected_nodes = {n for edge in g.edges() for n in edge}
        for node in connected_nodes:
            color, size = cls._get_node_color_and_size(node, hypergraph)
            nx.draw_networkx_nodes(g, pos, nodelist=[node], node_color=color, node_size=size, ax=ax)
        nx.draw_networkx_edges(g, pos, ax=ax, edge_color='#161925',
                               connectionstyle='arc3,rad=0.05', arrows=False)

        labels = cls._generate_node_labels(hypergraph, connected_nodes, g)
        nx.draw_networkx_labels(g, pos, labels=labels, ax=ax, font_color='black', font_size=10)

        plt.title("Hypergraph Visualization", fontsize=16, color='black')
        plt.tight_layout()
        return fig

    @classmethod
    def _get_node_color_and_size(cls, node: int, hypergraph: Hypergraph):
        hyperedge_ids = {edge.id for edge in hypergraph.get_all_hyper_edges()}
        source_target_ids = {n.id for n in hypergraph.get_hypergraph_source() + hypergraph.get_hypergraph_target()}

        if node in hyperedge_ids:
            return '#23395B', 25
        if node not in source_target_ids:
            return '#CBF7ED', 300
        return '#8EA8C3', 100

    @staticmethod
    def _generate_node_labels(hypergraph: Hypergraph, connected_nodes: set[int], g: nx.DiGraph) -> dict[int, str]:
        inputs = [inp for inp in hypergraph.get_hypergraph_source() if inp.id in g.nodes]
        outputs = [inp for inp in hypergraph.get_hypergraph_target() if inp.id in g.nodes]
        hyperedge_ids = {edge.id for edge in hypergraph.get_all_hyper_edges()}

        input_ids = [node.id for node in inputs]
        output_ids = [node.id for node in outputs]
        internal_ids = [node.id for node in hypergraph.get_all_nodes()
                        if node.id not in input_ids + output_ids + list(hyperedge_ids)
                        and node.id in g.nodes]

        labels = {}
        if len(input_ids) == 1:
            labels.update({input_ids[0]: "input"} if input_ids[0] in connected_nodes else {})
        else:
            for i, nid in enumerate(input_ids):
                if nid in connected_nodes:
                    labels[nid] = f"input_{ascii_lowercase[i]}"

        if len(output_ids) == 1:
            labels.update({output_ids[0]: "output"} if output_ids[0] in connected_nodes else {})
        else:
            for i, nid in enumerate(output_ids):
                if nid in connected_nodes:
                    labels[nid] = f"output_{ascii_lowercase[i]}"

        for i, nid in enumerate(internal_ids):
            if nid in connected_nodes:
                labels[nid] = f"{ascii_lowercase[i]}"

        return labels

    @classmethod
    def combine_visualizations(cls, visualizations: list[plt.Figure]) -> plt.Figure:
        if not visualizations:
            return None
        return visualizations[0]
