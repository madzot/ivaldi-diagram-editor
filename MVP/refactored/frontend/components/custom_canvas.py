import tkinter as tk
from threading import Timer
from tkinter import filedialog

import ttkbootstrap as ttk
from PIL import Image, ImageTk
from ttkbootstrap.constants import *

from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.backend.types.ActionType import ActionType
from MVP.refactored.backend.types.connection_side import ConnectionSide
from MVP.refactored.frontend.canvas_objects.box import Box
from MVP.refactored.frontend.canvas_objects.connection import Connection
from MVP.refactored.frontend.canvas_objects.corner import Corner
from MVP.refactored.frontend.canvas_objects.spider import Spider
from MVP.refactored.frontend.util.event import Event
from MVP.refactored.util.copier import Copier
from MVP.refactored.util.exporter.hypergraph_exporter import HypergraphExporter
from constants import *
from MVP.refactored.frontend.canvas_objects.wire import Wire


class CustomCanvas(tk.Canvas):
    def __init__(self, master, diagram_source_box, receiver: Receiver, main_diagram,
                 parent_diagram, add_boxes, id_=None, **kwargs):
        super().__init__(master, **kwargs)

        screen_width_min = round(main_diagram.winfo_screenwidth() / 1.5)
        screen_height_min = round(main_diagram.winfo_screenheight() / 1.5)
        self.configure(bg='white', width=screen_width_min, height=screen_height_min)
        self.update()

        self.parent_diagram = parent_diagram
        self.main_diagram = main_diagram
        self.master = master
        self.boxes: list[Box] = []
        self.outputs: list[Connection] = []
        self.inputs: list[Connection] = []
        self.spiders: list[Spider] = []
        self.wires: list[Wire] = []
        self.corners: list[Corner] = []
        self.temp_wire = None
        self.temp_end_connection = None
        self.pulling_wire = False
        self.previous_x = None
        self.previous_y = None
        self.quick_pull = False
        self.receiver = receiver
        self.current_wire_start = None
        self.current_wire = None
        self.draw_wire_mode = False
        self.bind('<Button-1>', self.on_canvas_click)
        self.bind("<Configure>", self.on_canvas_resize)
        self.diagram_source_box = diagram_source_box  # Only here if canvas is sub-diagram

        if not id_:
            self.id = id(self)
        else:
            self.id = id_

        self.receiver.add_new_canvas(self.id)


        self.name = self.create_text(0, 0, text=str(self.id)[-6:], fill="black", font='Helvetica 15 bold')
        self.name_text = str(self.id)[-6:]
        self.set_name(str(self.id))
        self.selectBox = None
        self.selector = main_diagram.selector
        self.bind("<ButtonPress-1>", self.__select_start__)
        self.bind('<Motion>', self.start_pulling_wire)
        self.bind('<Double-Button-1>', self.pull_wire)
        self.bind("<B1-Motion>", self.__select_motion__)
        self.bind("<ButtonRelease-1>", lambda event: self.__select_release__())
        self.bind("<Button-3>", self.handle_right_click)
        self.bind("<Delete>", lambda event: self.delete_selected_items())
        self.bind("<MouseWheel>", self.zoom)
        self.bind("<Right>", self.pan_horizontal)
        self.bind("<Left>", self.pan_horizontal)
        self.bind("<Down>", self.pan_vertical)
        self.bind("<Up>", self.pan_vertical)
        self.bind("<Control-c>", lambda event: self.copy_selected_items())
        self.bind("<Control-v>", self.paste_copied_items)
        self.bind("<Control-x>", lambda event: self.cut_selected_items())
        self.bind("<Control-n>", lambda event: self.create_sub_diagram())
        self.selecting = False
        self.copier = Copier()
        self.hypergraph_exporter = HypergraphExporter(self)

        if add_boxes and diagram_source_box:
            for connection in diagram_source_box.connections:
                if connection.side == "left":
                    self.add_diagram_input()
                if connection.side == "right":
                    self.add_diagram_output()
        self.set_name(self.name)
        self.context_menu = tk.Menu(self, tearoff=0)
        self.columns = {}

        self.tree_logo = (Image.open(ASSETS_DIR + "/file-tree-outline.png"))
        self.tree_logo = self.tree_logo.resize((20, 15))
        self.tree_logo = ImageTk.PhotoImage(self.tree_logo)

        button = ttk.Button(self, image=self.tree_logo,
                            command=lambda: self.main_diagram.toggle_treeview(), bootstyle=(PRIMARY, OUTLINE))
        button.place(x=28, y=20, anchor=tk.CENTER)
        self.box_shape = "rectangle"
        self.is_wire_pressed = False

        self.copy_logo = (Image.open(ASSETS_DIR + "/content-copy.png"))
        self.copy_logo = self.copy_logo.resize((20, 20))
        self.copy_logo = ImageTk.PhotoImage(self.copy_logo)

        self.total_scale = 1.0
        self.delta = 0.75

        self.prev_width_max = self.canvasx(self.winfo_width())
        self.prev_height_max = self.canvasy(self.winfo_height())
        self.prev_width_min = self.canvasx(0)
        self.prev_height_min = self.canvasy(0)

        c1 = Corner(None, None, "left", [0, 0], self, 0)
        c2 = Corner(None, None, "left", [0, self.winfo_height()], self, 0)
        c3 = Corner(None, None, "left", [self.winfo_width(), 0], self, 0)
        c4 = Corner(None, None, "left", [self.winfo_width(), self.winfo_height()], self, 0)
        self.corners.append(c1)
        self.corners.append(c2)
        self.corners.append(c3)
        self.corners.append(c4)
        self.init_corners()

        self.prev_scale = 1.0

        self.pan_history_x = 0
        self.pan_history_y = 0
        self.pan_speed = 20

        self.resize_timer = None

    def update_prev_winfo_size(self):
        self.prev_width_max = self.canvasx(self.winfo_width())
        self.prev_height_max = self.canvasy(self.winfo_height())
        self.prev_width_min = self.canvasx(0)
        self.prev_height_min = self.canvasy(0)

    def pan_horizontal(self, event):
        if event.keysym == "Right":
            multiplier = -1
        else:
            multiplier = 1

        for corner in self.corners:
            next_location = [
                corner.location[0] + multiplier * self.pan_speed,
                corner.location[1]
            ]
            if 0 < round(next_location[0]) < self.winfo_width() or 0 < round(next_location[1]) < self.winfo_height():
                self.pan_speed = min(abs(1 - corner.location[0]), abs(self.winfo_width() - corner.location[0] - 1))
                return

        for connection in self.corners + self.inputs + self.outputs:
            connection.location[0] = connection.location[0] + multiplier * self.pan_speed
            self.coords(connection.circle,
                        connection.location[0] - connection.r, connection.location[1] - connection.r,
                        connection.location[0] + connection.r, connection.location[1] + connection.r)
        self.move_boxes_spiders(True, multiplier)
        self.pan_speed = 20

    def pan_vertical(self, event):
        if event.keysym == "Down":
            multiplier = -1
        else:
            multiplier = 1

        for corner in self.corners:
            next_location = [
                corner.location[0], corner.location[1] + multiplier * self.pan_speed
            ]
            if 0 < round(next_location[0]) < self.winfo_width() or 0 < round(next_location[1]) < self.winfo_height():
                self.pan_speed = min(abs(1 - corner.location[1]), abs(self.winfo_height() - corner.location[1] - 1))
                return

        for connection in self.corners + self.inputs + self.outputs:
            connection.location[1] = connection.location[1] + multiplier * self.pan_speed
            self.coords(connection.circle,
                        connection.location[0] - connection.r, connection.location[1] - connection.r,
                        connection.location[0] + connection.r, connection.location[1] + connection.r)
        self.move_boxes_spiders(False, multiplier)
        self.pan_speed = 20

    def move_boxes_spiders(self, is_horizontal, multiplier):
        if is_horizontal:
            attr = "x"
            self.pan_history_x += multiplier * self.pan_speed
        else:
            attr = "y"
            self.pan_history_y += multiplier * self.pan_speed
        for spider in self.spiders:
            setattr(spider, attr, getattr(spider, attr) + multiplier * self.pan_speed)
            spider.move_to((spider.x, spider.y))
        for box in self.boxes:
            setattr(box, attr, getattr(box, attr) + multiplier * self.pan_speed)
            box.update_size(box.size[0], box.size[1])
            box.move_label()
        for wire in self.wires:
            wire.update()
        if self.pulling_wire:
            self.temp_wire.update()

    def delete(self, *args):
        # HypergraphManager.modify_canvas_hypergraph(self)
        super().delete(*args)

    def remove_box(self, box: Box):
        if box in self.boxes:
            self.boxes.remove(box)

    def remove_all_boxes(self):
        self.boxes = set()

    def remove_wire(self, wire: Wire):
        self.wires.remove(wire)

    def add_wire(self, wire: Wire):
        self.wires.add(wire)

    def remove_all_wires(self):
        self.wires = set()

    def update_after_treeview(self, canvas_width, treeview_width, to_left):
        if to_left:
            old_canvas_width = canvas_width + treeview_width
        else:

            old_canvas_width = canvas_width - treeview_width

        for box in self.boxes:
            relative_pos = ((box.x + box.x + box.size[0]) / 2) / old_canvas_width * canvas_width
            box.x = relative_pos - box.size[0] / 2
            box.update_size(box.size[0], box.size[1])
            box.move_label()

        for spider in self.spiders:
            relative_pos = (spider.x / old_canvas_width) * canvas_width
            spider.x = relative_pos
            spider.move_to((spider.x, spider.y))

        for wire in self.wires:
            wire.update()

    def handle_right_click(self, event):
        if self.selector.selecting:
            self.selector.finish_selection()
        if self.draw_wire_mode:
            self.cancel_wire_pulling(event)
        else:
            self.show_context_menu(event)

    def set_name(self, name):
        w = self.winfo_width()
        self.coords(self.name, w / 2, 12)
        self.itemconfig(self.name, text=name)
        self.name_text = name

    def offset_items(self, x_offset, y_offset):
        for box in self.boxes:
            box.x -= x_offset
            box.y -= y_offset
            box.update_size(box.size[0], box.size[1])
            box.move_label()
        for spider in self.spiders:
            spider.x -= x_offset
            spider.y -= y_offset
            spider.move_to((spider.x, spider.y))
        for wire in self.wires:
            wire.update()
        for i_o_c in self.inputs + self.outputs + self.corners:
            i_o_c.location = [i_o_c.location[0] - x_offset, i_o_c.location[1] - y_offset]
            self.coords(i_o_c.circle, i_o_c.location[0] - i_o_c.r, i_o_c.location[1] - i_o_c.r,
                        i_o_c.location[0] + i_o_c.r, i_o_c.location[1] + i_o_c.r)
        self.pan_history_x = 0
        self.pan_history_y = 0

    def reset_zoom(self):
        while self.total_scale - 1 > 0.01:
            event = Event(self.winfo_width() / 2, self.winfo_height() / 2, 5, -120)
            self.zoom(event)

    def zoom(self, event):
        event.x, event.y = self.canvasx(event.x), self.canvasy(event.y)
        scale = 1

        self.prev_scale = self.total_scale
        if event.num == 5 or event.delta == -120:
            scale *= self.delta
            self.total_scale *= self.delta
        if event.num == 4 or event.delta == 120:
            scale /= self.delta
            self.total_scale /= self.delta

        if self.prev_scale < self.total_scale:
            denominator = self.delta
        else:
            denominator = 1 / self.delta
            is_allowed, x_offset, y_offset, end = self.check_max_zoom(event.x, event.y, denominator)
            if end:
                self.total_scale = self.prev_scale
                return
            if not is_allowed:
                event.x += x_offset
                event.y += y_offset

        self.update_coordinates(denominator, event, scale)
        self.update_inputs_outputs()
        if self.total_scale - 1 < 0.1:
            self.init_corners()
        self.configure(scrollregion=self.bbox('all'))

    def update_coordinates(self, denominator, event, scale):
        for corner in self.corners:
            next_location = [
                self.calculate_zoom_dif(event.x, corner.location[0], denominator),
                self.calculate_zoom_dif(event.y, corner.location[1], denominator)
            ]
            corner.location = next_location
            self.coords(corner.circle, next_location[0] - corner.r, corner.location[1] - corner.r,
                        corner.location[0] + corner.r, corner.location[1] + corner.r)

        for i_o in self.inputs + self.outputs:
            i_o_location = [
                self.calculate_zoom_dif(event.x, i_o.location[0], denominator),
                self.calculate_zoom_dif(event.y, i_o.location[1], denominator)
            ]
            i_o.r *= scale
            i_o.location = i_o_location
            self.coords(i_o.circle, i_o.location[0] - i_o.r, i_o.location[1] - i_o.r,
                        i_o.location[0] + i_o.r, i_o.location[1] + i_o.r)

        for box in self.boxes:
            box.x = self.calculate_zoom_dif(event.x, box.x, denominator)
            box.y = self.calculate_zoom_dif(event.y, box.y, denominator)
            box.update_size(box.size[0] * scale, box.size[1] * scale)
            box.move_label()

        for spider in self.spiders:
            spider.x = self.calculate_zoom_dif(event.x, spider.x, denominator)
            spider.y = self.calculate_zoom_dif(event.y, spider.y, denominator)
            spider.location = spider.x, spider.y
            spider.r *= scale
            self.coords(spider.circle, spider.x - spider.r, spider.y - spider.r, spider.x + spider.r,
                        spider.y + spider.r)

        for wire in self.wires:
            wire.wire_width *= scale
            wire.update()
        if self.temp_wire:
            self.temp_wire.update()

    def check_max_zoom(self, x, y, denominator):
        x_offset = 0
        y_offset = 0
        for corner in self.corners:
            next_location = [
                self.calculate_zoom_dif(x, corner.location[0], denominator),
                self.calculate_zoom_dif(y, corner.location[1], denominator)
            ]
            multiplier = 1 / (1 - self.delta)
            if self.canvasx(0) < round(next_location[0]) < self.canvasx(self.winfo_width()):
                x_offset = -next_location[0] * multiplier
                if round(next_location[0]) > self.canvasx(self.winfo_width()) / 2:
                    x_offset = (self.canvasx(self.winfo_width()) - next_location[0]) * multiplier
            if self.canvasy(0) < round(next_location[1]) < self.canvasy(self.winfo_height()):
                y_offset = -next_location[1] * multiplier
                if round(next_location[1]) > self.canvasy(self.winfo_height()) / 2:
                    y_offset = (self.canvasy(self.winfo_height()) - next_location[1]) * multiplier
            # TODO does this part also need canvas coords
            # if 0 < round(next_location[0]) < self.winfo_width():
            #     x_offset = -next_location[0] * multiplier
            #     if round(next_location[0]) > self.winfo_width() / 2:
            #         x_offset = (self.winfo_width() - next_location[0]) * multiplier
            # if 0 < round(next_location[1]) < self.winfo_height():
            #     y_offset = -next_location[1] * multiplier
            #     if round(next_location[1]) > self.winfo_height() / 2:
            #         y_offset = (self.winfo_height() - next_location[1]) * multiplier
        is_allowed = x_offset == 0 == y_offset
        return is_allowed, x_offset, y_offset, self.check_corner_start_locations()

    def check_corner_start_locations(self):
        min_x = self.canvasx(0)
        min_y = self.canvasy(0)
        max_x = self.canvasx(self.winfo_width())
        max_y = self.canvasy(self.winfo_height())
        # min_x = 0
        # min_y = 0
        # max_x = self.winfo_width()
        # max_y = self.winfo_height()
        count = 0
        locations = [
            [min_x, min_y],
            [min_x, max_y],
            [max_x, min_y],
            [max_x, max_y]

        ]
        for corner in self.corners:
            for location in locations:
                if ((abs(round(self.canvasx(corner.location[0])) - location[0]) < 2
                    and abs(round(self.canvasy(corner.location[1])) - location[1]) < 2)
                        or
                    (abs(round(corner.location[0]) - location[0]) < 2
                        and abs(round(corner.location[1]) - location[1]) < 2)):
                    count += 1
        return count >= 4

    def close_menu(self):
        if self.context_menu:
            self.context_menu.destroy()

    def show_context_menu(self, event):
        if self.is_wire_pressed:
            self.close_menu()
            self.is_wire_pressed = False
            return
        event.x, event.y = self.canvasx(event.x), self.canvasy(event.y)
        if not self.is_mouse_on_object(event):
            self.close_menu()
            self.context_menu = tk.Menu(self, tearoff=0)

            self.context_menu.add_command(label="Add undefined box",
                                          command=lambda loc=(event.x, event.y): self.add_box(loc))

            # noinspection PyUnresolvedReferences
            if len(self.master.quick_create_boxes) > 0:
                sub_menu = tk.Menu(self.context_menu, tearoff=0)
                self.context_menu.add_cascade(menu=sub_menu, label="Add custom box")
                # noinspection PyUnresolvedReferences
                for box in self.master.quick_create_boxes:
                    # noinspection PyUnresolvedReferences
                    sub_menu.add_command(label=box,
                                         command=lambda loc=(event.x, event.y), name=box:
                                         self.master.json_importer.add_box_from_menu(self, name, loc))

            self.context_menu.add_command(label="Add spider",
                                          command=lambda loc=(event.x, event.y): self.add_spider(loc))

            self.context_menu.add_command(label="Cancel")
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def is_mouse_on_object(self, event):
        for box in self.boxes:
            if (box.x <= event.x <= box.x + box.size[0]
                    and box.y <= event.y <= box.y + box.size[1]):
                return True
        for spider in self.spiders:
            if (spider.x - spider.r <= event.x <= spider.x + spider.r
                    and spider.y - spider.r <= event.y <= spider.y + spider.r):
                return True
        return False

    # binding for drag select
    def __select_start__(self, event):
        event.x, event.y = self.canvasx(event.x), self.canvasy(event.y)
        [box.close_menu() for box in self.boxes]
        [wire.close_menu() for wire in self.wires]
        [(spider.close_menu(), self.tag_raise(spider.circle)) for spider in self.spiders]

        [i.close_menu() for i in self.inputs]
        [o.close_menu() for o in self.outputs]
        [[c.close_menu() for c in box.connections] for box in self.boxes]

        if self.find_overlapping(event.x - 1, event.y - 1, event.x + 1, event.y + 1):
            self.on_canvas_click(event)
            return
        self.selector.finish_selection()
        self.selector.start_selection(event)

    def __select_motion__(self, event):
        event.x, event.y = self.canvasx(event.x), self.canvasy(event.y)
        self.selector.update_selection(event)

    def __select_release__(self):
        self.selector.finalize_selection(self.boxes, self.spiders, self.wires)
        self.selector.select_action()

    def delete_selected_items(self):
        self.selector.delete_selected_items()

    def pull_wire(self, event):
        if not self.quick_pull and not self.draw_wire_mode:
            self.quick_pull = True
            connection = self.get_connection_from_location(event)
            if connection is not None and not connection.has_wire:
                self.toggle_draw_wire_mode()
                self.on_canvas_click(event, connection)
            else:
                self.quick_pull = False

    def get_connection_from_location(self, event):
        if self.draw_wire_mode or self.quick_pull:
            x, y = event.x, event.y
            for circle in [c for box in self.boxes for c in
                           box.connections] + self.outputs + self.inputs + self.spiders:

                conn_x, conn_y, conn_x2, conn_y2 = self.coords(circle.circle)
                if conn_x <= x <= conn_x2 and conn_y <= y <= conn_y2:
                    return circle
        return None

    def _fix_new_sub_diagram_box_wires(self, sub_diagram_box: Box) -> None:
        """
        This is workaround to fix the wires that are not connected to the sub-diagram box
        TODO: Fix the original issue
        """
        if not sub_diagram_box:
            return

        for connection in sub_diagram_box.connections:
            correct_wire = connection.wire
            correct_wire.end_connection.wire = correct_wire

    # HANDLE CLICK ON CANVAS
    def on_canvas_click(self, event, connection=None):
        if self.selector.selecting:
            self.selector.finish_selection()
        if connection is None:
            connection = self.get_connection_from_location(event)
        if connection is not None:
            self.handle_connection_click(connection, event)

    def start_pulling_wire(self, event):
        if self.draw_wire_mode and self.pulling_wire:
            if self.temp_wire is not None:
                self.temp_wire.delete_self()
            if self.temp_end_connection.location != (self.canvasx(event.x), self.canvasy(event.y)):
                self.previous_x = self.canvasx(event.x)
                self.previous_y = self.canvasy(event.y)
                self.temp_end_connection.delete_me()
                self.temp_end_connection = Connection(None, 0, None,
                                                      (self.canvasx(event.x), self.canvasy(event.y)),
                                                      self)
            self.temp_wire = Wire(self, self.current_wire_start, self.receiver, self.temp_end_connection, None, True)

    def handle_connection_click(self, c, event):
        if c.has_wire or not self.draw_wire_mode:
            return
        if not self.current_wire_start:
            self.start_wire_from_connection(c, event)
            self.start_pulling_wire(event)
        else:
            self.end_wire_to_connection(c)

    def start_wire_from_connection(self, connection, event=None):
        if connection.side == "spider" or not connection.has_wire:
            self.current_wire_start = connection

            connection.color_green()

            if event is not None:
                x, y = self.canvasx(event.x), self.canvasy(event.y)
                self.pulling_wire = True
                self.temp_end_connection = Connection(None, None, None, (x, y), self)

    def end_wire_to_connection(self, connection, bypass_legality_check=False):

        if connection == self.current_wire_start:
            self.nullify_wire_start()
            self.cancel_wire_pulling()

        if self.current_wire_start and self.is_wire_between_connections_legal(self.current_wire_start,
                                                                              connection) or bypass_legality_check:
            self.cancel_wire_pulling()
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

    def cancel_wire_pulling(self, event=None):
        if event:
            self.nullify_wire_start()
        if self.temp_wire is not None:
            self.temp_end_connection.delete_me()
            self.temp_wire.delete_self()
            self.temp_wire = None
            self.temp_end_connection = None
            self.pulling_wire = False
            if self.quick_pull:
                self.quick_pull = False
                self.draw_wire_mode = False
                self.main_diagram.draw_wire_button.config(bootstyle=(PRIMARY, OUTLINE))

    def nullify_wire_start(self):
        if self.current_wire_start:
            self.current_wire_start.color_black()
        self.current_wire_start = None
        self.current_wire = None

    def add_box(self, loc=(100, 100), size=(60, 60), id_=None, shape=None):
        if shape is None:
            shape = self.box_shape
        box = Box(self, *loc, self.receiver, size=size, id_=id_, shape=shape)
        self.boxes.append(box)
        return box

    def get_box_by_id(self, box_id: int) -> Box | None:
        for box in self.boxes:
            if box.id == box_id:
                return box
        return None

    def get_box_function(self, box_id) -> BoxFunction | None:
        box = self.get_box_by_id(box_id)
        if box:
            return BoxFunction(box.label_text, code=self.main_diagram.label_content[box.label_text])
        return None

    def add_spider(self, loc=(100, 100), id_=None):
        spider = Spider(None, 0, "spider", loc, self, self.receiver, id_=id_)
        self.spiders.append(spider)
        return spider

    def add_spider_with_wires(self, start: Connection, end: Connection, x, y):
        spider = self.add_spider((x, y))
        self.start_wire_from_connection(start)
        self.end_wire_to_connection(spider)

        self.start_wire_from_connection(end)
        self.end_wire_to_connection(spider)

    # OTHER BUTTON FUNCTIONALITY
    def save_as_png(self):
        self.reset_zoom()
        filetypes = [('png files', '*.png')]
        file_path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=filetypes,
                                                 title="Save png file")
        if file_path:
            self.main_diagram.generate_png(self, file_path)

    def open_tikz_generator(self):
        self.reset_zoom()
        tikz_window = tk.Toplevel(self)
        tikz_window.title("TikZ Generator")

        tk.Label(tikz_window, text="PGF/TikZ plots can be used with the following packages.\nUse pgfplotsset to change the size of plots.", justify="left").pack()

        pgfplotsset_text = tk.Text(tikz_window, width=30, height=5)
        pgfplotsset_text.insert(tk.END, "\\usepackage{tikz}\n\\usepackage{pgfplots}\n\\pgfplotsset{\ncompat=newest, \nwidth=15cm, \nheight=10cm\n}")
        pgfplotsset_text.config(state=tk.DISABLED)
        pgfplotsset_text.pack()

        tikz_text = tk.Text(tikz_window)
        tikz_text.insert(tk.END, self.main_diagram.generate_tikz(self))
        tikz_text.config(state="disabled")
        tikz_text.pack(pady=10, fill=tk.BOTH, expand=True)
        tikz_text.update()

        tikz_copy_button = ttk.Button(tikz_text, image=self.copy_logo,
                                      command=lambda: self.main_diagram.copy_to_clipboard(tikz_text),
                                      bootstyle=LIGHT)
        tikz_copy_button.place(x=tikz_text.winfo_width() - 30, y=20, anchor=tk.CENTER)

    def toggle_draw_wire_mode(self):
        self.draw_wire_mode = not self.draw_wire_mode
        if self.draw_wire_mode:
            for item in self.selector.selected_items:
                item.deselect()
            self.selector.selected_items.clear()
            self.main_diagram.draw_wire_button.config(bootstyle=SUCCESS)
        else:
            self.nullify_wire_start()
            self.cancel_wire_pulling()
            self.main_diagram.draw_wire_button.config(bootstyle=(PRIMARY, OUTLINE))

    # RESIZE/UPDATE
    def on_canvas_resize(self, _):
        # update label loc
        w = self.canvasx(self.winfo_width())
        self.coords(self.name, w / 2, self.canvasy(10))

        if self.total_scale - 1 > 0.1:
            self.update_corners()
        else:
            self.init_corners()

        self.update_inputs_outputs()
        self.update_prev_winfo_size()
        # self.offset_items(self.corners[0].location[0], self.corners[0].location[1])
        # TODO here or somewhere else limit resize if it would mess up output/input display

    @staticmethod
    def debounce(wait_time):
        """
        Decorator that will debounce a function so that it is called after wait_time seconds
        If it is called multiple times, will wait for the last call to be debounced and run only this one.
        """

        def decorator(function):
            def debounced(*args, **kwargs):
                def call_function():
                    debounced._timer = None
                    return function(*args, **kwargs)

                # if we already have a call to the function currently waiting to be executed, reset the timer
                if debounced._timer is not None:
                    debounced._timer.cancel()

                # after wait_time, call the function provided to the decorator with its arguments
                debounced._timer = Timer(wait_time, call_function)
                debounced._timer.start()

            debounced._timer = None
            return debounced

        return decorator

    def init_corners(self):
        min_x = self.canvasx(0)
        min_y = self.canvasy(0)
        max_x = self.canvasx(self.winfo_width())
        max_y = self.canvasy(self.winfo_height())
        self.corners[0].move_to([min_x, min_y])
        self.corners[1].move_to([min_x, max_y])
        self.corners[2].move_to([max_x, min_y])
        self.corners[3].move_to([max_x, max_y])
        self.update_inputs_outputs()

    @debounce(1)
    def update_corners(self):
        min_x = self.canvasx(0)
        min_y = self.canvasy(0)
        max_x = self.canvasx(self.winfo_width())
        max_y = self.canvasy(self.winfo_height())
        self.corners[0].move_to([(self.corners[0].location[0] + (min_x - self.prev_width_min) / self.delta),
                                 (self.corners[0].location[1] + (min_y - self.prev_height_min) / self.delta)])

        self.corners[1].move_to([(self.corners[1].location[0] + (min_x - self.prev_width_min) / self.delta),
                                 (self.corners[1].location[1] + (max_y - self.prev_height_max) / self.delta)])

        self.corners[2].move_to([(self.corners[2].location[0] + (max_x - self.prev_width_max) / self.delta),
                                 (self.corners[2].location[1] + (min_y - self.prev_height_min) / self.delta)])

        self.corners[3].move_to([(self.corners[3].location[0] + (max_x - self.prev_width_max) / self.delta),
                                 (self.corners[3].location[1] + (max_y - self.prev_height_max) / self.delta)])

    def update_inputs_outputs(self):
        x = self.corners[3].location[0]
        y = self.corners[3].location[1]
        min_y = self.corners[0].location[1]
        output_index = max([o.index for o in self.outputs] + [0])
        for o in self.outputs:
            i = o.index
            step = (y - min_y) / (output_index + 2)
            o.move_to([x - 7, min_y + step * (i + 1)])

        input_index = max([o.index for o in self.inputs] + [0])
        for o in self.inputs:
            i = o.index
            step = (y - min_y) / (input_index + 2)
            o.move_to([6 + self.corners[0].location[0], min_y + step * (i + 1)])
        [w.update() for w in self.wires]

    def delete_everything(self):
        while len(self.wires) > 0:
            self.wires[0].delete_self()
        while len(self.boxes) > 0:
            if self.boxes[0].sub_diagram:
                sub_diagram = 'sub_diagram'
            else:
                sub_diagram = None
            self.boxes[0].delete_box(action=sub_diagram)
        while len(self.spiders) > 0:
            self.spiders[0].delete_spider()
        while len(self.outputs) > 0:
            self.remove_diagram_output()
        while len(self.inputs) > 0:
            self.remove_diagram_input()

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
        connection_output_new = Connection(self.diagram_source_box, output_index,
                                           ConnectionSide.LEFT, [0, 0], self,
                                           r=5*self.total_scale, id_=id_)

        if self.diagram_source_box and self.receiver.listener:
            self.receiver.receiver_callback(ActionType.BOX_ADD_INNER_RIGHT, generator_id=self.diagram_source_box.id,
                                            connection_id=connection_output_new.id, connection_nr=connection_output_new.index,
                                            canvas_id=self.id)
        elif self.diagram_source_box is None and self.receiver.listener:
            self.receiver.receiver_callback(ActionType.DIAGRAM_ADD_OUTPUT, connection_nr=connection_output_new.index,
                                            connection_id=connection_output_new.id, canvas_id=self.id)

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
            self.receiver.receiver_callback(ActionType.DIAGRAM_REMOVE_OUTPUT, canvas_id=self.id, connection_id=to_be_removed.id)

    def add_diagram_input(self, id_=None):
        input_index = max([o.index for o in self.inputs] + [0])
        if len(self.inputs) != 0:
            input_index += 1
        new_input = Connection(self.diagram_source_box, input_index, ConnectionSide.RIGHT, [0, 0], self,
                               r=5*self.total_scale, id_=id_)
        if self.diagram_source_box and self.receiver.listener:
            self.receiver.receiver_callback(ActionType.BOX_ADD_INNER_LEFT, generator_id=self.diagram_source_box.id,
                                            connection_id=new_input.id, connection_nr=new_input.index, canvas_id=self.id)
        elif self.diagram_source_box is None and self.receiver.listener:
            self.receiver.receiver_callback(ActionType.DIAGRAM_ADD_INPUT,
                                            connection_id=new_input.id, connection_nr=new_input.index, canvas_id=self.id)
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
            self.receiver.receiver_callback(ActionType.DIAGRAM_REMOVE_INPUT, canvas_id=self.id, connection_id=to_be_removed.id)

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

    def setup_column_removal(self, item, found):
        if not found and item.snapped_x:
            self.remove_from_column(item, item.snapped_x)
            item.snapped_x = None
            item.prev_snapped = None
        elif item.is_snapped and found and item.snapped_x != item.prev_snapped:
            self.remove_from_column(item, item.prev_snapped)
        item.is_snapped = found
        item.prev_snapped = item.snapped_x

    def remove_from_column(self, item, snapped_x):
        self.columns[snapped_x].remove(item)
        if len(self.columns[snapped_x]) == 1:
            self.columns[snapped_x][0].snapped_x = None
            self.columns[snapped_x][0].is_snapped = False
            self.columns.pop(snapped_x, None)

    def export_hypergraph(self):
        self.reset_zoom()
        self.hypergraph_exporter.export()

    @staticmethod
    def calculate_zoom_dif(zoom_coord, object_coord, denominator):
        """Calculates how much an object will to be moved when zooming."""
        return round(zoom_coord - (zoom_coord - object_coord) / denominator, 4)

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

    def change_box_shape(self, shape):
        self.box_shape = shape

    def copy_selected_items(self):
        self.selector.copy_selected_items()

    def paste_copied_items(self, event):
        self.selector.paste_copied_items(event.x, event.y)

    def cut_selected_items(self):
        self.copy_selected_items()
        self.delete_selected_items()

    def create_sub_diagram(self):
        if len(list(filter(lambda x: isinstance(x, Spider) or isinstance(x, Box), self.selector.selected_items))) > 1:
            self.selector.create_sub_diagram()
            self.selector.selected_items = []
