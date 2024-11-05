from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph


class HypergraphManager:

    hypergraphs: list[Hypergraph] = []

    @staticmethod
    def get_graph_by_id(hypergraph_id: int) -> Hypergraph|None:
        for graph in HypergraphManager.hypergraphs:
            if graph.id == hypergraph_id:
                return graph
        return None
