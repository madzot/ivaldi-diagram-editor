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

    def select_action(self, create_diagram=False):
        if self.selecting:
            if create_diagram:
                self.create_sub_diagram(self.selected_boxes, self.selected_spiders, self.selected_wires,
                                        self.canvas.coords(self.canvas.selectBox))
                self.finish_selection()
            else:
                self.finish_selection()

    def finish_selection(self):
        for item in self.selected_items:
            item.deselect()
        # Remove the selection box and reset selecting state
        self.canvas.delete(self.canvas.selectBox)
        self.selecting = False
        self.selected_items.clear()

    def create_sub_diagram(self, boxes, spiders, wires, coordinates):
        x = (coordinates[0] + coordinates[2]) / 2
        y = (coordinates[1] + coordinates[3]) / 2

        # Create a new box that will contain the sub-diagram
        box = self.canvas.add_box((x, y))
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
        x1, y1, x2, y2 = self.canvas.coords(rect)
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        return selection_coords[0] <= x <= selection_coords[2] and selection_coords[1] <= y <= selection_coords[3]

    @staticmethod
    def is_within_selection_point(point, selection_coords):
        """Check if a point is within the selection area."""
        x, y = point
        return selection_coords[0] <= x <= selection_coords[2] and selection_coords[1] <= y <= selection_coords[3]
