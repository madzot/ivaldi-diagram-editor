from MVP.refactored.backend.connection_info import ConnectionInfo


class Resource:
    """Resource is backend representation of wire and spider."""
    def __init__(self, id):
        self.id = id
        self.connections: list[ConnectionInfo] = []
        self.spider = False
        self.spider_connection = None
        self.parent = None

    def add_connection(self, connection):
        self.connections.append(connection)

    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)

    def to_dict(self):
        return {
            "id": self.id,
            "connections": map(lambda c: c.to_list(), self.connections)
        }

    @classmethod
    def from_dict(cls, data):
        resource = cls(data["id"])
        resource.connections = map(lambda c: ConnectionInfo.from_list(c), data.get("connections"))
        return resource
