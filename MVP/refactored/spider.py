import tkinter as tk

from MVP.refactored.box import Box
from MVP.refactored.connection import Connection


class Spider(Connection):
    def __init__(self, box, index, side, location, canvas, receiver, id_=None):
        self.r = 10
        super().__init__(box, index, side, location, canvas, self.r)
        self.canvas = canvas
        self.x = location[0]
        self.y = location[1]
        self.location = location
        if not id_:
            self.id = id(self)
        else:
            self.id = id_

        self.connections: list[Connection] = []
        self.context_menu = tk.Menu(self.canvas, tearoff=0)
        self.bind_events()
        self.wires = []
        self.receiver = receiver
        if self.receiver.listener:
            if self.canvas.diagram_source_box:
                self.receiver.receiver_callback('create_spider', wire_id=self.id, connection_id=self.id,
                                                generator_id=self.canvas.diagram_source_box.id)
            else:
                self.receiver.receiver_callback('create_spider', wire_id=self.id, connection_id=self.id)

        self.is_snapped = False
        self.snapped_x = None
        self.prev_snapped = None

    def is_spider(self):
        return True

    def bind_events(self):
        self.canvas.tag_bind(self.circle, '<ButtonPress-1>', lambda event: self.on_press())
        self.canvas.tag_bind(self.circle, '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind(self.circle, '<ButtonPress-3>', self.show_context_menu)

    def show_context_menu(self, event):
        self.close_menu()
        self.context_menu = tk.Menu(self.canvas, tearoff=0)

        self.context_menu.add_command(label="Delete Spider", command=self.delete_spider)
        self.context_menu.add_command(label="Cancel")

        self.context_menu.tk_popup(event.x_root, event.y_root)

    def delete_spider(self, action=None):
        [wire.delete_self(self) for wire in self.wires.copy()]
        self.canvas.spiders.remove(self)
        self.delete_me()
        if self.receiver.listener:
            if action != "sub_diagram":
                self.receiver.receiver_callback('delete_spider', wire_id=self.id, connection_id=self.id)

    def close_menu(self):
        if self.context_menu:
            self.context_menu.destroy()

    def add_wire(self, wire):
        self.wires.append(wire)

    # MOVING, CLICKING ETC.
    def on_press(self):
        for item in self.canvas.selector.selected_items:
            item.deselect()
        self.canvas.selector.selected_items.clear()
        self.select()
        self.canvas.selector.selected_items.append(self)
        if not self.canvas.draw_wire_mode:
            if self not in self.canvas.selector.selected_items:
                self.select()
                self.canvas.selector.selected_items.append(self)

    def on_drag(self, event):
        if self.canvas.pulling_wire:
            return

        go_to_y = event.y
        go_to_x = self.x
        move_legal = False
        if not self.is_illegal_move(event.x):
            go_to_x = event.x
            move_legal = True

        col_preset = None

        # snapping into place
        # TODO bug here with box and 2 spiders
        found = False
        for box in self.canvas.boxes:
            if abs(box.x + box.size[0] / 2 - go_to_x) < box.size[0] / 2 + self.r and move_legal:
                go_to_x = box.x + box.size[0] / 2
                self.snapped_x = round(float(go_to_x), 4)
                if self.prev_snapped is None:
                    self.prev_snapped = self.snapped_x

                col_preset = box

                found = True
        for spider in self.canvas.spiders:
            if spider == self:
                continue

            cancel = False
            for wire in spider.wires:
                if wire.end_connection == self or wire.start_connection == self:
                    cancel = True
            if cancel:
                continue

            if abs(spider.location[0] - go_to_x) < self.r + spider.r and move_legal:
                go_to_x = spider.location[0]
                self.snapped_x = round(float(go_to_x), 4)
                if self.prev_snapped is None:
                    self.prev_snapped = self.snapped_x

                col_preset = spider

                found = True

        for existing_snapped_x in self.canvas.columns.keys():
            if self.snapped_x:
                if abs(self.snapped_x - existing_snapped_x) < 0.5:
                    self.snapped_x = existing_snapped_x

        if found:

            if self.snapped_x not in self.canvas.columns:
                self.canvas.columns[self.snapped_x] = [col_preset]
                col_preset.snapped_x = self.snapped_x
            if self not in self.canvas.columns[self.snapped_x]:
                self.canvas.columns[self.snapped_x].append(self)

            for column_item in self.canvas.columns[self.snapped_x]:
                if column_item == self:
                    continue
                if isinstance(column_item, Box):
                    if (go_to_y + self.r >= column_item.y
                            and go_to_y - self.r <= column_item.y + column_item.size[1]):
                        if not self.is_snapped:
                            go_to_y = self.find_space_y(self.snapped_x, go_to_y)
                        else:
                            return
                else:
                    if (go_to_y + self.r >= column_item.y - column_item.r
                            and go_to_y - self.r <= column_item.y + column_item.r):
                        if not self.is_snapped:
                            go_to_y = self.find_space_y(self.snapped_x, go_to_y)
                        else:
                            return

        self.canvas.setup_column_removal(self, found)

        self.is_snapped = found
        self.prev_snapped = self.snapped_x

        self.location = [go_to_x, go_to_y]
        self.x = go_to_x
        self.y = go_to_y

        self.canvas.coords(self.circle, self.x - self.r, self.y - self.r, self.x + self.r,
                           self.y + self.r)
        [w.update() for w in self.wires]

    def find_space_y(self, go_to_x, go_to_y):
        objects_by_distance = sorted(self.canvas.columns[float(go_to_x)], key=lambda x: abs(self.y - x.y))
        for item in objects_by_distance:
            if item == self:
                continue
            y_up = True
            y_down = True

            if isinstance(item, Box):
                go_to_y_up = item.y - self.r - 1
                go_to_y_down = item.y + item.size[1] + self.r + 1
            else:
                go_to_y_up = item.y - item.r - self.r - 1
                go_to_y_down = item.y + item.r + self.r + 1

            for component in objects_by_distance:
                if component == self or component == item:
                    continue

                upper_y, lower_y = self.canvas.get_upper_lower_edges(component)

                if go_to_y_up + self.r >= upper_y and go_to_y_up - self.r <= lower_y:
                    y_up = False
                if go_to_y_down + self.r >= upper_y and go_to_y_down - self.r <= lower_y:
                    y_down = False

            up_or_down = self.canvas.check_if_up_or_down(y_up, y_down, go_to_y_up, go_to_y_down, self)
            if up_or_down[0]:
                go_to_y = up_or_down[1]
                break
            else:
                continue
        return go_to_y

    def is_illegal_move(self, new_x):
        for connection in list(filter(lambda x: (x is not None and x != self),
                                      [w.end_connection for w in self.wires] + [w.start_connection for w in
                                                                                self.wires])):
            if connection.side == "spider" and abs(new_x - connection.location[0]) < 2 * self.r:
                return True
            if connection.side == "left":
                if new_x + self.r >= connection.location[0] - connection.width_between_boxes:
                    return True
            if connection.side == "right":
                if new_x - self.r <= connection.location[0] - connection.width_between_boxes:
                    return True
        return False

    def remove_wire(self, wire=None):
        if wire and wire in self.wires:
            self.wires.remove(wire)
