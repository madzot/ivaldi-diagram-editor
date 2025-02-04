import logging

from MVP.refactored.backend.diagram import Diagram
from MVP.refactored.backend.generator import Generator
from MVP.refactored.backend.hypergraph.box_to_hyper_edge_mapping import BoxToHyperEdgeMapping
from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge
from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.backend.hypergraph.wire_and_spider_to_node_mapping import WireAndSpiderToNodeMapping
from MVP.refactored.backend.resource import Resource

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Receiver:
    def __init__(self):
        self.listener = True
        self.diagram = Diagram()
        logger.info("Receiver initialized.")

    def receiver_callback(self, action, **kwargs):
        wire_id = kwargs.get('wire_id')
        start_connection = kwargs.get('start_connection')
        end_connection = kwargs.get('end_connection')
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
            self.delete_spider_be(wire_id, canvas_id)
        else:
            logger.info("Routing to box_callback")
            self.box_callback(generator_id, action, connection_id, generator_side, connection_nr, operator, canvas_id)

    def delete_spider_be(self, wire_id, canvas_id):
        logger.info(f"Routing to delete_spider")
        spider = self.spider_get_resource_by_connection_id(wire_id)
        if spider.parent:
            parent = self.generator_get_box_by_id(spider.parent)
            parent.spiders.remove(wire_id)
        self.wire_handle_delete_resource(spider)

        HypergraphManager.remove_node(spider.id)
        # self._remove_node(spider.id) TODO

    def spider_parent(self, id, generator_id=None, canvas_id=None):
        spider = self.spider_get_resource_by_connection_id(id)
        spider.parent = generator_id
        parent = self.generator_get_box_by_id(generator_id)
        parent.spiders.append(spider.id)

    def create_spider(self, id, connection_id, generator_id=None, canvas_id=None):
        logger.info(f"Creating spider with id: {id}")
        resource = Resource(id)
        resource.spider = True
        resource.spider_connection = connection_id
        if generator_id:
            resource.parent = generator_id
            parent = self.generator_get_box_by_id(generator_id)
            parent.spiders.append(resource.id)
        # self.diagram.add_resource(resource)
        self.diagram.spiders.append(resource)
        logger.info(f"Spider created and added to diagram: {resource}")

        HypergraphManager.create_new_node(id, canvas_id=canvas_id)
        # new_node = Node(id) TODO
        #
        # WireAndSpiderToNodeMapping.add_new_pair(id, new_node)
        # new_hypergraph = Hypergraph(canvas_id=canvas_id)
        # HypergraphManager.add_hypergraph(new_hypergraph)

    def wire_callback(self, wire_id, action=None, start_connection=None, connection_id=None, end_connection=None,
                      canvas_id=None):
        logger.info(
            f"wire_callback invoked with wire_id: {wire_id}, action: {action}, start_connection: {start_connection}, connection_id: {connection_id}")
        if action == 'wire_delete':
            if start_connection and start_connection[2] == "spider":
                spider = self.spider_get_resource_by_connection_id(start_connection[3])
                spider.remove_connection(start_connection)
            elif end_connection and end_connection[2] == "spider":
                spider = self.spider_get_resource_by_connection_id(end_connection[3])
                spider.remove_connection(end_connection)
            else:
                resource = self.wire_get_resource_by_id(wire_id)
                self.wire_handle_delete_resource(resource)

            HypergraphManager.remove_node(wire_id)
            # self._remove_node(wire_id) TODO
        else:
            # TODO Create node when wire connected to spider. Spider node and new node should be united.
            if end_connection:  # HAS end_connection if connection between spider and something
                if start_connection[2] == 'spider':
                    spider = self.spider_get_resource_by_connection_id(connection_id)
                    spider.add_connection(end_connection)
                    connection_nr = end_connection[0]
                    connection_box_id = end_connection[1]
                    connection_side = end_connection[2]
                    box = self.generator_get_box_by_id(connection_box_id)
                    if box:
                        if box.type != 1:
                            self.wire_add_to_atomic_box(connection_nr, box, connection_side, spider.id)
                        else:
                            self.wire_add_to_compound_box(spider.id, connection_nr, box, connection_id)

                    # Add hyper edge to new node or union nodes
                    self.add_hyper_edge_or_union_with_nodes(wire_id, spider.id, box, end_connection[3],
                                                            end_connection[2], canvas_id)
                    # TODO
                    new_node = HypergraphManager.create_new_node(wire_id, canvas_id)
                    HypergraphManager.union_nodes(new_node, spider.id) # unite wire and spider to one node
                    if box:
                        if connection_side == 'left':
                            HypergraphManager.connect_node_with_output(new_node, connection_box_id)
                        elif connection_side == 'right':
                            HypergraphManager.connect_node_with_input(new_node, connection_box_id)
                    else: # connection to spider
                        HypergraphManager.union_nodes(new_node, end_connection[3])
                    print(f"Added wire - {wire_id}")

                elif end_connection[2] == 'spider':
                    spider = self.spider_get_resource_by_connection_id(connection_id)
                    spider.add_connection(start_connection)
                    connection_nr = start_connection[0]
                    connection_box_id = start_connection[1]
                    connection_side = start_connection[2]
                    box = self.generator_get_box_by_id(connection_box_id)
                    if box:
                        if box.type != 1:
                            self.wire_add_to_atomic_box(connection_nr, box, connection_side, spider.id)
                        else:
                            self.wire_add_to_compound_box(spider.id, connection_nr, box, connection_id)

                    # Add hyper edge to new node or union nodes
                    self.add_hyper_edge_or_union_with_nodes(wire_id, spider.id, box, start_connection[3],
                                                            start_connection[2], canvas_id)
                    # TODO
                    new_node = HypergraphManager.create_new_node(wire_id, canvas_id)
                    HypergraphManager.union_nodes(new_node, spider.id)  # unite wire and spider to one node
                    if box:
                        if connection_side == 'left':
                            HypergraphManager.connect_node_with_output(new_node, connection_box_id)
                        elif connection_side == 'right':
                            HypergraphManager.connect_node_with_input(new_node, connection_box_id)
                    else:  # connection to spider
                        HypergraphManager.union_nodes(new_node, start_connection[3])
            else:  # if it connection not between spider and smt
                connection_nr = start_connection[0]
                connection_box_id = start_connection[1]
                connection_side = start_connection[2]
                resource: Resource = self.wire_get_resource_by_id(wire_id)
                if resource:
                    self.wire_handle_resource_action(resource, wire_id, connection_nr, connection_box_id,
                                                     connection_side,
                                                     connection_id)

                    new_node = Node(resource.id)
                    should_be_united_with: list[tuple[int, Node]] = []  # in tuple first is conn_id
                    hyper_edges_nodes: set[Node] = set()
                    for connection in resource.connections:
                        conn_index, box_id, side, conn_id = connection
                        if box_id is not None:  # Wire connection with box
                            hyper_edge = BoxToHyperEdgeMapping.get_hyper_edge_by_box_id(box_id)
                            if side == "right":
                                new_node.append_input(hyper_edge)
                                hyper_edge.set_target_node(conn_index, new_node)

                            elif side == "left":
                                new_node.append_output(hyper_edge)
                                hyper_edge.set_source_node(conn_index, new_node)

                            for node in hyper_edge.get_source_nodes() + hyper_edge.get_target_nodes():
                                hyper_edges_nodes.add(node)
                        else:  # Wire connection with diagram input/output
                            node = WireAndSpiderToNodeMapping.get_node_by_wire_or_spider_id(conn_id)  # input/output id
                            should_be_united_with.append((conn_id, node))


                    for conn_id, node_to_union in should_be_united_with:
                        new_node.union(node_to_union)

                    WireAndSpiderToNodeMapping.add_new_pair(resource.id, new_node)





                    # self.create_hypergraph([new_node], canvas_id, list(hyper_edges_nodes))

                else:
                    resource = self.wire_create_new_resource(wire_id, connection_nr, connection_box_id, connection_side,
                                                             connection_id)

        logger.info(f"Resources: {self.diagram.resources}")
        logger.info(f"Spiders: {self.diagram.spiders}")
        logger.info(f"Number of Resources: {len(self.diagram.resources)}")
        logger.info(f"Overall input and output: {self.diagram.input} and {self.diagram.output}")


    def spider_handle_delete_connection(self, spider, connection):
        if spider:
            for resource in list(spider.connections):
                if resource[2] == connection:
                    spider.connections.remove(resource)

    def wire_handle_delete_resource(self, resource):
        """Establish inner removal for connection."""
        if resource:
            if resource.connections:
                for associated_connection in resource.connections:
                    connection_nr = associated_connection[0]
                    box_id = associated_connection[1]
                    connection_side = associated_connection[2]
                    box = self.generator_get_box_by_id(box_id)
                    if box:
                        if box.type == 1:
                            connection_id = associated_connection[3]
                            for con in box.left:
                                if connection_id in con:
                                    box.left[connection_nr] = [connection_nr, box_id, connection_id]
                            for con in box.right:
                                if connection_id in con:
                                    box.right[connection_nr] = [connection_nr, box_id, connection_id]
                            for con in box.left_inner:
                                if connection_id in con:
                                    box.left_inner[connection_nr] = [connection_nr, box_id, connection_id]
                            for con in box.right_inner:
                                if connection_id in con:
                                    box.right_inner[connection_nr] = [connection_nr, box_id, connection_id]
                        else:
                            if connection_side == "left":
                                box.left[connection_nr] = [connection_nr, box_id]
                            else:
                                box.right[connection_nr] = [connection_nr, box_id]
                    else:  # Case of None when dealing with diagram input and outputs
                        if connection_side == "left":
                            self.diagram.output[connection_nr] = [connection_nr, box_id]
                        else:
                            self.diagram.input[connection_nr] = [connection_nr, box_id]

            self.diagram.remove_resource(resource)
            logger.warning(f"Resource with id {resource.id} removed.")
        else:
            logger.warning(f"Resource with id not found.")

    def wire_main_input_output(self, connection_nr, connection_box_id, connection_side, id):
        logger.info(f"Handling main input/output wiring with id: {id}")
        if connection_side == 'left':
            temp = [connection_nr, connection_box_id] + [id]
            self.diagram.output[connection_nr] = temp
        else:
            temp = [connection_nr, connection_box_id] + [id]
            self.diagram.input[connection_nr] = temp

    def wire_add_to_atomic_box(self, connection_nr, box, connection_side, id):
        logger.info(f"Adding connection to atomic box: {box.id}, side: {connection_side}, id: {id}, nr {connection_nr}")
        if connection_side == 'left':
            connection = box.left[connection_nr]
            box.left[connection_nr] = connection + [id]
        elif connection_side == 'right':
            connection = box.right[connection_nr]
            box.right[connection_nr] = connection + [id]

    def wire_add_to_compound_box(self, id, connection_nr, box, connection_id):
        logger.info(f"Adding connection to compound box: {box.id}, connection_id: {connection_id}, id: {id}")
        sides = ['left', 'right', 'left_inner', 'right_inner']
        for side in sides:
            side_list = getattr(box, side)
            for con in side_list:
                if connection_id in con:
                    side_list[connection_nr] += [id]

    def wire_handle_resource_action(self, resource, id, connection_nr, connection_box_id, connection_side,
                                    connection_id):
        logger.info(f"Handling resource action for resource: {resource}, id: {id}")
        if connection_box_id is None:
            if connection_side != 'spider':
                self.wire_main_input_output(connection_nr, connection_box_id, connection_side, id)
        else:
            box = self.generator_get_box_by_id(connection_box_id)
            if box:
                if box.type != 1:
                    self.wire_add_to_atomic_box(connection_nr, box, connection_side, id)
                else:
                    self.wire_add_to_compound_box(id, connection_nr, box, connection_id)
        resource.add_connection([connection_nr, connection_box_id, connection_side] + [connection_id])

    def wire_create_new_resource(self, id, connection_nr, connection_box_id, connection_side,
                                 connection_id) -> Resource:
        """
        :param id:
        :param connection_nr:
        :param connection_box_id:
        :param connection_side:
        :param connection_id:
        :return created resource:
        """
        logger.info(f"Creating new resource with id: {id}")
        resource = Resource(id)
        self.wire_handle_resource_action(resource, id, connection_nr, connection_box_id, connection_side,
                                         connection_id)
        self.diagram.add_resource(resource)
        logger.warning(f"Added connection to resource with id {id} connections {resource.connections}.")
        logger.info(f"Resources: {self.diagram.resources}")
        logger.info(f"Number of Resources: {len(self.diagram.resources)}")
        logger.info(f"Overall input and output: {self.diagram.input} and {self.diagram.output}")
        return resource

    def box_callback(self, id, action=None, connection_id=None, generator_side=None, connection_nr=None, operator=None,
                     canvas_id=None):
        box = self.generator_get_box_by_id(id)

        if box:
            if action in ["add_inner_left", "add_inner_right", "remove_inner_left", "remove_inner_right"]:
                self.generator_handle_inner_connection(box, action, connection_id)
            elif action in ['box_add_left', 'box_add_right', 'box_remove_connection']:
                self.generator_handle_box_connection(box, action, connection_nr, connection_id, generator_side)
                hyper_edge = BoxToHyperEdgeMapping.get_hyper_edge_by_box_id(box.id)
                if generator_side == "left":
                    hyper_edge.remove_source_connection_by_index(connection_nr)
                elif generator_side == "right":
                    hyper_edge.remove_target_connection_by_index(connection_nr)
            elif action == 'box_remove_connection_all':
                box.remove_all_left()
                box.remove_all_right()
                hyper_edge = BoxToHyperEdgeMapping.get_hyper_edge_by_box_id(box.id)
                hyper_edge.remove_all_source_nodes()
                hyper_edge.remove_all_target_nodes()
            elif action == 'box_delete':
                self.generator_delete_box(box)
                hyper_edge = BoxToHyperEdgeMapping.get_hyper_edge_by_box_id(box.id)
                hyper_edge.remove_self()
                BoxToHyperEdgeMapping.remove_pair(box.id)
            elif action == 'compound':
                box.add_type(1)
                logger.info(f"created sub diagram: {box.type}")
            elif action == 'atomic':
                box.add_type(0)
                logger.info(f"created atomic component: {box.type}")
            elif action == 'sub_box':
                parent = self.generator_get_box_by_id(connection_id)
                parent.subset.append(id)
                box.parent = connection_id
            elif action == "box_add_operator":
                box.operand = operator
            elif action == 'box_swap_id':
                hyper_edge = BoxToHyperEdgeMapping.get_hyper_edge_by_box_id(box.id)
                hyper_edge.set_id(connection_id)
                BoxToHyperEdgeMapping.remove_pair(box.id)
                BoxToHyperEdgeMapping.add_new_pair(connection_id, hyper_edge)
                box.id = connection_id
            elif action == "change_connection_id":
                if generator_side == "left":
                    box.left[-1] = connection_id
                else:
                    box.right[-1] = connection_id
        # TODO create or delete nodes when diagram input/output added/removed
        elif action == 'add_diagram_output':
            self.add_main_diagram_output()

            HypergraphManager.create_new_node(connection_id, canvas_id)
            # self._create_new_special_node(connection_id) TODO
        elif action == 'add_diagram_input':
            self.add_main_diagram_input()

            HypergraphManager.create_new_node(connection_id, canvas_id)
            # self._create_new_special_node(connection_id) TODO
        elif action == 'remove_diagram_input':
            self.remove_main_diagram_input()

            HypergraphManager.remove_node(connection_id)
            # self._remove_node(connection_id) TODO
        elif action == 'remove_diagram_output':
            self.remove_main_diagram_output()

            HypergraphManager.remove_node(connection_id)
            # self._remove_node(connection_id) TODO
        # elif action == 'box_swap_id':   PROGRAMM CAN`T REACH THAT?
        #     hyper_edge = BoxToHyperEdgeMapping.get_hyper_edge_by_box_id(box.id)
        #     BoxToHyperEdgeMapping.remove_pair(box.id)
        #     BoxToHyperEdgeMapping.add_new_pair(connection_id, hyper_edge)
        #
        #     box.id = connection_id
        else:
            self.generator_create_new_box(id)

            BoxToHyperEdgeMapping.add_new_pair(id, HyperEdge(id))

        logger.info(f"Resources: {self.diagram.resources}")
        logger.info(f"Number of Resources: {len(self.diagram.resources)}")
        logger.info(f"Number of Boxes: {len(self.diagram.boxes)}")

    def _create_new_special_node(self, _id: int):
        node = Node(_id, is_special=True)
        WireAndSpiderToNodeMapping.add_new_pair(_id, node)

    def _remove_node(self, _id: int):
        node = WireAndSpiderToNodeMapping.get_node_by_wire_or_spider_id(_id)
        node.remove_self()
        WireAndSpiderToNodeMapping.remove_pair(_id)

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
                box.left_inner.append([len(box.left_inner), box.id, connection_id])
                # NOTE currently not nessecary since FE handles subdiagram outer connection creation
                # if len(box.left) < len(box.left_inner):
                #     box.left.append([len(box.left), box.id])
            elif action == "add_inner_right":
                box.right_inner.append([len(box.right_inner), box.id, connection_id])
                # NOTE currently not nessecary since FE handles subdiagram outer connection creation
                # if len(box.right) < len(box.right_inner):
                #     box.right.append([len(box.right), box.id])
            if action == "remove_inner_left":
                self.generator_remove_box_connection(box, len(box.left_inner) - 1, "inner_left")
            elif action == "remove_inner_right":
                self.generator_remove_box_connection(box, len(box.right_inner) - 1, "inner_right")

    def generator_handle_box_connection(self, box, action, connection_nr, connection_id, generator_side):
        if action in ['box_add_left', 'box_add_right']:
            self.generator_add_box_connection(box, action, connection_nr, connection_id)
        elif action == 'box_remove_connection':
            self.generator_remove_box_connection(box, connection_nr, generator_side)

    def generator_add_box_connection(self, box, action, connection_nr, connection_id):
        if action == 'box_add_left':
            box.add_left([connection_nr, box.id, connection_id])
            logger.info(
                f"added box connecton left: id {box.id} connection nr {connection_nr} side left, connection id {connection_id}")
            logger.info(f"Number of connection in box side: {len(box.left)}")
        elif action == 'box_add_right':
            box.add_right([connection_nr, box.id, connection_id])
            logger.info(
                f"added box connecton right: id {box.id} connection nr {connection_nr} side right, connection id {connection_id}")
            logger.info(f"Number of connection in box side: {len(box.right)}")

    def generator_remove_box_connection(self, box, connection_id, connection_side):
        if box.type == 0:
            if connection_side == "left":
                if len(box.left[connection_id]) == 4:
                    if self.wire_get_resource_by_id(box.left[connection_id][3]):
                        self.wire_handle_delete_resource(self.wire_get_resource_by_id(box.left[connection_id][3]))
                    else:
                        self.spider_handle_delete_connection(
                            self.spider_get_resource_by_connection_id(box.left[connection_id][3]),
                            box.left[connection_id][2])
                box.remove_left_atomic(connection_id)
            elif connection_side == "right":
                if len(box.right[connection_id]) == 4:
                    if self.wire_get_resource_by_id(box.right[connection_id][3]):
                        self.wire_handle_delete_resource(self.wire_get_resource_by_id(box.right[connection_id][3]))
                    else:
                        self.spider_handle_delete_connection(
                            self.spider_get_resource_by_connection_id(box.right[connection_id][3]),
                            box.right[connection_id][2])
                box.remove_right_atomic(connection_id)
        else:
            if connection_side == "left":
                if len(box.left[connection_id]) == 4:
                    if self.wire_get_resource_by_id(box.left[connection_id][3]):
                        self.wire_handle_delete_resource(self.wire_get_resource_by_id(box.left[connection_id][3]))
                    else:
                        self.spider_handle_delete_connection(
                            self.spider_get_resource_by_connection_id(box.left[connection_id][3]),
                            box.left[connection_id][2])
                box.remove_left([connection_id, box.id])
            elif connection_side == "right":
                if len(box.right[connection_id]) == 4:
                    if self.wire_get_resource_by_id(box.right[connection_id][3]):
                        self.wire_handle_delete_resource(self.wire_get_resource_by_id(box.right[connection_id][3]))
                    else:
                        self.spider_handle_delete_connection(
                            self.spider_get_resource_by_connection_id(box.right[connection_id][3]),
                            box.right[connection_id][2])
                box.remove_right([connection_id, box.id])
            elif connection_side == "inner_left":
                if len(box.left_inner[connection_id]) == 4:
                    if self.wire_get_resource_by_id(box.left_inner[connection_id][3]):
                        self.wire_handle_delete_resource(self.wire_get_resource_by_id(box.left_inner[connection_id][3]))
                    else:
                        self.spider_handle_delete_connection(
                            self.spider_get_resource_by_connection_id(box.left_inner[connection_id][3]),
                            box.left_inner[connection_id][2])
                box.left_inner.pop()
            elif connection_side == "inner_right":
                if len(box.right_inner[connection_id]) == 4:
                    if self.wire_get_resource_by_id(box.right_inner[connection_id][3]):
                        self.wire_handle_delete_resource(
                            self.wire_get_resource_by_id(box.right_inner[connection_id][3]))
                    else:
                        self.spider_handle_delete_connection(
                            self.spider_get_resource_by_connection_id(box.right_inner[connection_id][3]),
                            box.right_inner[connection_id][2])
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
                connection_id = box.left[i][0]
                self.generator_remove_box_connection(box, connection_id, "left")
            for i in range(len(box.right) - 1, -1, -1):
                connection_id = box.right[i][0]
                self.generator_remove_box_connection(box, connection_id, "right")
            for i in range(len(box.left_inner) - 1, -1, -1):
                connection_id = box.left_inner[i][0]
                self.generator_remove_box_connection(box, connection_id, "inner_left")
            for i in range(len(box.right_inner) - 1, -1, -1):
                connection_id = box.right_inner[i][0]
                self.generator_remove_box_connection(box, connection_id, "inner_right")
            for wire in list(box.spiders):
                self.delete_spider_be(wire)
        else:
            if box.parent:
                parent_box = self.generator_get_box_by_id(box.parent)
                parent_box.subset.remove(box.id)
            for i in range(len(box.left) - 1, -1, -1):
                connection_id = box.left[i][0]
                self.generator_remove_box_connection(box, connection_id, "left")
            for i in range(len(box.right) - 1, -1, -1):
                connection_id = box.right[i][0]
                self.generator_remove_box_connection(box, connection_id, "right")

        self.diagram.remove_box(box)

    def generator_create_new_box(self, id):
        box = Generator(id)
        self.diagram.add_box(box)

    def wire_get_resource_by_id(self, id):
        return next((r for r in self.diagram.resources if r.id == id), None)

    def generator_get_box_by_id(self, id):
        return next((b for b in self.diagram.boxes if b.id == id), None)

    def spider_get_resource_by_connection_id(self, id):
        return next((b for b in self.diagram.spiders if b.id == id), None)
