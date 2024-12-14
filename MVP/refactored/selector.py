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
        self.copied_items = {"boxes": [], "spiders": [], "wires": []}  # Initialize copied_items

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
        """Store the selected items for later pasting."""
        self.copied_items = {
            "boxes": [box for box in self.selected_items if isinstance(box, Box)],
            "spiders": [spider for spider in self.selected_items if isinstance(spider, Spider)],
            "wires": [
                {
                    "wire": wire,
                    "start_connection": wire.start_connection,
                    "end_connection": wire.end_connection,
                }
                for wire in self.selected_items if isinstance(wire, Wire)
            ],
        }

    def paste_copied_items(self, offset_x=50, offset_y=50):
        """Recreate the copied items on the canvas at an offset."""
        new_items = {"boxes": [], "spiders": [], "wires": []}
        connection_mapping = {}

        # Step 1: Paste boxes and remap connections
        for box in self.copied_items["boxes"]:
            # Correct the parameter names for the `add_box` method
            new_box = self.canvas.add_box(
                loc=(box.x + offset_x, box.y + offset_y),
                size=box.size,
                id_=None
            )
            for connection in box.connections:
                if connection.side == "left":
                    new_conn = new_box.add_left_connection()
                else:
                    new_conn = new_box.add_right_connection()
                connection_mapping[connection] = new_conn
            new_items["boxes"].append(new_box)

        # Step 2: Paste spiders and map them
        for spider in self.copied_items["spiders"]:
            new_spider = self.canvas.add_spider(
                loc=(spider.location[0] + offset_x, spider.location[1] + offset_y),
                id_=None
            )
            connection_mapping[spider] = new_spider
            new_items["spiders"].append(new_spider)

        # Step 3: Recreate wires
        for wire_info in self.copied_items["wires"]:
            original_wire = wire_info["wire"]
            start_conn = connection_mapping.get(wire_info["start_connection"])
            end_conn = connection_mapping.get(wire_info["end_connection"])

            if start_conn and end_conn:
                new_wire = Wire(
                    self.canvas,
                    start_connection=start_conn,
                    receiver=self.canvas.receiver,
                    end_connection=end_conn,
                )
                new_items["wires"].append(new_wire)
            else:
                print(
                    f"Failed to recreate wire {original_wire.id}: "
                    f"Start: {start_conn}, End: {end_conn}"
                )

        self.canvas.update()
        print(f"Pasted items: {new_items}")






