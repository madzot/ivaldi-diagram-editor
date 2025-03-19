from MVP.refactored.backend.types.ActionType import ActionType
from MVP.refactored.frontend.canvas_objects.box import Box
from MVP.refactored.frontend.canvas_objects.spider import Spider
from MVP.refactored.frontend.canvas_objects.wire import Wire
import copy


class Selector:
    def __init__(self, main_diagram, receiver):
        self.canvas = main_diagram.custom_canvas
        self.selecting = False
        self.selected_items = []
        self.selected_boxes = []
        self.selected_spiders = []
        self.selected_wires = []
        self.origin_x = None
        self.origin_y = None
        self.connection_mapping = {}
        self.copied_items = []
        self.copied_wire_list = []
        self.receiver = receiver

    def start_selection(self, event):
        for item in self.selected_items:
            item.deselect()
        self.selecting = True
        self.origin_x = event.x
        self.origin_y = event.y
        self.canvas.selectBox = self.canvas.create_rectangle(self.origin_x, self.origin_y, self.origin_x + 1,
                                                             self.origin_y + 1)
        self.selected_items.clear()
        self.selected_boxes.clear()
        self.selected_spiders.clear()
        self.selected_wires.clear()

    def update_selection(self, event):
        if self.selecting:
            x_new = event.x
            y_new = event.y
            self.canvas.coords(self.canvas.selectBox, self.origin_x, self.origin_y, x_new, y_new)

    def finalize_selection(self, boxes, spiders, wires):
        if self.selecting:
            selected_coordinates = self.canvas.coords(self.canvas.selectBox)

            self.selected_boxes = [box for box in boxes if self.is_within_selection(box.rect, selected_coordinates)]

            self.selected_spiders = [spider for spider in spiders if
                                     self.is_within_selection_point(spider.location, selected_coordinates)]

            self.selected_wires = [wire for wire in wires if
                                   self.is_within_selection_point(wire.start_connection.location, selected_coordinates)
                                   or self.is_within_selection_point(wire.end_connection.location,
                                                                     selected_coordinates)]
            self.selected_items = self.selected_boxes + self.selected_spiders + self.selected_wires
            for item in self.selected_items:
                item.select()

    def select_action(self):
        if self.selecting:
            self.canvas.delete(self.canvas.selectBox)
            self.selecting = False

    def finish_selection(self):
        for item in self.selected_items:
            item.deselect()
        self.selected_items.clear()
        # Remove the selection box and reset selecting state
        self.canvas.delete(self.canvas.selectBox)
        self.selecting = False

    def create_sub_diagram(self):
        coordinates = self.find_corners_selected_items()
        if len(self.selected_boxes) == 0 and len(self.selected_spiders) == 0:
            return
        x = (coordinates[0] + coordinates[2]) / 2
        y = (coordinates[1] + coordinates[3]) / 2
        box = self.canvas.add_box((x, y), shape="rectangle")
        for wire in filter(lambda w: w in self.canvas.wires, self.selected_wires):
            # wire.delete_self("sub_diagram")
            wire.delete_self()
        for box_ in filter(lambda b: b in self.canvas.boxes, self.selected_boxes):
            # box_.delete_box(keep_sub_diagram=True, action="sub_diagram")
            box_.delete_box()
        for spider in filter(lambda s: s in self.canvas.spiders, self.selected_spiders):
            # spider.delete_spider("sub_diagram")
            spider.delete_spider()
            if self.canvas.receiver.listener:
                self.canvas.receiver.receiver_callback(
                    'create_spider_parent', wire_id=spider.id, connection_id=spider.id, generator_id=box.id
                ) # TODO WTF
        sub_diagram = box.edit_sub_diagram(save_to_canvasses=False)
        prev_status = self.canvas.receiver.listener
        # self.canvas.receiver.listener = False # TODO WTF Why it is off for this part
        self.canvas.copier.copy_canvas_contents(
            sub_diagram, self.selected_wires, self.selected_boxes, self.selected_spiders, coordinates, box
        ) # TODO add receiver callback into copier? I suppose that is solution
        box.lock_box()
        self.canvas.receiver.listener = prev_status

        sub_diagram.set_name(str(sub_diagram.id)[-6:])
        box.set_label(str(sub_diagram.id)[-6:])
        self.canvas.main_diagram.add_canvas(sub_diagram)

    def is_within_selection(self, rect, selection_coords):
        if len(self.canvas.coords(rect)) == 4:
            x1, y1, x2, y2 = self.canvas.coords(rect)
            x = (x1 + x2) / 2
            y = (y1 + y2) / 2
        elif len(self.canvas.coords(rect)) == 6:
            x1, y1, x2, y2, x3, y3 = self.canvas.coords(rect)
            x = (x1 + x2 + x3) / 3
            y = (y1 + y2 + y3) / 3
        else:
            return False
        return selection_coords[0] <= x <= selection_coords[2] and selection_coords[1] <= y <= selection_coords[3]

    def delete_selected_items(self):
        for item in self.selected_items:
            if isinstance(item, Box):
                if item.sub_diagram:
                    action_param = "sub_diagram"
                else:
                    action_param = None
                item.delete_box(action=action_param)
            if isinstance(item, Spider):
                item.delete_spider()
        self.selected_items.clear()

    @staticmethod
    def is_within_selection_point(point, selection_coords):
        """Check if a point is within the selection area."""
        x, y = point
        return selection_coords[0] <= x <= selection_coords[2] and selection_coords[1] <= y <= selection_coords[3]

    def copy_selected_items(self):
        if len(self.selected_items) > 0:
            self.copied_items.clear()
            self.copied_wire_list.clear()
            connection_list = []

            for item in self.selected_items:
                if isinstance(item, Box):
                    connections_copy = []
                    for connection in item.connections:
                        connection_list.append(connection)
                        connections_copy.append({
                            'id': copy.deepcopy(connection.id),
                            'side': copy.deepcopy(connection.side),
                            'index': copy.deepcopy(connection.index)
                        })

                    self.copied_items.append({
                        'component': "Box",
                        'id': copy.deepcopy(item.id),
                        'label': copy.deepcopy(item.label_text),
                        'location': (item.x, item.y),
                        'size': copy.deepcopy(item.size),
                        'shape': copy.deepcopy(item.shape),
                        'connections': connections_copy,
                        'sub-diagram': copy.deepcopy(item.sub_diagram.id) if item.sub_diagram else None
                    })
                    if item.sub_diagram:
                        if item.label_text not in self.canvas.master.project_exporter.get_current_d():
                            self.canvas.master.save_box_to_diagram_menu(item)

                if isinstance(item, Spider):
                    for wire in item.wires:
                        if wire.start_connection == item:
                            connection_list.append(wire.start_connection)
                        else:
                            connection_list.append(wire.end_connection)
                    self.copied_items.append({
                        'component': "Spider",
                        'id': copy.deepcopy(item.id),
                        'location': (item.x, item.y),
                        'size': copy.deepcopy(item.r),
                    })

            for item in self.selected_items:
                if isinstance(item, Wire):
                    if item.start_connection in connection_list and item.end_connection in connection_list:
                        self.copied_wire_list.append({
                            'wire': "Wire",
                            'start_connection': None,
                            'end_connection': None,
                            'original_start_connection': copy.deepcopy(item.start_connection.id),
                            'original_start_index': copy.deepcopy(item.start_connection.index),
                            'original_start_side': copy.deepcopy(item.start_connection.side),
                            'original_end_connection': copy.deepcopy(item.end_connection.id),
                            'original_end_index': copy.deepcopy(item.end_connection.index),
                            'original_end_side': copy.deepcopy(item.end_connection.side)
                        })


    def paste_copied_items(self, event_x=50, event_y=50):
        if len(self.copied_items) > 0:

            middle_point = self.find_middle_point(event_x, event_y)

            for item in self.copied_items:
                if item['component'] == "Box":
                    if item["sub-diagram"]:
                        new_box = self.canvas.master.json_importer.add_box_from_menu(
                            self.canvas, item['label'], (event_x + item['location'][0] - middle_point[0],
                                                         event_y + item['location'][1] - middle_point[1]), True)
                    else:
                        new_box = self.canvas.add_box((event_x + item['location'][0] - middle_point[0],
                                                       event_y + item['location'][1] - middle_point[1]),
                                                      size=item['size'], shape=item['shape'])
                        for c in item['connections']:
                            if c['side'] == "right":
                                new_box.add_right_connection()
                            if c['side'] == "left":
                                new_box.add_left_connection()
                        new_box.set_label(item['label'])

                    for wire in self.copied_wire_list:
                        for box_connection in item['connections']:
                            if wire['original_start_connection'] == box_connection['id']:
                                for connection in new_box.connections:
                                    if (connection.side == wire['original_start_side']
                                            and connection.index == wire['original_start_index']):
                                        wire['start_connection'] = connection
                            if wire['original_end_connection'] == box_connection['id']:
                                for connection in new_box.connections:
                                    if (connection.side == wire['original_end_side']
                                            and connection.index == wire['original_end_index']):
                                        wire['end_connection'] = connection

                if item['component'] == "Spider":
                    new_spider = self.canvas.add_spider((event_x + item['location'][0] - middle_point[0],
                                                         event_y + item['location'][1] - middle_point[1]))
                    for wire in self.copied_wire_list:
                        if wire['original_start_connection'] == item['id']:
                            wire['start_connection'] = new_spider
                        if wire['original_end_connection'] == item['id']:
                            wire['end_connection'] = new_spider

            for wire in self.copied_wire_list:
                self.canvas.start_wire_from_connection(wire['start_connection'])
                self.canvas.end_wire_to_connection(wire['end_connection'])

    def find_middle_point(self, event_x, event_y):
        most_left = self.canvas.winfo_width()
        most_right = 0
        most_up = self.canvas.winfo_height()
        most_down = 0
        for item in self.copied_items:
            if item['component'] == "Box":
                if item['location'][0] < most_left:
                    most_left = item['location'][0]
                if item['location'][1] < most_up:
                    most_up = item['location'][1]
                if item['location'][0] + item['size'][0] > most_right:
                    most_right = item['location'][0] + item['size'][0]
                if item['location'][1] + item['size'][1] > most_down:
                    most_down = item['location'][1] + item['size'][1]
            if item['component'] == "Spider":
                if item['location'][0] - item['size'] < most_left:
                    most_left = item['location'][0] - item['size']
                if item['location'][1] - item['size'] < most_up:
                    most_up = item['location'][1] - item['size']
                if item['location'][0] + item['size'] > most_right:
                    most_right = item['location'][0] + item['size']
                if item['location'][1] + item['size'] > most_down:
                    most_down = item['location'][1] + item['size']

        middle_x = (most_left + most_right) / 2
        middle_y = (most_up + most_down) / 2

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if most_left - (middle_x - event_x) < 0:
            middle_x = event_x + most_left
        if most_right - (middle_x - event_x) > canvas_width:
            middle_x = event_x - (canvas_width - most_right)

        if most_up - (middle_y - event_y) < 0:
            middle_y = event_y + most_up
        if most_down - (middle_y - event_y) > canvas_height:
            middle_y = event_y - (canvas_height - most_down)

        return middle_x, middle_y

    def find_corners_selected_items(self):
        most_left = self.canvas.winfo_width()
        most_right = 0
        most_up = self.canvas.winfo_height()
        most_down = 0
        for item in self.selected_items:
            if isinstance(item, Box):
                if item.x < most_left:
                    most_left = item.x
                if item.y < most_up:
                    most_up = item.y
                if item.x + item.size[0] > most_right:
                    most_right = item.x + item.size[0]
                if item.y + item.size[1] > most_down:
                    most_down = item.y + item.size[1]
            if isinstance(item, Spider):
                if item.x - item.r < most_left:
                    most_left = item.x - item.r
                if item.y - item.r < most_up:
                    most_up = item.y - item.r
                if item.x + item.r > most_right:
                    most_right = item.x + item.r
                if item.y + item.r > most_down:
                    most_down = item.y + item.r
        return [most_left, most_up, most_right, most_down]

    def select_wires_between_selected_items(self):
        self.selected_boxes.clear()
        self.selected_spiders.clear()
        self.selected_wires.clear()
        selected_connections = []
        for item in self.selected_items:
            if isinstance(item, Box):
                for connection in item.connections:
                    selected_connections.append(connection)
            if isinstance(item, Spider):
                selected_connections.append(item)
        for wire in self.canvas.wires:
            if wire.start_connection in selected_connections and wire.end_connection in selected_connections:
                if wire not in self.canvas.selector.selected_items:
                    wire.select()
                    self.canvas.selector.selected_items.append(wire)
            if wire.start_connection not in selected_connections or wire.end_connection not in selected_connections:
                if wire in self.canvas.selector.selected_items:
                    wire.deselect()
                    self.canvas.selector.selected_items.remove(wire)
