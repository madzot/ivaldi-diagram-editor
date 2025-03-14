import logging

from MVP.refactored.backend.types.ActionType import ActionType
from MVP.refactored.backend.types.GeneratorType import GeneratorType
from MVP.refactored.backend.types.connection_info import ConnectionInfo
from MVP.refactored.backend.types.connection_side import ConnectionSide
from MVP.refactored.backend.diagram import Diagram
from MVP.refactored.backend.generator import Generator
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.resource import Resource
from MVP.refactored.frontend.canvas_objects.spider import Spider

logging.basicConfig(level=logging.INFO, format='%(asc_time)s - %(level_name)s - %(message)s')
logger = logging.getLogger(__name__)


class Receiver:
    def __init__(self):
        self.listener = True
        # self.diagram = Diagram()
        self.diagrams: dict[int, Diagram] = {} # key is canvas_id where diagram located
        logger.info("Receiver initialized.")

    def add_new_canvas(self, canvas_id: int):
        self.diagrams[canvas_id] = Diagram()

    def receiver_callback(self, action: ActionType, **kwargs):
        resource_id = kwargs.get('resource_id')
        start_connection: ConnectionInfo|None = kwargs.get('start_connection')
        end_connection: ConnectionInfo|None = kwargs.get('end_connection')
        connection_id = kwargs.get('connection_id')
        generator_id = kwargs.get('generator_id')
        generator_side = kwargs.get('generator_side')
        connection_nr = kwargs.get('connection_nr')
        connection_side: ConnectionSide = kwargs.get('connection_side')
        operator = kwargs.get('operator')
        canvas_id = kwargs.get('canvas_id')
        new_id = kwargs.get('new_id')
        new_canvas_id = kwargs.get('new_canvas_id')
        resource_ids: list[int] = kwargs.get('resource_ids')
        generator_ids: list[int] = kwargs.get('generator_ids')

        logger.info(f"receiver_callback invoked with action: {action}, kwargs: {kwargs}")
        if action == ActionType.WIRE_CREATE:
            new_resource = self.create_new_resource(resource_id, canvas_id)
            self.add_connections_to_resource(new_resource, [start_connection, end_connection], canvas_id)
        elif action == ActionType.WIRE_DELETE:
            self.delete_resource(resource_id, canvas_id)
        elif action == ActionType.SPIDER_CREATE:
            new_resource = self.create_new_resource(resource_id, canvas_id, spider=True)
            new_resource.spider = True
            self.add_connections_to_resource(new_resource, [start_connection, end_connection], canvas_id)
        elif action == ActionType.SPIDER_PARENT_CREATE:
            pass
        elif action == ActionType.SPIDER_DELETE:
            self.delete_resource(resource_id, canvas_id, spider=True)
        elif action == ActionType.BOX_ADD_INNER_LEFT:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.add_left_inner(ConnectionInfo(connection_nr, ConnectionSide.INNER_LEFT, connection_id, box.id))
        elif action == ActionType.BOX_ADD_INNER_RIGHT:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.add_right_inner(ConnectionInfo(connection_nr, ConnectionSide.INNER_RIGHT, connection_id, box.id))
        elif action == ActionType.BOX_REMOVE_INNER_LEFT:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.remove_left_inner(connection_id)
        elif action == ActionType.BOX_REMOVE_INNER_RIGHT:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.remove_right_inner(connection_id)
        elif action == ActionType.BOX_ADD_LEFT:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.add_left(ConnectionInfo(connection_nr, ConnectionSide.LEFT, connection_id, box.id))
        elif action == ActionType.BOX_ADD_RIGHT:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.add_right(ConnectionInfo(connection_nr, ConnectionSide.RIGHT, connection_id, box.id))
        elif action == ActionType.BOX_REMOVE_LEFT:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.remove_left(connection_id)
        elif action == ActionType.BOX_REMOVE_RIGHT:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.remove_right(connection_id)
        elif action == ActionType.BOX_REMOVE_ALL_CONNECTIONS:
            box = self.get_generator_by_id(generator_id, canvas_id)
            # TODO handle inner connections
            box.remove_all_right()
            box.remove_all_left()
        elif action == ActionType.BOX_CREATE:
            self.create_new_generator(generator_id, canvas_id)
        elif action == ActionType.BOX_DELETE:
            self.delete_generator(generator_id, canvas_id)
        elif action == ActionType.BOX_COMPOUND:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.set_type(GeneratorType.COMPOUND)
        elif action == ActionType.BOX_ATOMIC:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.set_type(GeneratorType.ATOMIC)
        elif action == ActionType.BOX_SUB_BOX:
            pass
        elif action == ActionType.BOX_ADD_OPERATOR:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.add_operand(operator)
        elif action == ActionType.BOX_SWAP_ID:
            box = self.get_generator_by_id(generator_id, canvas_id)
            box.set_id(new_id)
        elif action == ActionType.BOX_SWAP_CONNECTION_ID:
            pass # in original diagram callback that events is not in use. In project there no occurrences for this event
        elif action == ActionType.DIAGRAM_ADD_INPUT:
            self.diagrams[canvas_id].add_input(ConnectionInfo(connection_nr, connection_side, connection_id, None))
        elif action == ActionType.DIAGRAM_ADD_OUTPUT:
            self.diagrams[canvas_id].add_output(ConnectionInfo(connection_nr, connection_side, connection_id, None))
        elif action == ActionType.DIAGRAM_REMOVE_INPUT:
            self.diagrams[canvas_id].remove_input(connection_id)
        elif action == ActionType.DIAGRAM_REMOVE_OUTPUT:
            self.diagrams[canvas_id].remove_output(connection_id)
        elif action == ActionType.SUB_DIAGRAM_CREATE:
            generators = self.get_generators_by_ids(generator_ids, canvas_id)
            resources = self.get_resources_by_ids(resource_ids, canvas_id)
            spider_ids = []
            spiders = self.get_spiders_by_ids(spider_ids, canvas_id) # TODO

            diagram = self.diagrams[canvas_id]
            new_diagram = Diagram()

            diagram.remove_boxes(generators)
            diagram.remove_spiders(resources)
            diagram.remove_resources(resources)
            diagram.add_sub_diagram(new_diagram)

            new_diagram.add_input(...)
            new_diagram.add_output(...)
            new_diagram.add_boxes(generators)
            new_diagram.add_spiders(resources)
            new_diagram.add_resources(resources)

        print("All")

    def spider_callback(self, action: str, **kwargs):
        pass

    def wire_callback(self, action: str, **kwargs):
        pass

    def box_callback(self, action: str, **kwargs):
        pass

    def create_new_resource(self, id: int, canvas_id: int, spider: bool=False) -> Resource:
        resource = Resource(id)
        if spider:
            self.diagrams[canvas_id].add_spider(resource)
        else:
            self.diagrams[canvas_id].add_resource(resource)
        return resource

    def delete_resource(self, id: int, canvas_id: int, spider: bool=False):
        if spider:
            self.diagrams[canvas_id].remove_spider_by_id(id)
        else:
            self.diagrams[canvas_id].remove_resource_by_id(id)

    def add_connections_to_resource(self, resource: Resource, connections: list[ConnectionInfo|None], canvas_id: int):
        for connection in connections:
            if connection is None: continue

            if connection.side == ConnectionSide.LEFT:
                if connection.has_box():
                    box = self.get_generator_by_id(connection.get_box_id(), canvas_id)
                    resource.add_left_connection(box.get_left_by_id(connection.get_id())) # We don`t simply add connection from loop (connection in connection),
                    # because we want that box(or input/output) connection and wire connection will be the same object,
                    # if we use from frontend connection they will differ.
                else: # it is output
                    output = self.get_output_by_id(connection.get_id(), canvas_id)
                    resource.add_left_connection(output)
            elif connection.side == ConnectionSide.RIGHT:
                if connection.has_box():
                    box = self.get_generator_by_id(connection.get_box_id(), canvas_id)
                    resource.add_right_connection(box.get_right_by_id(connection.get_id()))
                else: # it is input
                    input = self.get_input_by_id(connection.get_id(), canvas_id)
                    resource.add_right_connection(input)
            elif connection.side == ConnectionSide.SPIDER:
                spider = self.get_spider_by_id(connection.get_id(), canvas_id)
                connection.index = len(spider.get_spider_connections()) # we use here that rule, that when we add wire to spider
                # it always appends to the last connection
                spider.add_spider_connection(connection)
                resource.add_spider_connection(connection)

    def create_new_generator(self, box_id: int, canvas_id: int) -> Generator:
        box = Generator(box_id)
        self.diagrams[canvas_id].add_box(box)
        return box

    def delete_generator(self, box_id: int, canvas_id: int):
        self.diagrams[canvas_id].remove_box_by_id(box_id)

    def get_generator_by_id(self, box_id: int, canvas_id: int) -> Generator:
        return self.diagrams[canvas_id].get_generator_by_id(box_id)

    def get_generators_by_ids(self, generator_ids: list[int], canvas_id: int) -> list[Generator]:
        generators: list[Generator] = []
        for generator_id in generator_ids:
            generators.append(self.get_generator_by_id(generator_id, canvas_id))
        return generators

    def get_input_by_id(self, id: int, canvas_id: int) -> ConnectionInfo:
        return self.diagrams[canvas_id].get_input_by_id(id)

    def get_output_by_id(self, id: int, canvas_id: int) -> ConnectionInfo:
        return self.diagrams[canvas_id].get_output_by_id(id)

    def get_resource_by_id(self, resource_id: int, canvas_id: int) -> Resource:
        return self.diagrams[canvas_id].get_resource_by_id(resource_id)

    def get_resources_by_ids(self, resource_ids: list[int], canvas_id: int) -> list[Resource]:
        resources: list[Resource] = []
        for resource_id in resource_ids:
            resources.append(self.get_resource_by_id(resource_id, canvas_id))
        return resources

    def get_spider_by_id(self, spider_id: int, canvas_id: int) -> Resource:
        return self.diagrams[canvas_id].get_spider_by_id(spider_id)

    def get_spiders_by_ids(self, spider_ids: list[int], canvas_id: int) -> list[Resource]:
        resources: list[Resource] = []
        for resource_id in spider_ids:
            resources.append(self.get_spider_by_id(resource_id, canvas_id))
        return resources