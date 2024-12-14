from MVP.refactored.box import Box
from MVP.refactored.spider import Spider


class Selector:
    def __init__(self, canvas):
        self.canvas = canvas
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

    def select_action(self, event, create_diagram=False):
        if self.selecting:
            if create_diagram:
                self.create_sub_diagram(self.selected_boxes, self.selected_spiders, self.selected_wires,
                                        self.canvas.coords(self.canvas.selectBox), event)
                self.finish_selection()
            else:
                self.canvas.delete(self.canvas.selectBox)
                self.selecting = False

    def finish_selection(self):
        for item in self.selected_items:
            item.deselect()
        self.selected_items.clear()
        # Remove the selection box and reset selecting state
        self.canvas.delete(self.canvas.selectBox)
        self.selecting = False

    def create_sub_diagram(self, boxes, spiders, wires, coordinates, event):
        x = (coordinates[0] + coordinates[2]) / 2
        y = (coordinates[1] + coordinates[3]) / 2
        event.x, event.y = x, y

        # Create a new box that will contain the sub-diagram
        box = self.canvas.add_box((x, y), shape="rectangle")
        box.on_drag(event)
        sub_diagram = box.edit_sub_diagram(save_to_canvasses=False)
        prev_status = self.canvas.receiver.listener
        self.canvas.receiver.listener = False
        self.canvas.copier.copy_canvas_contents(
            sub_diagram, wires, boxes, spiders, coordinates, box
        )
        box.lock_box()
        self.canvas.receiver.listener = prev_status
        for wire in filter(lambda w: w in self.canvas.wires, wires):
            wire.delete_self("sub_diagram")
        for box_ in filter(lambda b: b in self.canvas.boxes, boxes):
            box_.delete_box(keep_sub_diagram=True, action="sub_diagram")
        for spider in filter(lambda s: s in self.canvas.spiders, spiders):
            spider.delete_spider("sub_diagram")
            if self.canvas.receiver.listener:
                self.canvas.receiver.receiver_callback(
                    'create_spider_parent', wire_id=spider.id, connection_id=spider.id, generator_id=box.id
                )

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
                item.delete_box()
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
            wire_list = []
            for item in self.selected_items:
                if isinstance(item, Box) or isinstance(item, Spider):
                    for wire in item.wires:
                        if wire not in wire_list:
                            wire_list.append(wire)
                        else:
                            wire_list.remove(wire)
                            self.copied_wire_list.append({
                                'wire': wire,
                                'start_connection': wire.start_connection,
                                'end_connection': wire.end_connection,
                                'original_start_connection': wire.start_connection,
                                'original_end_connection': wire.end_connection
                                })

                self.copied_items.append(item)

    def paste_copied_items(self, event_x=50, event_y=50):
        if len(self.copied_items) > 0:

            wire_list = self.copied_wire_list

            middle_point = self.find_middle_point()

            for item in self.copied_items:
                if isinstance(item, Box):
                    new_box = self.canvas.add_box((event_x+(item.x-middle_point[0]), event_y+(item.y-middle_point[1])),
                                                  size=item.size, shape=item.shape)
                    self.canvas.copier.copy_box(item, new_box, False)

                    for wire in wire_list:
                        if wire['original_start_connection'].box == item:
                            for connection in new_box.connections:
                                if (connection.side == wire['original_start_connection'].side
                                        and connection.index == wire['original_start_connection'].index):
                                    wire['start_connection'] = connection
                        if wire['original_end_connection'].box == item:
                            for connection in new_box.connections:
                                if (connection.side == wire['original_end_connection'].side
                                        and connection.index == wire['original_end_connection'].index):
                                    wire['end_connection'] = connection

                if isinstance(item, Spider):
                    new_spider = self.canvas.add_spider((event_x+(item.x-middle_point[0]),
                                                        event_y+(item.y-middle_point[1])))
                    for wire in wire_list:
                        if wire['original_start_connection'] is item:
                            wire['start_connection'] = new_spider
                        if wire['original_end_connection'] is item:
                            wire['end_connection'] = new_spider

            for wire in wire_list:
                self.canvas.start_wire_from_connection(wire['start_connection'])
                self.canvas.end_wire_to_connection(wire['end_connection'])

    def find_middle_point(self):
        most_left = self.canvas.winfo_width()
        most_right = 0
        most_up = self.canvas.winfo_height()
        most_down = 0
        for item in self.copied_items:
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
        return (most_left + most_right) / 2, (most_up + most_down) / 2
