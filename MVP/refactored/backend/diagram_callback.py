import logging

from MVP.refactored.backend.types.ActionType import ActionType
from MVP.refactored.backend.types.GeneratorType import GeneratorType
from MVP.refactored.backend.types.connection_info import ConnectionInfo
from MVP.refactored.backend.types.connection_side import ConnectionSide
from MVP.refactored.backend.diagram import Diagram
from MVP.refactored.backend.generator import Generator
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.resource import Resource

logging.basicConfig(level=logging.INFO, format='%(asc_time)s - %(level_name)s - %(message)s')
logger = logging.getLogger(__name__)


class Receiver:
    def __init__(self):
        self.listener = True
        self.diagram = Diagram()
        self.diagrams: dict[int, Diagram] = {} # key is canvas_id where diagram located
        logger.info("Receiver initialized.")

    def receiver_callback(self, action: ActionType, **kwargs):
        resource_id = kwargs.get('resource_id')
        start_connection: ConnectionInfo|None = kwargs.get('start_connection')
        end_connection: ConnectionInfo|None = kwargs.get('end_connection')
        connection_id = kwargs.get('connection_id')
        generator_id = kwargs.get('generator_id')
        generator_side = kwargs.get('generator_side')
        connection_nr = kwargs.get('connection_nr')
        operator = kwargs.get('operator')
        canvas_id = kwargs.get('canvas_id')
        new_id = kwargs.get('new_id')

        logger.info(f"receiver_callback invoked with action: {action}, kwargs: {kwargs}")
        if action == ActionType.WIRE_CREATE:
            new_resource = self.create_new_resource(resource_id, canvas_id)
            self.add_connections_to_resource(new_resource, [start_connection, end_connection])
        elif action == ActionType.WIRE_DELETE:
            self.delete_resource(resource_id, canvas_id)
        elif action == ActionType.SPIDER_CREATE:
            new_resource = self.create_new_resource(resource_id, canvas_id)
            new_resource.spider = True
            self.add_connections_to_resource(new_resource, [start_connection, end_connection])
        elif action == ActionType.SPIDER_PARENT_CREATE:
            pass
        elif action == ActionType.SPIDER_DELETE:
            self.delete_resource(resource_id, canvas_id)
        elif action == ActionType.BOX_ADD_INNER_LEFT:
            box = self.generator_get_box_by_id(generator_id, canvas_id)
            box.add_left_inner(ConnectionInfo(connection_nr, ConnectionSide.LEFT, connection_id, box.id))
        elif action == ActionType.BOX_ADD_INNER_RIGHT:
            box = self.generator_get_box_by_id(generator_id, canvas_id)
            box.add_right_inner(ConnectionInfo(connection_nr, ConnectionSide.RIGHT, connection_id, box.id))
        elif action == ActionType.BOX_REMOVE_INNER_LEFT:
            box = self.generator_get_box_by_id(generator_id, canvas_id)
            box.remove_left_inner(connection_id)
        elif action == ActionType.BOX_REMOVE_INNER_RIGHT:
            box = self.generator_get_box_by_id(generator_id, canvas_id)
            box.remove_right_inner(connection_id)
        elif action == ActionType.BOX_ADD_LEFT:
            box = self.generator_get_box_by_id(generator_id, canvas_id)
            box.add_left(ConnectionInfo(connection_nr, ConnectionSide.LEFT, connection_id, box.id))
        elif action == ActionType.BOX_ADD_RIGHT:
            box = self.generator_get_box_by_id(generator_id, canvas_id)
            box.add_right(ConnectionInfo(connection_nr, ConnectionSide.RIGHT, connection_id, box.id))
        elif action == ActionType.BOX_REMOVE_LEFT:
            box = self.generator_get_box_by_id(generator_id, canvas_id)
            box.remove_left(connection_id)
        elif action == ActionType.BOX_REMOVE_RIGHT:
            box = self.generator_get_box_by_id(generator_id, canvas_id)
            box.remove_right(connection_id)
        elif action == ActionType.BOX_REMOVE_ALL_CONNECTIONS:
            box = self.generator_get_box_by_id(generator_id, canvas_id)
            # TODO handle inner connections
            box.remove_all_right()
            box.remove_all_left()
        elif action == ActionType.BOX_CREATE:
            self.create_new_generator(generator_id, canvas_id)
        elif action == ActionType.BOX_DELETE:
            self.delete_generator(generator_id, canvas_id)
        elif action == ActionType.BOX_COMPOUND:
            box = self.generator_get_box_by_id(generator_id, canvas_id)
            box.set_type(GeneratorType.COMPOUND)
        elif action == ActionType.BOX_ATOMIC:
            box = self.generator_get_box_by_id(generator_id, canvas_id)
            box.set_type(GeneratorType.ATOMIC)
        elif action == ActionType.BOX_SUB_BOX:
            pass
        elif action == ActionType.BOX_ADD_OPERATOR:
            box = self.generator_get_box_by_id(generator_id, canvas_id)
            box.add_operand(operator)
        elif action == ActionType.BOX_SWAP_ID:
            box = self.generator_get_box_by_id(generator_id, canvas_id)
            box.set_id(new_id)
        elif action == ActionType.BOX_SWAP_CONNECTION_ID:
            pass # in original diagram callback that events is not in use. In project there no occurrences for this event
        elif action == ActionType.DIAGRAM_ADD_INPUT:
            self.diagrams[canvas_id].add_input(ConnectionInfo(connection_nr, ConnectionSide.LEFT, connection_id, None))
        elif action == ActionType.DIAGRAM_ADD_OUTPUT:
            self.diagrams[canvas_id].add_output(ConnectionInfo(connection_nr, ConnectionSide.RIGHT, connection_id, None))
        elif action == ActionType.DIAGRAM_REMOVE_INPUT:
            self.diagrams[canvas_id].remove_input(connection_id)
        elif action == ActionType.DIAGRAM_REMOVE_OUTPUT:
            self.diagrams[canvas_id].remove_output(connection_id)

    def spider_callback(self, action: str, **kwargs):
        pass
    def wire_callback(self, action: str, **kwargs):
        pass
    def box_callback(self, action: str, **kwargs):
        pass

    def create_new_resource(self, id: int, canvas_id: int) -> Resource:
        resource = Resource(id)
        self.diagrams[canvas_id].add_resource(resource)
        return resource

    def delete_resource(self, id: int, canvas_id: int):
        self.diagrams[canvas_id].remove_resource_by_id(id)

    @staticmethod
    def add_connections_to_resource(resource: Resource, connections: list[ConnectionInfo|None]):
        for connection in connections:
            if connection is None: continue
            if connection.side == ConnectionSide.LEFT:
                resource.add_left_connection(connection)
            else:
                resource.add_right_connection(connection)

    def create_new_generator(self, box_id: int, canvas_id: int) -> Generator:
        box = Generator(box_id)
        self.diagrams[canvas_id].add_box(box)
        return box

    def delete_generator(self, box_id: int, canvas_id: int):
        self.diagrams[canvas_id].remove_box_by_id(box_id)

    def wire_get_resource_by_id(self, resource_id: int, canvas_id: int):
        return next((r for r in self.diagrams[canvas_id].resources if r.id == resource_id), None)

    def generator_get_box_by_id(self, box_id: int, canvas_id: int) -> Generator:
        return next((b for b in self.diagrams[canvas_id].boxes if b.id == box_id), None)

    def spider_get_resource_by_connection_id(self, spider_id: int, canvas_id: int):
        return next((b for b in self.diagrams[canvas_id].spiders if b.id == spider_id), None)
