import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox as mb

from PIL import Image

from MVP.refactored.box import Box
from MVP.refactored.connection import Connection
from MVP.refactored.spider import Spider
from MVP.refactored.util.copier import Copier
from MVP.refactored.wire import Wire


class CustomCanvas(tk.Canvas):
    def __init__(self, master, diagram_source_box, receiver, main_diagram, parent_diagram, add_boxes, **kwargs):
        super().__init__(master, **kwargs)
        screen_width_min = round(main_diagram.winfo_screenwidth() / 1.5)
        screen_height_min = round(main_diagram.winfo_screenheight() / 1.5)
        self.configure(bg='white', width=screen_width_min, height=screen_height_min)

        self.parent_diagram = parent_diagram
        self.main_diagram = main_diagram
        self.master = master
        self.boxes: list[Box] = []
        self.outputs: list[Connection] = []
        self.inputs: list[Connection] = []
        self.spiders: list[Spider] = []
        self.wires: list[Wire] = []
        self.receiver = receiver
        self.current_wire_start = None
        self.current_wire = None
        self.draw_wire_mode = False
        self.bind('<Button-1>', self.on_canvas_click)
        self.bind("<Configure>", self.on_canvas_resize)
        self.diagram_source_box = diagram_source_box  # Only here if canvas is sub-diagram
        self.id = id(self)
        self.name = self.create_text(0, 0, text=str(self.id)[-6:], fill="black", font='Helvetica 15 bold')
        self.name_text = str(self.id)[-6:]
        self.set_name(str(self.id))
        self.selectBox = None
        self.bind("<ButtonPress-1>", self.__select_start__)
        self.bind("<B1-Motion>", self.__select_motion__)
        self.bind("<ButtonRelease-1>", self.__select_release__)
        self.selecting = False
        self.copier = Copier()
        if add_boxes and diagram_source_box:
            for connection in diagram_source_box.connections:
                if connection.side == "left":
                    self.add_diagram_input()
                if connection.side == "right":
                    self.add_diagram_output()
        self.set_name(self.name)
        self.columns = {}

    def set_name(self, name):
        w = self.winfo_width()
        self.coords(self.name, w / 2, 12)
        self.itemconfig(self.name, text=name)
        self.name_text = name

    # binding for drag select
    def __select_start__(self, event):
        [box.close_menu() for box in self.boxes]
        [wire.close_menu() for wire in self.wires]
        [(spider.close_menu(), self.tag_raise(spider.circle)) for spider in self.spiders]

        [i.close_menu() for i in self.inputs]
        [o.close_menu() for o in self.outputs]
        [[c.close_menu() for c in box.connections] for box in self.boxes]

        if self.find_overlapping(event.x - 1, event.y - 1, event.x + 1, event.y + 1):
            self.on_canvas_click(event)
            return
        self.selecting = True
        self.origin_x = event.x
        self.origin_y = event.y
        self.selectBox = self.create_rectangle(self.origin_x, self.origin_y, self.origin_x + 1, self.origin_y + 1)

    def __select_motion__(self, event):
        if self.selecting:
            x_new = event.x
            y_new = event.y
            self.coords(self.selectBox, self.origin_x, self.origin_y, x_new, y_new)

    def __select_release__(self, _):
        # TODO maybe there should be a Selector class to keep things clean?
        if self.selecting:
            selected_coordinates = self.coords(self.selectBox)
            # find boxes in selected area
            selected_boxes = []
            for box in self.boxes:
                x1, y1, x2, y2 = self.coords(box.rect)
                x = (x1 + x2) / 2
                y = (y1 + y2) / 2
                if selected_coordinates[0] <= x <= selected_coordinates[2] and selected_coordinates[1] <= y <= \
                        selected_coordinates[3]:
                    selected_boxes.append(box)

            selected_spiders = []
            for spider in self.spiders:
                x, y = spider.location
                if selected_coordinates[0] <= x <= selected_coordinates[2] and selected_coordinates[1] <= y <= \
                        selected_coordinates[3]:
                    selected_spiders.append(spider)

            # find wires in selected area (wires with beginning or end in selected box)
            selected_wires = []
            for wire in self.wires:
                # wire start in selected area
                x, y = wire.end_connection.location
                if selected_coordinates[0] <= x <= selected_coordinates[2] and selected_coordinates[1] <= y <= \
                        selected_coordinates[3]:
                    selected_wires.append(wire)
                    continue

                # wire start in selected area
                x, y = wire.start_connection.location
                if selected_coordinates[0] <= x <= selected_coordinates[2] and selected_coordinates[1] <= y <= \
                        selected_coordinates[3]:
                    selected_wires.append(wire)

            # select all
            for i in selected_wires + selected_boxes + selected_spiders:
                i.select()

            if selected_boxes:
                res = mb.askquestion(message='Add selection to a separate sub-diagram?')
                if res == 'yes':
                    x = (selected_coordinates[0] + selected_coordinates[2]) / 2
                    y = (selected_coordinates[1] + selected_coordinates[3]) / 2

                    # create new box that will contain the sub-diagram
                    box = self.add_box((x, y))
                    sub_diagram = box.edit_sub_diagram(save_to_canvasses=False)
                    prev_status = self.receiver.listener
                    self.receiver.listener = False
                    self.copier.copy_canvas_contents(sub_diagram, selected_wires, selected_boxes,
                                                     selected_spiders, selected_coordinates, box)
                    box.lock_box()
                    self.receiver.listener = prev_status
                    for w in list(filter(lambda wire_: (wire_ in self.wires), selected_wires)):
                        w.delete_self("sub_diagram")
                    for b in list(filter(lambda box_: (box_ in self.boxes), selected_boxes)):
                        b.delete_box(keep_sub_diagram=True, action="sub_diagram")
                    for s in list(filter(lambda spider_: (spider_ in self.spiders), selected_spiders)):
                        s.delete_spider("sub_diagram")
                        if self.receiver.listener:
                            self.receiver.receiver_callback('create_spider_parent', wire_id=s.id,
                                                            connection_id=s.id,
                                                            generator_id=box.id)
                    sub_diagram.set_name(str(sub_diagram.id)[-6:])
                    box.set_label(str(sub_diagram.id)[-6:])
                    self.main_diagram.add_canvas(sub_diagram)

            for i in selected_wires + selected_boxes + selected_spiders:
                i.deselect()

            self.delete(self.selectBox)
            self.selecting = False

    # HANDLE CLICK ON CANVAS
    def on_canvas_click(self, event):
        if self.draw_wire_mode:
            x, y = event.x, event.y
            for circle in [c for box in self.boxes for c in
                           box.connections] + self.outputs + self.inputs + self.spiders:

                conn_x, conn_y, conn_x2, conn_y2 = self.coords(circle.circle)
                if conn_x <= x <= conn_x2 and conn_y <= y <= conn_y2:
                    self.handle_connection_click(circle)
                    return

    def handle_connection_click(self, c):
        if c.has_wire or not self.draw_wire_mode:
            return
        if not self.current_wire_start:
            self.start_wire_from_connection(c)
        else:
            self.end_wire_to_connection(c)

    def start_wire_from_connection(self, connection):
        self.current_wire_start = connection

        connection.color_green()

    def end_wire_to_connection(self, connection, bypass_legality_check=False):

        if self.current_wire_start and self.is_wire_between_connections_legal(self.current_wire_start,
                                                                              connection) or bypass_legality_check:
            self.current_wire = Wire(self, self.current_wire_start, self.receiver, connection)
            self.wires.append(self.current_wire)

            if self.current_wire_start.box is not None:
                self.current_wire_start.box.add_wire(self.current_wire)
            if connection.box is not None:
                connection.box.add_wire(self.current_wire)

            self.current_wire_start.add_wire(self.current_wire)
            connection.add_wire(self.current_wire)

            self.current_wire.update()
            self.nullify_wire_start()

    def nullify_wire_start(self):
        if self.current_wire_start:
            self.current_wire_start.color_black()
        self.current_wire_start = None
        self.current_wire = None

    def add_box(self, loc=(100, 100), size=(60, 60), id_=None):
        box = Box(self, *loc, self.receiver, size=size, id_=id_)
        self.boxes.append(box)
        return box

    def add_spider(self, loc=(100, 100), id_=None):
        spider = Spider(None, 0, "spider", loc, self, self.receiver, id_=id_)
        self.spiders.append(spider)
        return spider

    def add_spider_with_wires(self, start, end, x, y):
        spider = self.add_spider((x, y))
        self.start_wire_from_connection(start)
        self.end_wire_to_connection(spider)

        self.start_wire_from_connection(end)
        self.end_wire_to_connection(spider)

    # OTHER BUTTON FUNCTIONALITY
    def save_as_png(self):
        filetypes = [('png files', '*.png')]
        file_path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=filetypes,
                                                 title="Save png file")
        if file_path:
            self.postscript(file='temp.ps', colormode="color")
            img = Image.open('temp.ps')
            img.save(file_path, 'png')
            os.remove("temp.ps")

    def toggle_draw_wire_mode(self):
        self.draw_wire_mode = not self.draw_wire_mode
        if self.draw_wire_mode:
            self.main_diagram.draw_wire_button.config(bg="lightgreen")
        else:
            self.nullify_wire_start()
            self.main_diagram.draw_wire_button.config(bg="white")

    # RESIZE/UPDATE
    def on_canvas_resize(self, _):
        # update label loc
        w = self.winfo_width()
        self.coords(self.name, w / 2, 10)

        self.update_inputs_outputs()
        # TODO here or somewhere else limit resize if it would mess up output/input display

    def update_inputs_outputs(self):
        x = self.winfo_width()
        y = self.winfo_height()
        output_index = max([o.index for o in self.outputs] + [0])
        for o in self.outputs:
            i = o.index
            step = y / (output_index + 2)
            o.move_to((x - 7, step * (i + 1)))

        input_index = max([o.index for o in self.inputs] + [0])
        for o in self.inputs:
            i = o.index
            step = y / (input_index + 2)
            o.move_to((6, step * (i + 1)))
        [w.update() for w in self.wires]

    def delete_everything(self):
        for w in self.wires:
            w.delete_self()
        for b in self.boxes:
            b.delete_box()
        self.boxes = []
        self.wires = []

    # STATIC HELPERS
    @staticmethod
    def is_wire_between_connections_legal(start, end):
        if start.is_spider() and end.is_spider():

            if abs(start.location[0] - end.location[0]) < 2 * start.r:
                return False

            for w in start.wires:
                if w.start_connection == end or w.end_connection == end:
                    return False

        if start == end:
            return False
        if (start.is_spider() and (
                end.side == "right" and end.location[0] > start.location[0] or
                end.side == "left" and end.location[0] < start.location[0]) or
                end.is_spider() and (
                        start.side == "right" and start.location[0] > end.location[0]
                        or start.side == "left" and start.location[0] < end.location[0])):
            return False

        if start.side == end.side == "spider":
            return True
        return not (start.side == end.side or start.side == "left" and start.location[0] - start.width_between_boxes <=
                    end.location[0] or start.side == "right" and start.location[0] + start.width_between_boxes >=
                    end.location[0])

    def random(self):
        if not self.draw_wire_mode:
            self.toggle_draw_wire_mode()

        for circle in [c for box in self.boxes for c in
                       box.connections] + self.outputs + self.inputs + self.spiders:
            if circle.has_wire:
                continue
            self.start_wire_from_connection(circle)

            for circle2 in [c for box in self.boxes for c in
                            box.connections] + self.outputs + self.inputs + self.spiders:

                if circle2.has_wire:
                    continue
                self.end_wire_to_connection(circle2)
                if not self.current_wire_start:
                    break
            self.nullify_wire_start()
        self.toggle_draw_wire_mode()

    def add_diagram_output(self, id_=None):
        output_index = max([o.index for o in self.outputs] + [0])
        if len(self.outputs) != 0:
            output_index += 1
        connection_output_new = Connection(self.diagram_source_box, output_index, "left", (0, 0), self, id_=id_)

        if self.diagram_source_box and self.receiver.listener:
            self.receiver.receiver_callback("add_inner_right", generator_id=self.diagram_source_box.id,
                                            connection_id=connection_output_new.id)
        elif self.diagram_source_box is None and self.receiver.listener:
            self.receiver.receiver_callback("add_diagram_output", generator_id=None,
                                            connection_id=connection_output_new.id)

        self.outputs.append(connection_output_new)
        self.update_inputs_outputs()
        return connection_output_new

    def add_diagram_input_for_sub_d_wire(self, id_=None):
        box_c = self.diagram_source_box.add_left_connection()
        canvas_i = self.add_diagram_input(id_=id_)
        return box_c, canvas_i

    def add_diagram_output_for_sub_d_wire(self, id_=None):
        box_c = self.diagram_source_box.add_right_connection()
        canvas_o = self.add_diagram_output(id_=id_)
        return box_c, canvas_o

    def remove_diagram_output(self):
        if not self.outputs:
            return
        to_be_removed = self.outputs.pop()
        to_be_removed.delete_me()
        self.update_inputs_outputs()
        if self.diagram_source_box is None and self.receiver.listener:
            self.receiver.receiver_callback("remove_diagram_output")

    def add_diagram_input(self, id_=None):
        input_index = max([o.index for o in self.inputs] + [0])
        if len(self.inputs) != 0:
            input_index += 1
        new_input = Connection(self.diagram_source_box, input_index, "right", (0, 0), self, id_=id_)
        if self.diagram_source_box and self.receiver.listener:
            self.receiver.receiver_callback("add_inner_left", generator_id=self.diagram_source_box.id,
                                            connection_id=new_input.id)
        elif self.diagram_source_box is None and self.receiver.listener:
            self.receiver.receiver_callback("add_diagram_input", generator_id=None,
                                            connection_id=new_input.id)
        self.inputs.append(new_input)
        self.update_inputs_outputs()
        return new_input

    def remove_diagram_input(self):
        if not self.inputs:
            return
        to_be_removed = self.inputs.pop()
        to_be_removed.delete_me()
        self.update_inputs_outputs()
        if self.diagram_source_box is None and self.receiver.listener:
            self.receiver.receiver_callback("remove_diagram_input")

    def remove_specific_diagram_input(self, con):
        if not self.inputs:
            return
        if self.diagram_source_box:
            index_ = con.index
            for c in self.diagram_source_box.connections:
                if c.side == "left" and index_ == c.index:
                    self.diagram_source_box.remove_connection(c)

        for c in self.inputs:
            if c.index > con.index and con.side == c.side:
                c.lessen_index_by_one()

        self.inputs.remove(con)
        con.delete_me()
        self.update_inputs_outputs()

    def remove_specific_diagram_output(self, con):
        if not self.outputs:
            return
        if self.diagram_source_box:
            index_ = con.index
            for c in self.diagram_source_box.connections:
                if c.side == "right" and index_ == c.index:
                    self.diagram_source_box.remove_connection(c)

        for c in self.outputs:
            if c.index > con.index and con.side == c.side:
                c.lessen_index_by_one()

        self.outputs.remove(con)

        con.delete_me()
        self.update_inputs_outputs()

    def find_connection_to_remove(self, side):
        c_max = 0
        c = None
        for connection in self.diagram_source_box.connections:
            if connection.side == side and connection.index >= c_max:
                c_max = connection.index
                c = connection
        return c

    def remove_from_column(self, item, found):
        if not found and item.snapped_x:
            snapped_x = item.snapped_x
            self.columns[snapped_x].remove(item)
            if len(self.columns[snapped_x]) == 1:
                self.columns[snapped_x][0].snapped_x = None
                self.columns[snapped_x][0].is_snapped = False
                self.columns.pop(item, None)
            item.snapped_x = None

    @staticmethod
    def get_upper_lower_edges(component):
        if isinstance(component, Box):
            upper_y = component.y
            lower_y = component.y + component.size[1]
        else:
            upper_y = component.y - component.r
            lower_y = component.y + component.r
        return upper_y, lower_y

    @staticmethod
    def check_if_up_or_down(y_up, y_down, go_to_y_up, go_to_y_down, item):
        break_boolean = True
        go_to_y = None
        if y_up and not y_down:
            go_to_y = go_to_y_up
        elif y_down and not y_up:
            go_to_y = go_to_y_down
        elif not y_up and not y_down:
            break_boolean = False
        elif y_down and y_up:
            distance_to_y_up = abs(item.y - go_to_y_up)
            distance_to_y_down = abs(item.y - go_to_y_down)
            if distance_to_y_up < distance_to_y_down:
                go_to_y = go_to_y_up
            else:
                go_to_y = go_to_y_down
        return break_boolean, go_to_y
