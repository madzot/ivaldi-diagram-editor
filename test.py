import networkx as nx
from networkx import NetworkXException
import matplotlib.pyplot as plt
from collections import defaultdict

test_hypergraph = {
    'nodes': ['a', 'b', 'c', 'd', 'e'],
    'edges': [
        ('a', 'c'),
        ('a', 'b', 'd'),
        ('c', 'e', 'd'),
    ]
}


def decompose_edges_by_len(hypergraph):
    decomposed_edges = defaultdict(list)
    for edge in hypergraph['edges']:
        decomposed_edges[len(edge)].append(edge)
    decomposition = {
        'nodes': hypergraph['nodes'],
        'edges': decomposed_edges
    }
    return decomposition


def get_node_color_and_size(node):
    if isinstance(node, tuple):  # Star-expanded hyperedge
        return '#d62828', 150
    if isinstance(node, str) and node.startswith("spider"):
        return '#fcbf49', 500
    if isinstance(node, str) and node.startswith("wire"):
        return '#eae2b7', 100
    return '#f77f00', 300  # Default: I/O

def plot_hypergraph_combined(hypergraph):
    decomposed = decompose_edges_by_len(hypergraph)
    decomposed_edges = decomposed['edges']
    nodes = decomposed['nodes']

    g = nx.DiGraph()
    g.add_nodes_from(nodes)

    for edge_order, edges in decomposed_edges.items():
        if edge_order == 2:
            g.add_edges_from(edges)
        else:
            for edge in edges:
                hypernode = tuple(edge)
                g.add_node(hypernode)
                for node in edge:
                    g.add_edge(node, hypernode)

    try:
        pos = nx.kamada_kawai_layout(g)
    except NetworkXException:
        pos = nx.spring_layout(g)

    fig, ax = plt.subplots(figsize=(10, 10))
    fig.patch.set_facecolor('#003049')
    ax.axis('off')

    for node in g.nodes():
        color, size = get_node_color_and_size(node)
        nx.draw_networkx_nodes(g, pos,
                               nodelist=[node],
                               node_color=color,
                               node_size=size,
                               ax=ax)

    nx.draw_networkx_edges(g, pos,
                           ax=ax,
                           edge_color='#8ecae6',
                           connectionstyle='arc3,rad=0.05',
                           arrows=False)

    labels = {node: str(node) for node in nodes if not isinstance(node, tuple)}
    nx.draw_networkx_labels(g, pos, labels=labels,
                            ax=ax, font_color='white', font_size=10)

    plt.title("All Hyperedges Combined", fontsize=16, color='white')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # Plot the hypergraph components
    plot_hypergraph_combined(test_hypergraph)
    plt.show()
    print(decompose_edges_by_len(test_hypergraph))
