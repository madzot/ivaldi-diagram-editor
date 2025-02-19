import tkinter as tk


def curved_line(start, end, det=15):
    sx = start[0]
    sy = start[1]
    dx = end[0] - sx
    dy = end[1] - sy

    coordinates = [0] * (det * 2 + 2)
    for i in range(det + 1):
        t = i / det
        coordinates[i * 2] = sx + dx * t
        coordinates[i * 2 + 1] = sy + dy * (3 * t ** 2 - 2 * t ** 3)
    return coordinates


class Wire:
    def __init__(self, canvas, start_connection, receiver, end_connection, id_=None, temporary=False):
        self.canvas = canvas
        self.context_menu = tk.Menu(self.canvas, tearoff=0)
        self.start_connection = start_connection
        self.end_connection = end_connection
        self.line = None
        self.wire_width = 3
        if not id_:
            self.id = id(self)
        else:
            self.id = id_
        self.receiver = receiver
        self.is_temporary = temporary
        if not temporary and not self.canvas.search:
            self.handle_wire_addition_callback()
        self.update()

    def delete_self(self, action=None):
        self.start_connection.remove_wire(self)
        self.end_connection.remove_wire(self)
        self.canvas.delete(self.line)
        if not self.is_temporary:
            if self in self.canvas.wires:
                self.canvas.wires.remove(self)
        if not self.is_temporary and not self.canvas.search:
            self.handle_wire_deletion_callback(action)

    def select(self):
        self.canvas.itemconfig(self.line, fill="green")

    def search_highlight_secondary(self):
        self.canvas.itemconfig(self.line, fill="orange")
        self.canvas.search_result_highlights.append(self)

    def search_highlight_primary(self):
        self.canvas.itemconfig(self.line, fill="cyan")
        self.canvas.search_result_highlights.append(self)

    def deselect(self):
        # make sure connections have wires attached after select and deselect as copying between canvasses can remove
        self.start_connection.add_wire(self)
        self.end_connection.add_wire(self)
        self.canvas.itemconfig(self.line, fill="black")

    def update(self):
        if self.end_connection:
            if self.line:
                self.canvas.coords(self.line,
                                   *curved_line(self.start_connection.location, self.end_connection.location))
            else:
                self.line = self.canvas.create_line(
                    *curved_line(self.start_connection.location, self.end_connection.location),
                    fill="black", width=self.wire_width)
                self.canvas.tag_bind(self.line, '<ButtonPress-3>', self.show_context_menu)
            self.canvas.tag_lower(self.line)

    def show_context_menu(self, event):
        self.canvas.is_wire_pressed = True
        if not self.is_temporary:
            self.close_menu()
            self.context_menu = tk.Menu(self.canvas, tearoff=0)
            self.context_menu.add_command(label="Create Spider",
                                          command=lambda bound_arg=event: self.create_spider(event))
            self.context_menu.add_command(label="Delete wire", command=self.delete_self)
            self.context_menu.add_command(label="Cancel")
            self.context_menu.post(event.x_root, event.y_root)

    def create_spider(self, event):
        x, y = event.x, event.y
        self.delete_self()
        self.canvas.add_spider_with_wires(self.start_connection, self.end_connection, x, y)

    def close_menu(self):
        if self.context_menu:
            self.context_menu.destroy()

    # BE callback methods
    def connection_data_optimizer(self):
        start_conn_data = [self.start_connection.index, None, self.start_connection.side, self.start_connection.id]
        end_conn_data = [self.end_connection.index, None, self.end_connection.side, self.end_connection.id]

        if self.start_connection.box:
            start_conn_data[1] = self.start_connection.box.id
        if self.end_connection.box:
            end_conn_data[1] = self.end_connection.box.id
        return start_conn_data, end_conn_data

    # BE callback methods
    def handle_wire_addition_callback(self):
        if not self.receiver.listener or self.canvas.search:
            return

        start_conn_data, end_conn_data = self.connection_data_optimizer()

        if self.start_connection.side == 'spider':
            self.receiver.receiver_callback("wire_add", wire_id=self.id,
                                            start_connection=start_conn_data[:3],
                                            connection_id=self.start_connection.id,
                                            end_connection=end_conn_data)
        elif self.end_connection.side == 'spider':
            self.receiver.receiver_callback("wire_add", wire_id=self.id,
                                            start_connection=start_conn_data,
                                            connection_id=self.end_connection.id,
                                            end_connection=end_conn_data[:3])
        else:
            self.receiver.receiver_callback("wire_add", wire_id=self.id,
                                            start_connection=start_conn_data[:3],
                                            connection_id=self.start_connection.id)
            self.add_end_connection(self.end_connection)

    # BE callback methods
    def handle_wire_deletion_callback(self, action):
        if not self.receiver.listener:
            return
        if action != "sub_diagram":
            start_conn_data, end_conn_data = self.connection_data_optimizer()
            if self.start_connection.side == 'spider':
                if self.end_connection.box is None:
                    self.receiver.receiver_callback("wire_delete", wire_id=self.start_connection.id,
                                                    end_connection=end_conn_data)
                else:
                    self.receiver.receiver_callback("wire_delete", wire_id=self.start_connection.id,
                                                    end_connection=end_conn_data)
            elif self.end_connection.side == 'spider':
                if self.start_connection.box is None:
                    self.receiver.receiver_callback("wire_delete", wire_id=self.end_connection.id,
                                                    start_connection=start_conn_data)
                else:
                    self.receiver.receiver_callback("wire_delete", wire_id=self.end_connection.id,
                                                    start_connection=start_conn_data)
            else:
                self.receiver.receiver_callback("wire_delete", wire_id=self.id)

    # BE callback methods
    def add_end_connection(self, connection):
        self.end_connection = connection
        if connection.box and self.receiver.listener:
            self.receiver.receiver_callback("wire_add", wire_id=self.id,
                                            start_connection=[connection.index, connection.box.id, connection.side],
                                            connection_id=connection.id)
        elif connection.box is None and self.receiver.listener and self.start_connection.box is not None:
            self.receiver.receiver_callback("wire_add", wire_id=self.id,
                                            start_connection=[connection.index, None, connection.side],
                                            connection_id=connection.id)
