import logging

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

    def receiver_callback(self, action, **kwargs):
        return
        wire_id = kwargs.get('wire_id')
        start_connection: ConnectionInfo|None = kwargs.get('start_connection')
        end_connection: ConnectionInfo|None = kwargs.get('end_connection')
        connection_id = kwargs.get('connection_id')
        generator_id = kwargs.get('generator_id')
        generator_side = kwargs.get('generator_side')
        connection_nr = kwargs.get('connection_nr')
        operator = kwargs.get('operator')
        canvas_id = kwargs.get('canvas_id')

        logger.info(f"receiver_callback invoked with action: {action}, kwargs: {kwargs}")
        if action in ['wire_add', 'wire_delete']:
            logger.info(f"Routing to wire_callback with action: {action}")
            self.wire_callback(wire_id, action, start_connection, connection_id, end_connection, canvas_id)
        elif action == 'create_spider':
            logger.info("Routing to create_spider")
            self.create_spider(wire_id, connection_id, generator_id, canvas_id)
        elif action == "create_spider_parent":
            self.spider_parent(wire_id, generator_id, canvas_id)
        elif action == 'delete_spider':
            logger.info("Routing to create_spider")
            self.delete_spider_be(wire_id)
        else:
            logger.info("Routing to box_callback")
            self.box_callback(generator_id, action, connection_id, generator_side, connection_nr, operator, canvas_id)

    def delete_spider_be(self, wire_id):
        logger.info(f"Routing to delete_spider")
        spider = self.spider_get_resource_by_connection_id(wire_id)
        if spider.parent:
            parent = self.generator_get_box_by_id(spider.parent)
            parent.spiders.remove(wire_id)
        self.wire_handle_delete_resource(spider)

        HypergraphManager.remove_node(spider.id)

    def spider_parent(self, spider_id, generator_id=None, canvas_id=None):
        spider = self.spider_get_resource_by_connection_id(spider_id)
        spider.parent = generator_id
        parent = self.generator_get_box_by_id(generator_id)
        parent.spiders.append(spider.id)

    def create_spider(self, spider_id, connection_id, generator_id=None, canvas_id=None):
        logger.info(f"Creating spider with id: {spider_id}")
        resource = Resource(spider_id)
        resource.spider = True
        resource.spider_connection = connection_id
        if generator_id:
            resource.parent = generator_id
            parent = self.generator_get_box_by_id(generator_id)
            parent.spiders.append(resource.id)
        # self.diagram.add_resource(resource)
        self.diagram.spiders.append(resource)
        logger.info(f"Spider created and added to diagram: {resource}")

        HypergraphManager.create_new_node(spider_id, canvas_id=canvas_id)

    def wire_callback(self, wire_id, action=None, start_connection: ConnectionInfo=None,
                      connection_id=None, end_connection: ConnectionInfo=None,
                      canvas_id=None):
        logger.info(
            f"wire_callback invoked with wire_id: {wire_id}, action: {action}, start_connection: {start_connection}, connection_id: {connection_id}")
        if action == 'wire_delete':
            if start_connection and start_connection.side == ConnectionSide.SPIDER:
                spider = self.spider_get_resource_by_connection_id(start_connection.id)
                spider.remove_connection(start_connection)
            elif end_connection and end_connection.side == ConnectionSide.SPIDER:
                spider = self.spider_get_resource_by_connection_id(end_connection.id)
                spider.remove_connection(end_connection)
            else:
                resource = self.wire_get_resource_by_id(wire_id)
                self.wire_handle_delete_resource(resource)

            HypergraphManager.remove_node(wire_id)
        else:
            if end_connection:  # HAS end_connection if connection between spider and something
                if start_connection.side == ConnectionSide.SPIDER:
                    spider = self.spider_get_resource_by_connection_id(connection_id)
                    spider.add_connection(end_connection)
                    box = self.generator_get_box_by_id(end_connection.box_id)
                    if box:
                        if box.type != 1:
                            self.wire_add_to_atomic_box(end_connection.index, box, end_connection.side, spider.id)
                        else:
                            self.wire_add_to_compound_box(spider.id, end_connection.index, box, connection_id)

                    new_node = HypergraphManager.create_new_node(wire_id, canvas_id)
                    HypergraphManager.union_nodes(new_node, spider.id) # unite wire and spider to one node
                    if box:
                        if end_connection.side == ConnectionSide.LEFT:
                            HypergraphManager.connect_node_with_output_hyper_edge(new_node, box.id)
                        elif end_connection.side == ConnectionSide.RIGHT:
                            HypergraphManager.connect_node_with_input_hyper_edge(new_node, box.id)
                    else: # connection to spider
                        HypergraphManager.union_nodes(new_node, end_connection.id)
                    print(f"Added wire - {wire_id}")

                elif end_connection.side == ConnectionSide.SPIDER:
                    spider = self.spider_get_resource_by_connection_id(connection_id)
                    spider.add_connection(start_connection)
                    box = self.generator_get_box_by_id(start_connection.box_id)
                    if box:
                        if box.type != 1:
                            self.wire_add_to_atomic_box(start_connection.id, box, start_connection.side, spider.id)
                        else:
                            self.wire_add_to_compound_box(spider.id, start_connection.id, box, connection_id)

                    new_node = HypergraphManager.create_new_node(wire_id, canvas_id)
                    HypergraphManager.union_nodes(new_node, spider.id)  # unite wire and spider to one node
                    if box:
                        if start_connection.side == ConnectionSide.LEFT:
                            HypergraphManager.connect_node_with_output_hyper_edge(new_node, box.id)
                        elif start_connection.side == ConnectionSide.RIGHT:
                            HypergraphManager.connect_node_with_input_hyper_edge(new_node, box.id)
                    else:  # connection to spider
                        HypergraphManager.union_nodes(new_node, start_connection.id)
            else:  # if it connection not between spider and smt
                resource: Resource = self.wire_get_resource_by_id(wire_id)
                if resource:
                    self.wire_handle_resource_action(resource, wire_id, start_connection.index, start_connection.box_id,
                                                     start_connection.side,
                                                     connection_id)


                    new_node = HypergraphManager.create_new_node(resource.id, canvas_id)
                    for connection in resource.connections:
                        if connection.has_box(): # connection with box(hyper edge)
                            if connection.side == ConnectionSide.LEFT:
                                HypergraphManager.connect_node_with_output_hyper_edge(new_node, connection.box_id)
                            elif connection.side == ConnectionSide.RIGHT:
                                HypergraphManager.connect_node_with_input_hyper_edge(new_node, connection.box_id)
                        else: # connection with diagram input/output
                            HypergraphManager.union_nodes(new_node, connection.id)

                else:
                    resource = self.wire_create_new_resource(wire_id, start_connection.index,
                                                             start_connection.box_id, start_connection.side,connection_id)

        logger.info(f"Resources: {self.diagram.resources}")
        logger.info(f"Spiders: {self.diagram.spiders}")
        logger.info(f"Number of Resources: {len(self.diagram.resources)}")
        logger.info(f"Overall input and output: {self.diagram.input} and {self.diagram.output}")

    def spider_handle_delete_connection(self, spider, side: ConnectionSide):
        if spider:
            for connection in list(spider.connections):
                if connection.side == side:
                    spider.connections.remove(connection)

    def wire_handle_delete_resource(self, resource: Resource):
        """Establish inner removal for connection."""
        if resource:
            if resource.connections:
                for associated_connection in resource.connections:
                    connection_nr = associated_connection.index
                    box_id = associated_connection.box_id
                    connection_side: ConnectionSide = associated_connection.side
                    box = self.generator_get_box_by_id(box_id)
                    if box:
                        if box.type == 1:
                            connection_id = associated_connection.id
                            for con in box.left:
                                if connection_id in con:
                                    box.left[connection_nr] = ConnectionInfo(connection_nr, None, connection_id, box_id)
                            for con in box.right:
                                if connection_id in con:
                                    box.right[connection_nr] = ConnectionInfo(connection_nr, None, connection_id, box_id)
                            for con in box.left_inner:
                                if connection_id in con:
                                    box.left_inner[connection_nr] = ConnectionInfo(connection_nr, None, connection_id, box_id)
                            for con in box.right_inner:
                                if connection_id in con:
                                    box.right_inner[connection_nr] = ConnectionInfo(connection_nr, None, connection_id, box_id)
                        else:
                            if connection_side == ConnectionSide.LEFT:
                                box.left[connection_nr] = ConnectionInfo(connection_nr, None, None, box_id)
                            else:
                                box.right[connection_nr] = ConnectionInfo(connection_nr, None, None, box_id)
                    else:  # Case of None when dealing with diagram input and outputs
                        if connection_side == ConnectionSide.LEFT:
                            self.diagram.output[connection_nr] = ConnectionInfo(connection_nr, None, None, box_id)
                        else:
                            self.diagram.input[connection_nr] = ConnectionInfo(connection_nr, None, None, box_id)

            self.diagram.remove_resource(resource)
            logger.warning(f"Resource with id {resource.id} removed.")
        else:
            logger.warning(f"Resource with id not found.")

    def wire_main_input_output(self, connection_nr, connection_box_id, connection_side, resource_id):
        logger.info(f"Handling main input/output wiring with id: {resource_id}")
        if connection_side == 'left':
            temp = [connection_nr, connection_box_id] + [resource_id]
            self.diagram.output[connection_nr] = temp
        else:
            temp = [connection_nr, connection_box_id] + [resource_id]
            self.diagram.input[connection_nr] = temp

    def wire_add_to_atomic_box(self, connection_nr, box, connection_side, resource_id):
        logger.info(f"Adding connection to atomic box: {box.id}, side: {connection_side}, id: {resource_id}, nr {connection_nr}")
        if connection_side == 'left':
            connection = box.left[connection_nr]
            # box.left[connection_nr] = connection + [resource_id]
            box.left[connection_nr].id = resource_id
        elif connection_side == 'right':
            connection = box.right[connection_nr]
            # box.right[connection_nr] = connection + [resource_id]
            box.right[connection_nr].id = resource_id

    def wire_add_to_compound_box(self, resource_id, connection_nr, box, connection_id):
        logger.info(f"Adding connection to compound box: {box.id}, connection_id: {connection_id}, id: {resource_id}")
        sides = ['left', 'right', 'left_inner', 'right_inner']
        for side in sides:
            side_list = getattr(box, side)
            for con in side_list:
                if connection_id in con:
                    # side_list[connection_nr] += [resource_id]
                    side_list[connection_nr].id = resource_id

    def wire_handle_resource_action(self, resource: Resource, resource_id, connection_nr, connection_box_id, connection_side,
                                    connection_id):
        logger.info(f"Handling resource action for resource: {resource}, id: {resource_id}")
        if connection_box_id is None:
            if connection_side != 'spider':
                self.wire_main_input_output(connection_nr, connection_box_id, connection_side, resource_id)
        else:
            box = self.generator_get_box_by_id(connection_box_id)
            if box:
                if box.type != 1:
                    self.wire_add_to_atomic_box(connection_nr, box, connection_side, resource_id)
                else:
                    self.wire_add_to_compound_box(resource_id, connection_nr, box, connection_id)
        resource.add_connection(ConnectionInfo(connection_nr, connection_side, connection_id, connection_box_id))

    def wire_create_new_resource(self, wire_id, connection_nr, connection_box_id, connection_side,
                                 connection_id) -> Resource:
        """
        :param wire_id:
        :param connection_nr:
        :param connection_box_id:
        :param connection_side:
        :param connection_id:
        :return created resource:
        """
        logger.info(f"Creating new resource with id: {wire_id}")
        resource = Resource(wire_id)
        self.wire_handle_resource_action(resource, wire_id, connection_nr, connection_box_id, connection_side,
                                         connection_id)
        self.diagram.add_resource(resource)
        logger.warning(f"Added connection to resource with id {wire_id} connections {resource.connections}.")
        logger.info(f"Resources: {self.diagram.resources}")
        logger.info(f"Number of Resources: {len(self.diagram.resources)}")
        logger.info(f"Overall input and output: {self.diagram.input} and {self.diagram.output}")
        return resource

    def box_callback(self, box_id, action=None, connection_id=None, generator_side=None, connection_nr=None, operator=None,
                     canvas_id=None):
        box = self.generator_get_box_by_id(box_id)

        if box:
            if action in ["add_inner_left", "add_inner_right", "remove_inner_left", "remove_inner_right"]:
                self.generator_handle_inner_connection(box, action, connection_id)
            elif action in ['box_add_left', 'box_add_right', 'box_remove_connection']:
                self.generator_handle_box_connection(box, action, connection_nr, connection_id, generator_side)
            elif action == 'box_remove_connection_all':
                box.remove_all_left()
                box.remove_all_right()
            elif action == 'box_delete':
                self.generator_delete_box(box)
                HypergraphManager.remove_hyper_edge(box.id)
            elif action == 'compound':
                box.add_type(1)
                logger.info(f"created sub diagram: {box.type}")
            elif action == 'atomic':
                box.add_type(0)
                logger.info(f"created atomic component: {box.type}")
            elif action == 'sub_box':
                parent = self.generator_get_box_by_id(connection_id)
                parent.subset.append(box_id)
                box.parent = connection_id
            elif action == "box_add_operator":
                box.operand = operator
            elif action == 'box_swap_id':
                HypergraphManager.swap_hyper_edge_id(box.id, connection_id)
                box.id = connection_id
            elif action == "change_connection_id":
                if generator_side == ConnectionSide.LEFT:
                    # box.left[-1] = connection_id
                    box.left.id = connection_id
                else:
                    # box.right[-1] = connection_id
                    box.right.id = connection_id
        # TODO create or delete nodes when diagram input/output added/removed
        elif action == 'add_diagram_output':
            self.add_main_diagram_output()

            HypergraphManager.create_new_node(connection_id, canvas_id)
        elif action == 'add_diagram_input':
            self.add_main_diagram_input()

            HypergraphManager.create_new_node(connection_id, canvas_id)
        elif action == 'remove_diagram_input':
            self.remove_main_diagram_input()

            HypergraphManager.remove_node(connection_id)
        elif action == 'remove_diagram_output':
            self.remove_main_diagram_output()

            HypergraphManager.remove_node(connection_id)
        # elif action == 'box_swap_id':   PROGRAM CAN`T REACH THAT?
        #     hyper_edge = BoxToHyperEdgeMapping.get_hyper_edge_by_box_id(box.id)
        #     BoxToHyperEdgeMapping.remove_pair(box.id)
        #     BoxToHyperEdgeMapping.add_new_pair(connection_id, hyper_edge)
        #
        #     box.id = connection_id
        else:
            self.generator_create_new_box(box_id)

        logger.info(f"Resources: {self.diagram.resources}")
        logger.info(f"Number of Resources: {len(self.diagram.resources)}")
        logger.info(f"Number of Boxes: {len(self.diagram.boxes)}")

    def add_main_diagram_input(self):
        self.diagram.input.append([len(self.diagram.input), None])

    def add_main_diagram_output(self):
        self.diagram.output.append([len(self.diagram.output), None])

    def remove_main_diagram_input(self):
        if len(self.diagram.input[-1]) > 2:
            resource = self.wire_get_resource_by_id(self.diagram.input[-1][2])
            self.wire_handle_delete_resource(resource)
        self.diagram.input.pop()

    def remove_main_diagram_output(self):
        if len(self.diagram.output[-1]) > 2:
            resource = self.wire_get_resource_by_id(self.diagram.output[-1][2])
            self.wire_handle_delete_resource(resource)
        self.diagram.output.pop()

    def generator_handle_inner_connection(self, box, action, connection_id):
        if box.type == 1:
            if action == "add_inner_left":
                box.add_left_inner(ConnectionInfo(len(box.left_inner), ConnectionSide.INNER_LEFT, connection_id, box.id))
                # NOTE currently not necessary since FE handles sub diagram outer connection creation
                # if len(box.left) < len(box.left_inner):
                #     box.left.append([len(box.left), box.id])
            elif action == "add_inner_right":
                box.add_right_inner(ConnectionInfo(len(box.right_inner), ConnectionSide.INNER_RIGHT, connection_id, box.id))
                # NOTE currently not necessary since FE handles sub diagram outer connection creation
                # if len(box.right) < len(box.right_inner):
                #     box.right.append([len(box.right), box.id])
            if action == "remove_inner_left":
                self.generator_remove_box_connection(box, len(box.left_inner) - 1, ConnectionSide.INNER_LEFT)
            elif action == "remove_inner_right":
                self.generator_remove_box_connection(box, len(box.right_inner) - 1, ConnectionSide.INNER_RIGHT)

    def generator_handle_box_connection(self, box, action, connection_nr, connection_id, generator_side):
        if action in ['box_add_left', 'box_add_right']:
            self.generator_add_box_connection(box, action, connection_nr, connection_id)
        elif action == 'box_remove_connection':
            self.generator_remove_box_connection(box, connection_nr, generator_side)

    def generator_add_box_connection(self, box, action, connection_nr, connection_id):
        if action == 'box_add_left':
            box.add_left(ConnectionInfo(connection_nr, ConnectionSide.LEFT, connection_id, box.id))
            logger.info(
                f"added box connection left: id {box.id} connection nr {connection_nr} side left, connection id {connection_id}")
            logger.info(f"Number of connection in box side: {len(box.left)}")
        elif action == 'box_add_right':
            box.add_right(ConnectionInfo(connection_nr, ConnectionSide.RIGHT, connection_id, box.id))
            logger.info(
                f"added box connection right: id {box.id} connection nr {connection_nr} side right, connection id {connection_id}")
            logger.info(f"Number of connection in box side: {len(box.right)}")

    def generator_remove_box_connection(self, box: Generator, connection_id, connection_side):
        if box.type == 0:
            if connection_side == ConnectionSide.LEFT:
                if box.left[connection_id].is_all_fields_exists():
                    if self.wire_get_resource_by_id(box.left[connection_id].id):
                        self.wire_handle_delete_resource(self.wire_get_resource_by_id(box.left[connection_id].id))
                    else:
                        self.spider_handle_delete_connection(
                            self.spider_get_resource_by_connection_id(box.left[connection_id].id),
                            box.left[connection_id].side)
                box.remove_left_atomic(connection_id)
            elif connection_side == ConnectionSide.RIGHT:
                if box.right[connection_id].is_all_fields_exists():
                    if self.wire_get_resource_by_id(box.right[connection_id].id):
                        self.wire_handle_delete_resource(self.wire_get_resource_by_id(box.right[connection_id].id))
                    else:
                        self.spider_handle_delete_connection(
                            self.spider_get_resource_by_connection_id(box.right[connection_id].id),
                            box.right[connection_id].side)
                box.remove_right_atomic(connection_id)
        else:
            if connection_side == ConnectionSide.LEFT:
                if box.left[connection_id].is_all_fields_exists():
                    if self.wire_get_resource_by_id(box.left[connection_id].id):
                        self.wire_handle_delete_resource(self.wire_get_resource_by_id(box.left[connection_id].id))
                    else:
                        self.spider_handle_delete_connection(
                            self.spider_get_resource_by_connection_id(box.left[connection_id].id),
                            box.left[connection_id].side)
                # box.remove_left([connection_id, box.id])
                box.remove_left(connection_id)
            elif connection_side == ConnectionSide.RIGHT:
                # if len(box.right[connection_id]) == 4:
                if box.right[connection_id].is_all_fields_exists():
                    if self.wire_get_resource_by_id(box.right[connection_id].id):
                        self.wire_handle_delete_resource(self.wire_get_resource_by_id(box.right[connection_id].id))
                    else:
                        self.spider_handle_delete_connection(
                            self.spider_get_resource_by_connection_id(box.right[connection_id].id),
                            box.right[connection_id].side)
                # box.remove_right([connection_id, box.id])
                box.remove_right(connection_id)
            elif connection_side == ConnectionSide.INNER_LEFT:
                # if len(box.left_inner[connection_id]) == 4:
                if box.left_inner[connection_id].is_all_fields_exists():
                    if self.wire_get_resource_by_id(box.left_inner[connection_id].id):
                        self.wire_handle_delete_resource(self.wire_get_resource_by_id(box.left_inner[connection_id].id))
                    else:
                        self.spider_handle_delete_connection(
                            self.spider_get_resource_by_connection_id(box.left_inner[connection_id].id),
                            box.left_inner[connection_id].side)
                box.left_inner.pop()
            elif connection_side == ConnectionSide.INNER_RIGHT:
                # if len(box.right_inner[connection_id]) == 4:
                if box.right_inner[connection_id].is_all_fields_exists():
                    if self.wire_get_resource_by_id(box.right_inner[connection_id].id):
                        self.wire_handle_delete_resource(
                            self.wire_get_resource_by_id(box.right_inner[connection_id].id))
                    else:
                        self.spider_handle_delete_connection(
                            self.spider_get_resource_by_connection_id(box.right_inner[connection_id].id),
                            box.right_inner[connection_id].side)
                box.right_inner.pop()
        logger.info(f"Removed associated resource: {connection_id}, side {connection_side}")

    def generator_delete_box(self, box):
        if box.type == 1:
            if box.parent:
                parent_box = self.generator_get_box_by_id(box.parent)
                parent_box.subset.remove(box.id)
            for sub_box in list(box.subset):
                sub_box_object = self.generator_get_box_by_id(sub_box)
                self.generator_delete_box(sub_box_object)
            for i in range(len(box.left) - 1, -1, -1):
                connection_id = box.left[i].id
                self.generator_remove_box_connection(box, connection_id, ConnectionSide.LEFT)
            for i in range(len(box.right) - 1, -1, -1):
                connection_id = box.right[i].id
                self.generator_remove_box_connection(box, connection_id, ConnectionSide.RIGHT)
            for i in range(len(box.left_inner) - 1, -1, -1):
                connection_id = box.left_inner[i].id
                self.generator_remove_box_connection(box, connection_id, ConnectionSide.INNER_LEFT)
            for i in range(len(box.right_inner) - 1, -1, -1):
                connection_id = box.right_inner[i].id
                self.generator_remove_box_connection(box, connection_id, ConnectionSide.INNER_RIGHT)
            for wire in list(box.spiders):
                self.delete_spider_be(wire)
        else:
            if box.parent:
                parent_box = self.generator_get_box_by_id(box.parent)
                parent_box.subset.remove(box.id)
            for i in range(len(box.left) - 1, -1, -1):
                connection_id = box.left[i].id
                self.generator_remove_box_connection(box, connection_id, ConnectionSide.LEFT)
            for i in range(len(box.right) - 1, -1, -1):
                connection_id = box.right[i].id
                self.generator_remove_box_connection(box, connection_id, ConnectionSide.RIGHT)

        self.diagram.remove_box(box)

    def generator_create_new_box(self, box_id):
        box = Generator(box_id)
        self.diagram.add_box(box)

    def wire_get_resource_by_id(self, resource_id):
        return next((r for r in self.diagram.resources if r.id == resource_id), None)

    def generator_get_box_by_id(self, box_id):
        return next((b for b in self.diagram.boxes if b.id == box_id), None)

    def spider_get_resource_by_connection_id(self, spider_id):
        return next((b for b in self.diagram.spiders if b.id == spider_id), None)
