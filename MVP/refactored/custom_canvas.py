import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox as mb

from PIL import Image

from MVP.refactored.box import Box
from MVP.refactored.connection import Connection
from MVP.refactored.selector import Selector
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
        self.selector = Selector(self)
        self.bind("<ButtonPress-1>", self.__select_start__)
        self.bind("<B1-Motion>", self.__select_motion__)
        self.bind("<ButtonRelease-1>", lambda event: self.__select_release__())
        self.selecting = False
        self.copier = Copier()
        if add_boxes and diagram_source_box:
            for connection in diagram_source_box.connections:
                if connection.side == "left":
                    self.add_diagram_input()
                if connection.side == "right":
                    self.add_diagram_output()
        self.set_name(self.name)
        self.bind('<ButtonPress-3>', self.show_context_menu)
        self.context_menu = tk.Menu(self, tearoff=0)
        self.is_context_menu_open = False
        self.columns = {}

    def set_name(self, name):
        w = self.winfo_width()
        self.coords(self.name, w / 2, 12)
        self.itemconfig(self.name, text=name)
        self.name_text = name

    def close_menu(self):
        if self.context_menu:
            self.context_menu.destroy()

    def show_context_menu(self, event):
        event.x, event.y = self.canvasx(event.x), self.canvasy(event.y)
        if not self.is_mouse_on_object(event):
            self.close_menu()
            self.context_menu = tk.Menu(self, tearoff=0)

            self.context_menu.add_command(label="Add undefined box",
                                          command=lambda loc=(event.x, event.y): self.add_box(loc))
            self.context_menu.add_command(label="Add spider",
                                          command=lambda loc=(event.x, event.y): self.add_spider(loc))

            self.context_menu.add_command(label="Cancel")
            self.context_menu.tk_popup(event.x_root, event.y_root)

    @staticmethod
    def grouped(iterable, n):
        "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
        return zip(*[iter(iterable)] * n)

    def is_mouse_on_object(self, event):
        print(event)
        for box in self.boxes:
            if (box.x <= event.x <= box.x + box.size[0]
                    and box.y <= event.y <= box.y + box.size[1]):
                return True
        for spider in self.spiders:
            if (spider.x - spider.r <= event.x <= spider.x + spider.r
                    and spider.y - spider.r <= event.y <= spider.y + spider.r):
                return True
        for wire in self.wires:

            print(self.coords(wire.line))
        return False

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
        self.selector.start_selection(event)

    def __select_motion__(self, event):
        self.selector.update_selection(event)

    def __select_release__(self):
        self.selector.finalize_selection(self.boxes, self.spiders, self.wires)
        if len(self.selector.selected_items) > 1:
            res = mb.askquestion(message='Add selection to a separate sub-diagram?')
            if res == 'yes':
                self.selector.select_action(True)
                return
        self.selector.select_action(False)

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
        if self.selector.selected_items:
            for item in self.selector.selected_items:
                if isinstance(item, Box):
                    if not (item.x < event.x < item.x + item.size[0] and item.y < event.y < item.y + item.size[1]):
                        item.deselect()
                        self.selector.selected_items.remove(item)
                if isinstance(item, Spider):
                    if not (item.x - item.r / 2 < event.x < item.x + item.r / 2 and
                            item.y - item.r / 2 < event.y < item.y + item.r / 2):
                        item.deselect()
                        self.selector.selected_items.remove(item)

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
            for item in self.selector.selected_items:
                item.deselect()
            self.selector.selected_items.clear()
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
