from MVP.refactored.backend.hypergraph.node import Node

class WireAndSpiderToNodeMapping:
    _wire_Spider_to_node_mapping: dict[int, Node] = {}
    @classmethod
    def add_new_pair(cls, wire_or_spider_id: int, node: Node):
        cls._wire_Spider_to_node_mapping[wire_or_spider_id] = node

    @classmethod
    def remove_pair(cls, wire_or_spider_id: int):
        if wire_or_spider_id in cls._wire_Spider_to_node_mapping:
            del cls._wire_Spider_to_node_mapping[wire_or_spider_id]

    @classmethod
    def get_node_by_wire_or_spider_id(cls, wire_or_spider_id: int) -> Node | None:
        if wire_or_spider_id in cls._wire_Spider_to_node_mapping:
            return cls._wire_Spider_to_node_mapping[wire_or_spider_id]
        return None
