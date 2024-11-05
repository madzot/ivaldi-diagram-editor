from MVP.refactored.backend.hypergraph.hypergraph_manage import HypergraphManager


class BackendNotation:

    def get_all_hypergraph_notations(self) -> str:
        hypergraphs = HypergraphManager.hypergraphs
        return "\n\n".join([str(hypergraph) for hypergraph in hypergraphs])
