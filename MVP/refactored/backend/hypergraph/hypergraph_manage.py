from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph


class Manage:
    hypergraphs: list[Hypergraph] = []

    @staticmethod
    def get_graph_by_id(id: int) -> Hypergraph | None:
        for g in HypergraphManager.hypergraphs:
            if g.id == id:
                return g
        return None
