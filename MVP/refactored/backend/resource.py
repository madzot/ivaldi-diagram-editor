from MVP.refactored.backend.types.connection_info import ConnectionInfo


class Resource:
    """Resource is backend representation of wire and spider."""
    def __init__(self, id):
        self.id = id
        self.connections: list[ConnectionInfo] = []
        self.left_connection: list[ConnectionInfo] = []
        self.right_connection: list[ConnectionInfo] = []
        self.spider_connection: list[ConnectionInfo] = []
        self.spider = False
        # self.spider_connection = None
        self.parent = None

    def add_connection(self, connection):
        self.connections.append(connection)

    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)

    def add_left_connection(self, connection):
        if connection not in self.left_connection:
            self.left_connection.append(connection)

    def add_right_connection(self, connection):
        if connection not in self.right_connection:
            self.right_connection.append(connection)

    def add_spider_connection(self, connection):
        if not self.spider:
            if connection not in self.spider_connection:
                self.spider_connection.append(connection)
        else:
            # if resource is spider, all connections have same id as spider
            self.spider_connection.append(connection)

    def get_left_connections(self):
        """Return left connections sorted by index.
        Wire will have only one item in the list
        """
        return sorted(self.left_connection, key=lambda connection: connection.index)

    def get_right_connections(self):
        """Return right connections sorted by index.
        Wire will have only one item in the list
        """
        return sorted(self.right_connection, key=lambda connection: connection.index)

    def get_spider_connections(self):
        return sorted(self.spider_connection, key=lambda connection: connection.index)

    def to_dict(self):
        return {
            "id": self.id,
            "connections": map(lambda c: c.to_list(), self.connections)
        }

    def __eq__(self, other):
        if isinstance(other, Resource):
            return self.id == other.id
        return False

    @classmethod
    def from_dict(cls, data):
        resource = cls(data["id"])
        resource.connections = map(lambda c: ConnectionInfo.from_list(c), data.get("connections"))
        return resource
