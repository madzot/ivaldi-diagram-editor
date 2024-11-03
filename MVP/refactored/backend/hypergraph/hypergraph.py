from MVP.refactored.backend.hypergraph.node import Node


class Hypergraph(Node):
    """Hypergraph class."""

    def __init__(self, hypergraph_id=None, inputs=None, outputs=None, nodes=None):
        super().__init__(hypergraph_id, inputs, outputs)
        if nodes is None:
            nodes = []
        self.nodes = nodes
        # if not self.is_valid(): TODO
        #     raise ValueError("The hypergraph is not valid.")
        self.set_hypergraph_io()

    def add_node(self, node: Node) -> None:
        if node in self.nodes:
            raise ValueError("Node already exists")
        # if not node.is_valid():
        #     raise ValueError("Node is not valid")
        self.nodes.append(node)
        self.set_hypergraph_io()

    def add_nodes(self, nodes: [Node]) -> None:
        for node in nodes:
            self.add_node(node)

    def get_node(self, node_id: int) -> Node:
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def remove_node(self, node: Node) -> None:
        self.nodes.pop(node)

    def set_hypergraph_io(self) -> None:
        """Define input and output wires for hypergraph."""
        all_inputs = set()
        all_outputs = set()

        for node in self.nodes:
            all_inputs.update(node.inputs)
            all_outputs.update(node.outputs)

        self.inputs = list(all_inputs - all_outputs)
        self.outputs = list(all_outputs - all_inputs)

    def is_valid(self) -> bool:
        """Validate hypergraph structure by checking input/output consistency and cycles."""
        node_inputs = set()
        node_outputs = set()

        for node in self.nodes:
            node_inputs.update(node.inputs)
            node_outputs.update(node.outputs)

        # Check if all node inputs are either in hypergraph inputs or match any node's outputs
        invalid_inputs = node_inputs - set(self.inputs) - node_outputs
        if invalid_inputs:
            return False

        # Check if all node outputs are either in hypergraph outputs or match any node's inputs
        invalid_outputs = node_outputs - set(self.outputs) - node_inputs
        if invalid_outputs:
            return False

        return self.has_no_cycles()

    def has_no_cycles(self) -> bool:
        """Check if the hypergraph has no cycles."""
        explored_nodes = set()
        current_path = set()

        for current_node in self.nodes:
            if current_node not in explored_nodes:
                if not self.depth_first_search(current_node, explored_nodes, current_path):
                    return False
        return True

    def depth_first_search(self, node, visited, current_path) -> bool:
        """Helper function to check if the hypergraph has no cycles, using depth first search."""
        if node in current_path:
            return False
        if node in visited:
            return True

        visited.add(node)
        current_path.add(node)

        for output in node.outputs:
            for other_node in self.nodes:
                if output in other_node.inputs:
                    if not self.depth_first_search(other_node, visited, current_path):
                        return False

        current_path.remove(node)
        return True

    def to_dict(self) -> dict:
        """Return a dictionary representation of the hypergraph."""
        hypergraph_dict = super().to_dict()
        hypergraph_dict["nodes"] = [node.to_dict() for node in self.nodes]
        return hypergraph_dict

    def __str__(self) -> str:
        """Return a string representation of the hypergraph."""
        node_descriptions = [f"Node ID: {node.id}, Inputs: {node.inputs}, Outputs: {node.outputs}" for node in
                             self.nodes]

        # Format the node descriptions into a single string
        nodes_str = "\n".join(node_descriptions)

        return (f"Hypergraph ID: {self.id}\n"
                f"Inputs: {self.inputs}\n"
                f"Outputs: {self.outputs}\n"
                f"Nodes:\n{nodes_str}")


def test_hypergraph_str():
    # Create sample nodes
    node1 = Node(node_id=0, inputs=[0], outputs=[1, 2])
    node2 = Node(node_id=1, inputs=[1], outputs=[3])
    node3 = Node(node_id=2, inputs=[2], outputs=[4])

    # Create a hypergraph
    hypergraph = Hypergraph(hypergraph_id=100, nodes=[node1, node2, node3])
    print(str(hypergraph))
