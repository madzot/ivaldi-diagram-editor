import tkinter as tk

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
    def on_press(self):
        if not self.canvas.draw_wire_mode:
            if self not in self.canvas.selector.selected_items:
                self.select()
                self.canvas.selector.selected_items.append(self)

    def on_drag(self, event):
        self.y = event.y
        move_legal = False
        if not self.is_illegal_move(event.x):
            self.x = event.x
            move_legal = True

        # snapping into place
        # TODO bug here with box and 2 spiders
        found = False
        for box in self.canvas.boxes:
            if abs(box.x + box.size[0] / 2 - event.x) < box.size[0] / 2 + self.r and move_legal:
                if self.y + self.r >= box.y and self.y - self.r <= box.y + box.size[1]:
                    if not self.is_snapped:
                        if (box.y * 2 + box.size[1]) / 2 <= self.y:
                            self.y = box.y + box.size[1] + self.r + 1
                        else:
                            self.y = box.y - self.r - 1
                    else:
                        return
                self.x = box.x + box.size[0] / 2
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
                if self.y + self.r >= spider.y - spider.r and self.y <= spider.y + self.r + spider.r:
                    if not self.is_snapped:
                        if spider.y <= self.y:
                            self.y = spider.y + spider.r * 2 + 1
                        else:
                            self.y = spider.y - spider.r * 2 - 1
                    else:
                        return
                self.x = spider.location[0]
                found = True
        self.is_snapped = found

        self.location = [self.x, self.y]

        self.canvas.coords(self.circle, self.x - self.r, self.y - self.r, self.x + self.r,
                           self.y + self.r)
        [w.update() for w in self.wires]

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
