import matplotlib.pyplot as plt
import hypernetx as hnx
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
        # Prepare data for HyperNetX
        edge_dict = {}
        node_roles = {}
        for edge in hypergraph.get_all_hyper_edges():
            source_nodes: list[Node] = edge.get_source_nodes()
            target_nodes: list[Node] = edge.get_target_nodes()

            united_source_nodes: list[Node] = [n for src in source_nodes for n in src.get_united_with_nodes()]
            united_target_nodes: list[Node] = [n for tgt in target_nodes for n in tgt.get_united_with_nodes()]

            all_nodes: list[Node] = set(source_nodes + target_nodes + united_source_nodes + united_target_nodes)

            edge_dict[edge.id] = {node.id for node in all_nodes}

            for node in all_nodes:
                if node not in node_roles:
                    node_roles[node] = set()
                if node in hypergraph.get_hypergraph_source():
                    node_roles[node].add('source')
                if node in hypergraph.get_hypergraph_target():
                    node_roles[node].add('target')

        color_map = {
            frozenset(['source']): 'darkgreen',
            frozenset(['target']): 'red',
            frozenset(['source', 'target']): 'plum',
        }

        node_facecolors = {
            node.id: color_map.get(frozenset(roles), 'black')
            for node, roles in node_roles.items()
        }
        H = hnx.Hypergraph(edge_dict)

        fig, ax = plt.subplots(figsize=(10, 10))
        fig.patch.set_facecolor('white')
        ax.axis('off')

        hnx.draw(H, with_node_labels=True, with_edge_labels=True, ax=ax, nodes_kwargs={"facecolors": node_facecolors})

        plt.title("Hypergraph Visualization (HyperNetX)", fontsize=16, color='black')
        plt.tight_layout()
        return fig

    @classmethod
    def combine_visualizations(cls, visualizations: list[plt.Figure]) -> plt.Figure:
        if not visualizations:
            return None
        return visualizations[0]
