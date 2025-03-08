from MVP.refactored.backend.types.GeneratorType import GeneratorType
from MVP.refactored.backend.types.connection_info import ConnectionInfo


class Generator:
    """Backend representation of frontend box."""
    def __init__(self, id):
        self.id = id
        self.type: GeneratorType = GeneratorType.ATOMIC  # 0-atomic 1-compound None-undefined
        self.left: list[ConnectionInfo] = []
        self.right: list[ConnectionInfo] = []
        self.left_inner: list[ConnectionInfo] = []
        self.right_inner: list[ConnectionInfo] = []
        self.subset = []
        self.parent = None
        self.spiders = []
        self.operand = None

    def add_left(self, left: ConnectionInfo):
        self.left.insert(left.index, left)

    def add_right(self, right: ConnectionInfo):
        self.right.insert(right.index, right)

    def add_left_inner(self, left: ConnectionInfo):
        self.left_inner.insert(left.index, left)

    def add_right_inner(self, right: ConnectionInfo):
        self.right_inner.insert(right.index, right)

    def add_operand(self, operand):
        self.operand = operand

    def remove_operand(self):
        self.operand = None

    def set_id(self, new_id: int):
        self.id = new_id

    def set_type(self, type: GeneratorType):
        self.type = type

    def remove_type(self):
        self.type = None

    def remove_all_left(self):
        for left in self.left:
            left.set_box_id(None)
        self.left.clear()

    def remove_all_right(self):
        for right in self.right:
            right.set_box_id(None)
        self.right.clear()

    def remove_left(self, connection_id: int=None):
        # self.left.pop(connection_id)
        # for i, resource in enumerate(self.left):
        #     resource.index = i
        for connection in self.left:
            if connection.id == connection_id:
                connection.set_box_id(None)
                self.left.remove(connection)
                return

    def remove_right(self, connection_id: int=None):
        # self.right.pop(connection_id)
        # for i, resource in enumerate(self.right):
        #     resource.index = i
        for connection in self.right:
            if connection.id == connection_id:
                connection.set_box_id(None)
                self.right.remove(connection)
                return


    def remove_left_inner(self, connection_id: int=None):
        # self.left_inner.pop(connection_id)
        # for i, resource in enumerate(self.left_inner):
        #     resource.index = i
        for connection in self.left_inner:
            if connection.id == connection_id:
                connection.set_box_id(None)
                self.left_inner.remove(connection)
                return

    def remove_right_inner(self, connection_id: int=None):
        # self.right_inner.pop(connection_id)
        # for i, resource in enumerate(self.right_inner):
        #     resource.index = i
        for connection in self.right_inner:
            if connection.id == connection_id:
                connection.set_box_id(None)
                self.right_inner.remove(connection)
                return

    def remove_left_atomic(self, connection_id: int):
        self.left.pop(connection_id)
        for i, resource in enumerate(self.left):
            resource.index = i

    def remove_right_atomic(self, connection_id: int):
        self.right.pop(connection_id)
        for i, resource in enumerate(self.left):
            resource.index = i

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "left": self.left,
            "right": self.right,
            "left_inner": self.left_inner,
            "right_inner": self.right_inner,
            "operand": self.operand
        }

    @classmethod
    def from_dict(cls, data):
        box = cls(data["id"])
        box.type = data.get("type")
        box.left = data.get("left", [])
        box.right = data.get("right", [])
        box.left_inner = data.get("left_inner", [])
        box.right_inner = data.get("right_inner", [])
        box.operand = data.get("operand")
        return box
