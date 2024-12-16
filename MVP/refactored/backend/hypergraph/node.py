from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge
from typing import Self


class Node:
    def __init__(self, node_id: int=None, is_special=False):
        if node_id is None:
            node_id = id(self)
        self.id = node_id
        self.inputs: list[HyperEdge] = []
        self.outputs: list[HyperEdge] = []
        self.is_special = is_special # if it diagram input/output
        self.is_compound = False # if it is several nodes, for example input/output and wire => two nodes in one, spider and wire.
        self.united_with: list[Node] = []
        # Should be modified that we can determine how each node connected to another

    def remove_self(self):
        pass

    def union(self, other: Self):
        for other_others in other.united_with:
            for current_node_united in self.united_with:
                other_others.united_with.append(current_node_united)
                current_node_united.united_with.append(other_others)
            self.united_with.append(other_others)
            other_others.united_with.append(self)
        self.united_with.append(other)
        other.united_with.append(self)
        # self.is_compound = True
        # if other.is_special:
        #     self.is_special = True
        #
        # other_inputs = other.get_inputs()
        # other_outputs = other.get_outputs()
        # for other_input_hyper_edge in other_inputs:
        #     conn_index = other_input_hyper_edge.get_target_node_connection_index(other)
        #     other_input_hyper_edge.set_target_node(conn_index, self)
        # for other_output_hyper_edge in other_outputs:
        #     conn_index = other_output_hyper_edge.get_source_node_connection_index(other)
        #     other_output_hyper_edge.set_source_node(conn_index, self)
        # self.inputs.extend(other.get_inputs())
        # self.outputs.extend(other.get_outputs())


    def append_input(self, input: HyperEdge):
        if input not in self.inputs:
            self.inputs.append(input)

    def append_output(self, output: HyperEdge):
        if output not in self.outputs:
            self.outputs.append(output)

    def set_inputs(self, inputs: list[HyperEdge]):
        self.inputs = inputs

    def get_inputs(self) -> list[HyperEdge]:
        inputs = []
        inputs.extend(self.inputs)
        for other in self.united_with:
            inputs.extend(other.inputs)
        return inputs

    def get_outputs(self) -> list[HyperEdge]:
        outputs = []
        outputs.extend(self.outputs)
        for other in self.united_with:
            outputs.extend(other.outputs)
        return outputs

    def remove_input(self, input: HyperEdge):
        if input in self.inputs:
            self.inputs.remove(input)

    def remove_output(self, output: HyperEdge):
        if output in self.outputs:
            self.outputs.remove(output)

    def __eq__(self, __value):
        if type(self) == type(__value):
            return self.id == __value.id
        return False

    def __hash__(self):
        return hash(self.id)

