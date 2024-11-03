from MVP.refactored.backend.hypergraph.hypergraph_manage import Manage


class BackendNotation:

    def get_all_hypergraph_notations(self) -> str:
        hypergraphs = Manage.hypergraphs
        return "\n\n".join([str(hypergraph) for hypergraph in hypergraphs])
