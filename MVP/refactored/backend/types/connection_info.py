from MVP.refactored.backend.types.connection_side import ConnectionSide

from typing import Self

class ConnectionInfo:
    def __init__(self, connection_index: int, connection_side: ConnectionSide, connection_id: int, related_box_id: int=None):
        self.index = connection_index
        self.box_id = related_box_id
        self.side = connection_side
        self.id = connection_id

    def get_id(self) -> int:
        return self.id

    def has_box(self)-> bool:
        return self.box_id is not None

    def get_box_id(self)-> int:
        return self.box_id

    def set_box_id(self, id: int|None):
        self.box_id = id

    def to_list(self)-> list:
        return [self.index, self.box_id, self.side, self.id]

    def is_all_fields_exists(self) -> bool:
        return self.index is not None and self.box_id is not None and self.side is not None and self.id is not None

    @classmethod
    def from_list(cls, data)-> Self:
        return ConnectionInfo(data[0], data[2], data[3], data[1])

    def __eq__(self, __value):
        return isinstance(__value, ConnectionInfo) and self.id == __value.id

