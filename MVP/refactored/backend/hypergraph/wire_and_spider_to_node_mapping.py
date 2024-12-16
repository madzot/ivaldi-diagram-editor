from collections import defaultdict

from MVP.refactored.backend.hypergraph.node import Node

class WireAndSpiderToNodeMapping:
    _wire_Spider_to_node_mapping: dict[int, Node] = {}
    _node_to_wire_spider_mapping: dict[Node, set[int]] = defaultdict(set)
    @classmethod
    def add_new_pair(cls, wire_or_spider_id: int, node: Node):
        cls._wire_Spider_to_node_mapping[wire_or_spider_id] = node
        cls._node_to_wire_spider_mapping[node].add(wire_or_spider_id)

    @classmethod
    def remove_pair(cls, wire_or_spider_id: int):
        if wire_or_spider_id in cls._wire_Spider_to_node_mapping:
            node = cls._wire_Spider_to_node_mapping[wire_or_spider_id]
            cls._node_to_wire_spider_mapping[node].remove(wire_or_spider_id)
            if not cls._node_to_wire_spider_mapping[node]:
                del cls._node_to_wire_spider_mapping[node]


    @classmethod
    def get_node_by_wire_or_spider_id(cls, wire_or_spider_id: int) -> Node | None:
        if wire_or_spider_id in cls._wire_Spider_to_node_mapping:
            return cls._wire_Spider_to_node_mapping[wire_or_spider_id]
        return None
