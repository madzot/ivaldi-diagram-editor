from MVP.refactored.backend.connection_side import ConnectionSide

from typing import Self

class ConnectionInfo:
    def __init__(self, connection_index: int, connection_side: ConnectionSide, connection_id: int, related_box_id: int=None):
        self.index = connection_index
        self.box_id = related_box_id
        self.side = connection_side
        self.id = connection_id

    def has_box(self)-> bool:
        return self.box_id is not None

    def to_list(self)-> list:
        return [self.index, self.box_id, self.side, self.id]

    @classmethod
    def from_list(cls, data)-> Self:
        return ConnectionInfo(data[0], data[2], data[3], data[1])