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

    def is_spider(self):
        return True

    def bind_events(self):
        self.canvas.tag_bind(self.circle, '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind(self.circle, '<ButtonPress-3>', self.show_context_menu)

    def show_context_menu(self, event):
        self.close_menu()
        self.context_menu = tk.Menu(self.canvas, tearoff=0)

        self.context_menu.add_command(label="Delete Spider", command=self.delete_spider)
        self.context_menu.add_command(label="Cancel")

        self.context_menu.post(event.x_root, event.y_root)

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

    def on_drag(self, event):

        go_to_y = event.y
        go_to_x = self.x
        move_legal = False
        if not self.is_illegal_move(event.x):
            go_to_x = event.x
            move_legal = True

        # snapping into place
        # TODO bug here with box and 2 spiders
        found = False
        for box in self.canvas.boxes:
            if abs(box.x + box.size[0] / 2 - event.x) < box.size[0] / 2 + self.r and move_legal:

                go_to_x = box.x + box.size[0] / 2
                self.snapped_x = float(go_to_x)

                if self.snapped_x not in self.canvas.columns:
                    self.canvas.columns[self.snapped_x] = [box]
                if self not in self.canvas.columns[self.snapped_x]:
                    self.canvas.columns[self.snapped_x].append(self)

                if go_to_y + self.r >= box.y and go_to_y - self.r <= box.y + box.size[1]:
                    if not self.is_snapped:
                        go_to_y = self.find_space_y(self.snapped_x, go_to_y)
                    else:
                        return

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

            if abs(spider.location[0] - event.x) < self.r + spider.r and move_legal:
                go_to_x = spider.location[0]
                self.snapped_x = go_to_x

                if self.snapped_x not in self.canvas.columns:
                    self.canvas.columns[self.snapped_x] = [spider]
                if self not in self.canvas.columns[self.snapped_x]:
                    self.canvas.columns[self.snapped_x].append(self)

                if go_to_y + self.r >= spider.y - spider.r and go_to_y - self.r <= spider.y + spider.r:
                    if not self.is_snapped:
                        go_to_y = self.find_space_y(self.snapped_x, go_to_y)
                    else:
                        return
                found = True
        self.is_snapped = found
        if not found and self.snapped_x:
            self.canvas.columns[self.snapped_x].remove(self)
            if len(self.canvas.columns[self.snapped_x]) == 1:
                self.canvas.columns[self.snapped_x][0].snapped_x = None
                self.canvas.columns[self.snapped_x][0].is_snapped = False
                self.canvas.columns.pop(self.snapped_x, None)
            self.snapped_x = None

        self.location = [go_to_x, go_to_y]
        self.x = go_to_x
        self.y = go_to_y

        self.canvas.coords(self.circle, self.x - self.r, self.y - self.r, self.x + self.r,
                           self.y + self.r)
        [w.update() for w in self.wires]

    def find_space_y(self, go_to_x, go_to_y):
        print("adada")
        objects_by_distance = sorted(self.canvas.columns[float(go_to_x)], key=lambda x: abs(self.y - x.y))
        print(objects_by_distance)
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

                if isinstance(component, Box):
                    upper_y = component.y
                    lower_y = component.y + component.size[1]
                else:
                    upper_y = component.y - component.r
                    lower_y = component.y + component.r

                print()
                print(go_to_y_up)
                print(go_to_y_down)
                print(upper_y)
                print(lower_y)
                print()
                if go_to_y_up + self.r >= upper_y and go_to_y_up - self.r <= lower_y:
                    y_up = False
                if go_to_y_down + self.r >= upper_y and go_to_y_down - self.r <= lower_y:
                    y_down = False

            if y_up and not y_down:
                go_to_y = go_to_y_up
                print("FINISHING FIRST")
                break
            elif y_down and not y_up:
                print("FINISHING SECOND")
                go_to_y = go_to_y_down
                break
            elif not y_up and not y_down:
                continue
            elif y_down and y_up:
                print("FINISHING THIRD")
                distance_to_y_up = abs(self.y - go_to_y_up)
                distance_to_y_down = abs(self.y - go_to_y_down)
                if distance_to_y_up < distance_to_y_down:
                    go_to_y = go_to_y_up
                else:
                    go_to_y = go_to_y_down
                break
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
