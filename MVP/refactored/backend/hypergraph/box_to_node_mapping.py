from MVP.refactored.backend.hypergraph.node import Node

class BoxToNodeMapping:
    _box_to_node_mapping: dict[int, Node] = {} # NB! Sometimes instead of box id there will be connection id,
                                                       # because input and output of diagram is also nodes.
    @classmethod
    def add_new_pair(cls, box_id: int, node: Node):
        cls._box_to_node_mapping[box_id] = node

    @classmethod
    def remove_pair(cls, box_id: int):
        if box_id in cls._box_to_node_mapping:
            del cls._box_to_node_mapping[box_id]

    @classmethod
    def get_node_by_box_id(cls, box_id: int) -> Node|None:
        if box_id in cls._box_to_node_mapping:
            return cls._box_to_node_mapping[box_id]
        return None
