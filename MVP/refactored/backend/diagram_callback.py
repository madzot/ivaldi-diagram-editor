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
            new_resource = self.create_new_resource(resource_id)
            self.add_connections_to_resource(new_resource, [start_connection, end_connection])
        elif action == ActionType.WIRE_DELETE:
            self.delete_resource(resource_id)
        elif action == ActionType.SPIDER_CREATE:
            new_resource = self.create_new_resource(resource_id)
            new_resource.spider = True
            self.add_connections_to_resource(new_resource, [start_connection, end_connection])
        elif action == ActionType.SPIDER_PARENT_CREATE:
            pass
        elif action == ActionType.SPIDER_DELETE:
            self.delete_resource(resource_id)
        elif action == ActionType.BOX_ADD_INNER_LEFT:
            pass
        elif action == ActionType.BOX_ADD_INNER_RIGHT:
            pass
        elif action == ActionType.BOX_REMOVE_INNER_LEFT:
            pass
        elif action == ActionType.BOX_REMOVE_INNER_RIGHT:
            pass
        elif action == ActionType.BOX_ADD_LEFT:
            pass
        elif action == ActionType.BOX_ADD_RIGHT:
            pass
        elif action == ActionType.BOX_REMOVE_LEFT:
            pass
        elif action == ActionType.BOX_REMOVE_RIGHT:
            pass
        elif action == ActionType.BOX_REMOVE_ALL_CONNECTIONS:
            pass
        elif action == ActionType.BOX_CREATE:
            self.create_new_generator(generator_id)
        elif action == ActionType.BOX_DELETE:
            self.delete_generator(generator_id)
        elif action == ActionType.BOX_COMPOUND:
            box = self.generator_get_box_by_id(generator_id)
            box.set_type(GeneratorType.COMPOUND)
        elif action == ActionType.BOX_ATOMIC:
            box = self.generator_get_box_by_id(generator_id)
            box.set_type(GeneratorType.ATOMIC)
        elif action == ActionType.BOX_SUB_BOX:
            pass
        elif action == ActionType.BOX_ADD_OPERATOR:
            box = self.generator_get_box_by_id(generator_id)
            box.add_operand(operator)
        elif action == ActionType.BOX_SWAP_ID:
            box = self.generator_get_box_by_id(generator_id)
            box.set_id(new_id)
        elif action == ActionType.BOX_SWAP_CONNECTION_ID:
            pass
        elif action == ActionType.DIAGRAM_ADD_INPUT:
            pass
        elif action == ActionType.DIAGRAM_ADD_OUTPUT:
            pass
        elif action == ActionType.DIAGRAM_REMOVE_INPUT:
            pass
        elif action == ActionType.DIAGRAM_REMOVE_OUTPUT:
            pass

    def spider_callback(self, action: str, **kwargs):
        pass
    def wire_callback(self, action: str, **kwargs):
        pass
    def box_callback(self, action: str, **kwargs):
        pass

    def create_new_resource(self, id: int) -> Resource:
        resource = Resource(id)
        self.diagram.add_resource(resource)
        return resource

    def delete_resource(self, id: int):
        self.diagram.remove_resource_by_id(id)

    @staticmethod
    def add_connections_to_resource(resource: Resource, connections: list[ConnectionInfo|None]):
        for connection in connections:
            if connection is None: continue
            if connection.side == ConnectionSide.LEFT:
                resource.add_left_connection(connection)
            else:
                resource.add_right_connection(connection)

    def create_new_generator(self, box_id: int) -> Generator:
        box = Generator(box_id)
        self.diagram.add_box(box)
        return box

    def delete_generator(self, box_id: int):
        self.diagram.remove_box_by_id(box_id)

    def wire_get_resource_by_id(self, resource_id):
        return next((r for r in self.diagram.resources if r.id == resource_id), None)

    def generator_get_box_by_id(self, box_id) -> Generator:
        return next((b for b in self.diagram.boxes if b.id == box_id), None)

    def spider_get_resource_by_connection_id(self, spider_id):
        return next((b for b in self.diagram.spiders if b.id == spider_id), None)
