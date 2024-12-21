from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge

class BoxToHyperEdgeMapping:
    _box_to_hyper_edge_mapping: dict[int, HyperEdge] = {}

    @classmethod
    def add_new_pair(cls, box_id: int, hyper_edge: HyperEdge):
        cls._box_to_hyper_edge_mapping[box_id] = hyper_edge

    @classmethod
    def remove_pair(cls, box_id: int):
        if box_id in cls._box_to_hyper_edge_mapping:
            del cls._box_to_hyper_edge_mapping[box_id]

    @classmethod
    def get_hyper_edge_by_box_id(cls, box_id: int) -> HyperEdge | None:
        if box_id in cls._box_to_hyper_edge_mapping:
            return cls._box_to_hyper_edge_mapping[box_id]
        return None
