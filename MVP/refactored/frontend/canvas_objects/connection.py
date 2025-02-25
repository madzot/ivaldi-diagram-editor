import tkinter as tk


class Connection:
    def __init__(self, box, index, side, location, canvas, r=5, id_=None):
        self.canvas = canvas
        self.id = id(self)
        self.box = box  # None if connection is diagram input/output/spider
        self.index = index
        self.side = side  # 'spider' if connection is a spider
        self.location = location
        self.wire = None
        self.has_wire = False
        self.r = r
        if not id_:
            self.id = id(self)

        else:
            self.id = id_
        self.node = None

        self.context_menu = tk.Menu(self.canvas, tearoff=0)

        self.circle = self.canvas.create_oval(location[0] - self.r, location[1] - self.r, location[0] + self.r,
                                              location[1] + self.r, fill="black", outline="black")
        self.width_between_boxes = 1  # px
        self.bind_events()

    def bind_events(self):
        self.canvas.tag_bind(self.circle, '<ButtonPress-3>', self.show_context_menu)

    def show_context_menu(self, event):
        self.close_menu()
        if self.box and not (self.box.sub_diagram or self.box.locked):
            self.context_menu = tk.Menu(self.canvas, tearoff=0)

            self.context_menu.add_command(label="Delete Connection", command=self.manually_delete_self)
            self.context_menu.add_command(label="Cancel")

            self.context_menu.post(event.x_root, event.y_root)

    def close_menu(self):
        if self.context_menu:
            self.context_menu.destroy()

    def manually_delete_self(self):
        if self.box:
            if self.box.sub_diagram and self.side == "left":
                for i in self.box.sub_diagram.inputs:
                    if i.index == self.index:
                        self.box.sub_diagram.remove_specific_diagram_input(i)
                        return
            if self.box.sub_diagram and self.side == "right":
                for i in self.box.sub_diagram.outputs:
                    if i.index == self.index:
                        self.box.sub_diagram.remove_specific_diagram_output(i)
                        return
            self.box.remove_connection(self)
            self.delete()
            return

        if self in self.canvas.inputs:
            self.canvas.remove_specific_diagram_input(self)
            return
        if self in self.canvas.outputs:
            self.canvas.remove_specific_diagram_output(self)
            return

    def color_black(self):
        self.canvas.itemconfig(self.circle, fill='black')

    def color_yellow(self):
        self.canvas.itemconfig(self.circle, fill='yellow')

    def color_green(self):
        self.canvas.itemconfig(self.circle, fill='green')

    def move_to(self, location):
        self.canvas.coords(self.circle, location[0] - self.r, location[1] - self.r, location[0] + self.r,
                           location[1] + self.r)
        self.location = location

    def lessen_index_by_one(self):
        self.index -= 1

    def delete(self):
        self.canvas.delete(self.circle)
        if self.has_wire:
            self.canvas.delete(self.wire)
            self.wire.delete_self()

            if self.box and self.wire in self.box.wires:
                self.box.wires.remove(self.wire)

            if self.wire in self.canvas.wires:
                self.canvas.wires.remove(self.wire)

    def add_wire(self, wire):
        if not self.has_wire and self.wire is None:
            self.wire = wire
            self.has_wire = True

    def is_spider(self):
        return False

    def remove_wire(self, wire=None):
        if self.wire:
            self.wire = None
            self.has_wire = False

    def select(self):
        self.canvas.itemconfig(self.circle, fill="green")

    def search_highlight_secondary(self):
        self.canvas.itemconfig(self.circle, fill="orange")
        self.canvas.search_result_highlights.append(self)

    def search_highlight_primary(self):
        self.canvas.itemconfig(self.circle, fill="cyan")
        self.canvas.search_result_highlights.append(self)

    def deselect(self):
        self.canvas.itemconfig(self.circle, fill="black")
