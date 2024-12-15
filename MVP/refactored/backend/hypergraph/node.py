from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge


class Node:
    def __init__(self, node_id: int=None):
        if node_id is None:
            node_id = id(self)
        self.id = node_id
        self.inputs: list[HyperEdge] = []
        self.outputs: list[HyperEdge] = []

    def remove_self(self):
        pass

    def append_input(self, input: HyperEdge):
        self.inputs.append(input)

    def append_output(self, output: HyperEdge):
        self.outputs.append(output)

    def set_inputs(self, inputs: list[HyperEdge]):
        self.inputs = inputs

    def get_inputs(self) -> list[HyperEdge]:
        return self.inputs

    def get_outputs(self) -> list[HyperEdge]:
        return self.outputs

    def remove_input(self, input: HyperEdge):
        if input in self.inputs:
            self.inputs.remove(input)

    def remove_output(self, output: HyperEdge):
        if output in self.outputs:
            self.outputs.remove(output)
