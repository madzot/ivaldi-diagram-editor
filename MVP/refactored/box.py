import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog

from MVP.refactored.code_editor import CodeEditor
from MVP.refactored.backend.box_functions.box_function import BoxFunction, functions
from MVP.refactored.connection import Connection


class Box:
    def __init__(self, canvas, x, y, receiver, size=(60, 60), id_=None):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.size = size
        self.x_dif = 0
        self.y_dif = 0
        self.connections: list[Connection] = []
        self.label = None
        self.label_text = ""
        self.wires = []
        if not id_:
            self.id = id(self)
        else:
            self.id = id_
        self.context_menu = tk.Menu(self.canvas, tearoff=0)
        self.rect = self.canvas.create_rectangle(self.x, self.y, self.x + self.size[0], self.y + self.size[1],
                                                 outline="black", fill="white")
        self.resize_handle = self.canvas.create_rectangle(self.x + self.size[0] - 10, self.y + self.size[1] - 10,
                                                          self.x + self.size[0], self.y + self.size[1],
                                                          outline="black", fill="black")
        self.locked = False
        self.bind_events()
        self.sub_diagram = None
        self.receiver = receiver
        if self.receiver.listener:
            self.receiver.receiver_callback("box_add", generator_id=self.id)
            if self.canvas.diagram_source_box:
                self.receiver.receiver_callback("sub_box", generator_id=self.id,
                                                connection_id=self.canvas.diagram_source_box.id)

        self.is_snapped = False
        self.snapped_x = None
        self.prev_snapped = None
        self.box_function: BoxFunction = None

    def set_box_function(self, function: BoxFunction):
        self.box_function = function

    def get_box_function(self) -> BoxFunction:
        return self.box_function

    def set_id(self, id_):
        if self.receiver.listener:
            self.receiver.receiver_callback("box_swap_id", generator_id=self.id, connection_id=id_)
            if self.canvas.diagram_source_box:
                self.receiver.receiver_callback("sub_box", generator_id=self.id,
                                                connection_id=self.canvas.diagram_source_box.id)
        self.id = id_
        # TODO if box changes id, so corresponding node should also change id

    def bind_events(self):
        self.canvas.tag_bind(self.rect, '<ButtonPress-1>', self.on_press)
        self.canvas.tag_bind(self.rect, '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind(self.rect, '<ButtonPress-3>', self.show_context_menu)
        self.canvas.tag_bind(self.resize_handle, '<ButtonPress-1>', self.on_resize_press)
        self.canvas.tag_bind(self.resize_handle, '<B1-Motion>', self.on_resize_drag)
        self.canvas.tag_bind(self.rect, '<Double-Button-1>', self.set_inputs_outputs)

    def show_context_menu(self, event):
        self.close_menu()
        self.context_menu = tk.Menu(self.canvas, tearoff=0)

        if not self.sub_diagram:
            self.context_menu.add_command(label="Add code", command=self.open_editor)
            if not self.label_text.strip():
                self.context_menu.entryconfig("Add code", state="disabled", label="Label needed to add code")

        if not self.locked and not self.sub_diagram:
            self.context_menu.add_command(label="Add Left Connection", command=self.add_left_connection)
            self.context_menu.add_command(label="Add Right Connection", command=self.add_right_connection)

            for circle in self.connections:
                self.context_menu.add_command(label=f"Remove {circle.side} connection nr {circle.index}",
                                              command=lambda bound_arg=circle: self.remove_connection(bound_arg))

        if self.locked:
            self.context_menu.add_command(label="Unlock Box", command=self.unlock_box)
        if not self.locked:
            self.context_menu.add_command(label="Edit label", command=self.edit_label)
            self.context_menu.add_command(label="Edit Sub-Diagram", command=self.edit_sub_diagram)
            self.context_menu.add_command(label="Lock Box", command=self.lock_box)
        self.context_menu.add_command(label="Save Box to Menu", command=self.save_box_to_menu)
        self.context_menu.add_command(label="Add function", command=lambda: self.add_function(event))
        self.context_menu.add_command(label="Delete Box", command=self.delete_box)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Cancel")
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def add_function(self, event):
        menu = tk.Menu(self.canvas, tearoff=0)
        for name in functions:
            menu.add_command(label=name, command=lambda x=name: self.set_function(x))
        menu.add_command(label="Add custom function", command=self.show_add_custom_function_menu)
        menu.post(event.x_root, event.y_root)

    def show_add_custom_function_menu(self):
        file = filedialog.askopenfile(title="Send a python script, that contains function \"invoke\"",
                                      filetypes=(("Python script", "*.py"),))
        if file:
            self.set_function(file.name, file.read())

    def set_function(self, name, code=None):
        self.box_function = BoxFunction(name, code)

    def count_inputs(self) -> int:
        count = 0
        for connection in self.connections:
            if connection.side == "left":
                count += 1
        return count

    def open_editor(self):
        CodeEditor(self)

    def count_outputs(self) -> int:
        count = 0
        for connection in self.connections:
            if connection.side == "right":
                count += 1
        return count

    def get_inputs(self) -> list[int]:
        inputs = []
        for connection in self.connections:
            if connection.side == "left":
                inputs.append(connection.wire.id)
        return inputs

    def get_outputs(self) -> list[int]:
        outputs = []
        for connection in self.connections:
            if connection.side == "right":
                outputs.append(connection.wire.id)
        return outputs

    def save_box_to_menu(self):
        if not self.label_text:
            self.edit_label()
        if not self.label_text:
            return
        self.canvas.main_diagram.save_box_to_diagram_menu(self)

    def set_inputs_outputs(self, _):
        # TODO idea: double click on box with sub diagram opens the sub-diagram?
        if self.locked or self.sub_diagram:
            return
        # ask for inputs amount
        inputs = simpledialog.askstring(title="Inputs (left connections)", prompt="Enter amount")
        if inputs and not inputs.isdigit():
            while True:
                inputs = simpledialog.askstring(title="Inputs (left connections)",
                                                prompt="Enter amount, must be integer!")
                if inputs:
                    if inputs.isdigit():
                        break
                else:
                    break

        # ask for outputs amount
        outputs = simpledialog.askstring(title="Outputs (right connections)", prompt="Enter amount")
        if outputs and not outputs.isdigit():
            while True:
                outputs = simpledialog.askstring(title="Outputs (right connections)",
                                                 prompt="Enter amount, must be integer!")
                if outputs:
                    if outputs.isdigit():
                        break
                else:
                    break
        # select connections to remove

        to_be_removed = []
        for c in self.connections:
            if c.side == "right" and outputs:
                to_be_removed.append(c)
            if c.side == "left" and inputs:
                to_be_removed.append(c)

        # remove selected connectionsS
        for c in to_be_removed:
            if c.has_wire:
                c.wire.delete_from_canvas()

            c.delete_me()
            self.connections.remove(c)
            self.update_connections()
            self.update_wires()

        # add new connections
        self.receiver.receiver_callback("box_remove_connection_all", generator_id=self.id)
        if outputs:
            for _ in range(int(outputs)):
                self.add_right_connection()
        if inputs:
            for _ in range(int(inputs)):
                self.add_left_connection()

    def edit_sub_diagram(self, save_to_canvasses=True, add_boxes=True):
        from MVP.refactored.custom_canvas import CustomCanvas
        if self.receiver.listener:
            self.receiver.receiver_callback("compound", generator_id=self.id)
        if not self.sub_diagram:
            self.sub_diagram = CustomCanvas(self.canvas.main_diagram, self, self.receiver, self.canvas.main_diagram,
                                            self.canvas, add_boxes, self.id, highlightthickness=0)
            self.canvas.itemconfig(self.rect, fill="#dfecf2")
            if save_to_canvasses:
                name = self.label_text
                if not name:
                    name = str(self.sub_diagram.id)[-6:]
                    self.set_label(name)
                self.sub_diagram.set_name(name)
                self.canvas.main_diagram.add_canvas(self.sub_diagram)
                self.canvas.main_diagram.change_canvas_name(self.sub_diagram)
                self.canvas.main_diagram.switch_canvas(self.sub_diagram)

            return self.sub_diagram
        else:
            self.canvas.main_diagram.switch_canvas(self.sub_diagram)
            return self.sub_diagram

    def close_menu(self):
        if self.context_menu:
            self.context_menu.destroy()

    # MOVING, CLICKING ETC.
    def on_press(self, event):
        for item in self.canvas.selector.selected_items:
            item.deselect()
        self.canvas.selector.selected_items.clear()
        self.select()
        self.canvas.selector.selected_items.append(self)
        self.start_x = event.x
        self.start_y = event.y
        self.x_dif = event.x - self.x
        self.y_dif = event.y - self.y

    def on_drag(self, event):

        self.start_x = event.x
        self.start_y = event.y

        go_to_x = event.x - self.x_dif
        go_to_y = event.y - self.y_dif

        col_preset = None

        # snapping into place
        found = False
        for box in self.canvas.boxes:
            if box == self:
                continue

            if abs(box.x + box.size[0] / 2 - (go_to_x + self.size[0] / 2)) < box.size[0] / 2 + self.size[0] / 2:

                go_to_x = box.x + box.size[0] / 2 - +self.size[0] / 2
                self.snapped_x = float(go_to_x + self.size[0] / 2)

                col_preset = box

                found = True
        for spider in self.canvas.spiders:

            if abs(spider.location[0] - (go_to_x + self.size[0] / 2)) < self.size[0] / 2 + spider.r:
                go_to_x = spider.x - +self.size[0] / 2
                self.snapped_x = float(spider.x)
                if self.prev_snapped is None:
                    self.prev_snapped = self.snapped_x

                col_preset = spider

                found = True

        if found:

            if self.snapped_x not in self.canvas.columns:
                self.canvas.columns[self.snapped_x] = [col_preset]
            if self not in self.canvas.columns[self.snapped_x]:
                self.canvas.columns[self.snapped_x].append(self)

            for column_item in self.canvas.columns[self.snapped_x]:
                if column_item == self:
                    continue
                if isinstance(column_item, Box):
                    if (go_to_y + self.size[1] >= column_item.y
                            and go_to_y <= column_item.y + column_item.size[1]):
                        if not self.is_snapped:
                            go_to_y = self.find_space_y(self.snapped_x, go_to_y)
                        else:
                            return
                else:
                    if (go_to_y + self.size[1] >= column_item.y - column_item.r
                            and go_to_y <= column_item.y + column_item.r):
                        if not self.is_snapped:
                            go_to_y = self.find_space_y(self.snapped_x, go_to_y)
                        else:
                            return

        self.canvas.setup_column_removal(self, found)

        self.is_snapped = found
        self.prev_snapped = self.snapped_x

        self.move(go_to_x, go_to_y)
        self.move_label()

    def find_space_y(self, go_to_x, go_to_y):
        objects_by_distance = sorted(self.canvas.columns[float(go_to_x)], key=lambda x: abs(self.y - x.y))
        for item in objects_by_distance:
            if item == self:
                continue
            y_up = True
            y_down = True

            if isinstance(item, Box):
                go_to_y_up = item.y - self.size[1] - 1
                go_to_y_down = item.y + item.size[1] + 1
            else:
                go_to_y_up = item.y - item.r - self.size[1] - 1
                go_to_y_down = item.y + item.r + 1

            for component in objects_by_distance:
                if component == self or component == item:
                    continue

                upper_y, lower_y = self.canvas.get_upper_lower_edges(component)

                if go_to_y_up + self.size[1] >= upper_y and go_to_y_up <= lower_y:
                    y_up = False
                if go_to_y_down + self.size[1] >= upper_y and go_to_y_down <= lower_y:
                    y_down = False

            up_or_down = self.canvas.check_if_up_or_down(y_up, y_down, go_to_y_up, go_to_y_down, self)
            if up_or_down[0]:
                go_to_y = up_or_down[1]
                break
            else:
                continue
        return go_to_y

    def on_resize_drag(self, event):
        resize_x = self.x + self.size[0] - 10
        resize_y = self.y + self.size[1] - 10
        dx = event.x - self.start_x
        dy = event.y - self.start_y

        if dx > 0 and not resize_x <= event.x:
            dx = 0

        if dy > 0 and not resize_y <= event.y:
            dy = 0

        self.start_x = event.x
        self.start_y = event.y
        new_size_x = max(20, self.size[0] + dx)
        new_size_y = max(20, self.size[1] + dy)
        self.update_size(new_size_x, new_size_y)
        self.move_label()

    def resize_by_connections(self):
        # TODO resize by label too if needed
        nr_cs = max([c.index for c in self.connections] + [0])
        height = max([50 * nr_cs, 50])
        if self.size[1] < height:
            self.update_size(self.size[0], height)
            self.move_label()

    def move_label(self):
        if self.label:
            self.canvas.coords(self.label, self.x + self.size[0] / 2, self.y + self.size[1] / 2)

    def edit_label(self):
        # TODO check if label is already in use and if definitions match
        self.label_text = simpledialog.askstring("Input", "Enter label:", initialvalue=self.label_text)
        if self.receiver.listener:
            self.receiver.receiver_callback("box_add_operator", generator_id=self.id, operator=self.label_text)
        if not self.label:
            self.label = self.canvas.create_text((self.x + self.size[0] / 2, self.y + self.size[1] / 2),
                                                 text=self.label_text, fill="black", font=('Helvetica', 14))

        else:
            self.canvas.itemconfig(self.label, text=self.label_text)
        if self.label_text:
            if self.sub_diagram:
                self.sub_diagram.set_name(self.label_text)
                self.canvas.main_diagram.change_canvas_name(self.sub_diagram)

        self.canvas.tag_bind(self.label, '<ButtonPress-1>', self.on_press)
        self.canvas.tag_bind(self.label, '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind(self.label, '<ButtonPress-3>', self.show_context_menu)
        self.canvas.tag_bind(self.label, '<Double-Button-1>', self.set_inputs_outputs)

    def set_label(self, new_label):
        self.label_text = new_label
        if self.receiver.listener:
            self.receiver.receiver_callback("box_add_operator", generator_id=self.id, operator=self.label_text)
        if not self.label:
            self.label = self.canvas.create_text((self.x + self.size[0] / 2, self.y + self.size[1] / 2),
                                                 text=self.label_text, fill="black", font=('Helvetica', 14))
        else:
            self.canvas.itemconfig(self.label, text=self.label_text)
        self.canvas.tag_bind(self.label, '<ButtonPress-1>', self.on_press)
        self.canvas.tag_bind(self.label, '<B1-Motion>', self.on_drag)
        self.canvas.tag_bind(self.label, '<ButtonPress-3>', self.show_context_menu)
        self.canvas.tag_bind(self.label, '<Double-Button-1>', self.set_inputs_outputs)

    def on_resize_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def move(self, new_x, new_y):
        is_bad = False
        for connection in self.connections:
            if connection.has_wire and self.is_illegal_move(connection, new_x):
                is_bad = True
                break
        if is_bad:
            self.y = new_y
            self.update_position()
            self.update_connections()
            self.update_wires()
        else:
            self.x = new_x
            self.y = new_y
            self.update_position()
            self.update_connections()
            self.update_wires()

    def select(self):
        self.canvas.itemconfig(self.rect, outline="green")
        [c.select() for c in self.connections]

    def deselect(self):
        self.canvas.itemconfig(self.rect, outline="black")
        [c.deselect() for c in self.connections]

    def lock_box(self):
        self.locked = True

    def unlock_box(self):
        self.locked = False

    def delete_sub_diagram(self):
        self.sub_diagram.custom_canvas.delete_everything()
        self.canvas.itemconfig(self.rect, fill="white")
        self.sub_diagram = None
        self.locked = False
        self.canvas.delete(self.label)
        self.label = None
        self.label_text = ""

    # UPDATES
    def update_size(self, new_size_x, new_size_y):
        self.size = (new_size_x, new_size_y)
        self.update_position()
        self.update_connections()
        self.update_wires()

    def update_position(self):
        self.canvas.coords(self.rect, self.x, self.y, self.x + self.size[0], self.y + self.size[1])
        self.canvas.coords(self.resize_handle, self.x + self.size[0] - 10, self.y + self.size[1] - 10,
                           self.x + self.size[0], self.y + self.size[1])

    def update_connections(self):
        for c in self.connections:
            conn_x, conn_y = self.get_connection_coordinates(c.side, c.index)
            c.move_to((conn_x, conn_y))

    def update_wires(self):
        [wire.update() for wire in self.wires]

    # ADD TO/REMOVE FROM CANVAS
    def add_wire(self, wire):
        self.wires.append(wire)

    def add_left_connection(self, id_=None):
        i = self.get_new_left_index()
        conn_x, conn_y = self.get_connection_coordinates("left", i)
        connection = Connection(self, i, "left", (conn_x, conn_y), self.canvas, id_=id_)
        self.connections.append(connection)

        self.update_connections()
        self.update_wires()
        if self.receiver.listener:
            self.receiver.receiver_callback("box_add_left", generator_id=self.id, connection_nr=i,
                                            connection_id=connection.id)

        self.resize_by_connections()
        return connection

    def add_right_connection(self, id_=None):
        i = self.get_new_right_index()
        conn_x, conn_y = self.get_connection_coordinates("right", i)
        connection = Connection(self, i, "right", (conn_x, conn_y), self.canvas, id_=id_)

        self.connections.append(connection)
        self.update_connections()
        self.update_wires()
        if self.receiver.listener:
            self.receiver.receiver_callback("box_add_right", generator_id=self.id, connection_nr=i,
                                            connection_id=connection.id)
        self.resize_by_connections()
        return connection

    def remove_connection(self, circle):
        for c in self.connections:
            if c.index > circle.index and circle.side == c.side:
                c.lessen_index_by_one()
        if self.receiver.listener:
            self.receiver.receiver_callback("box_remove_connection", generator_id=self.id, connection_nr=circle.index,
                                            generator_side=circle.side)

        self.connections.remove(circle)
        circle.delete_me()
        self.update_connections()
        self.update_wires()
        self.resize_by_connections()

    def delete_box(self, keep_sub_diagram=False, action=None):
        for c in self.connections:
            if c.has_wire:
                c.wire.delete_from_canvas()
            c.delete_me()

        self.canvas.delete(self.rect)
        self.canvas.delete(self.resize_handle)

        if self.snapped_x and self.snapped_x in self.canvas.columns:
            self.canvas.columns[self.snapped_x].remove(self)
            if len(self.canvas.columns[self.snapped_x]) == 1:
                self.canvas.columns[self.snapped_x][0].snapped_x = None
                self.canvas.columns[self.snapped_x][0].is_snapped = False
                self.canvas.columns.pop(self.snapped_x, None)
            self.snapped_x = None
        if self in self.canvas.boxes:
            self.canvas.boxes.remove(self)
        self.canvas.delete(self.label)
        if self.sub_diagram and not keep_sub_diagram:
            self.canvas.main_diagram.del_from_canvasses(self.sub_diagram)
        if self.receiver.listener:
            if action != "sub_diagram":
                self.receiver.receiver_callback("box_delete", generator_id=self.id)

    # BOOLEANS
    def is_illegal_move(self, connection, new_x):
        wire = connection.wire
        if connection.side == "left":
            if connection == wire.start_connection:
                other_connection = wire.end_connection
            else:
                other_connection = wire.start_connection
            other_x = other_connection.location[0]
            if other_x + other_connection.width_between_boxes >= new_x:
                return True

        if connection.side == "right":
            if connection == wire.start_connection:
                other_connection = wire.end_connection
            else:
                other_connection = wire.start_connection

            other_x = other_connection.location[0]
            if other_x - other_connection.width_between_boxes <= new_x + self.size[0]:
                return True
        return False

    def has_left_connections(self):
        for c in self.connections:
            if c.side == "left":
                return True
        return False

    def has_right_connections(self):
        for c in self.connections:
            if c.side == "right":
                return True
        return False

    # HELPERS
    def get_connection_coordinates(self, side, index):
        if side == "left":
            i = self.get_new_left_index()
            return self.x, self.y + (index + 1) * self.size[1] / (i + 1)

        elif side == "right":
            i = self.get_new_right_index()
            return self.x + self.size[0], self.y + (index + 1) * self.size[1] / (i + 1)

    def get_new_left_index(self):
        if not self.has_left_connections():
            return 0
        return max([c.index if c.side == "left" else 0 for c in self.connections]) + 1

    def get_new_right_index(self):
        if not self.has_right_connections():
            return 0
        return max([c.index if c.side == "right" else 0 for c in self.connections]) + 1
