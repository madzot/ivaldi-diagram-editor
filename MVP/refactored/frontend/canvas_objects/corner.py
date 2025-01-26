import tkinter as tk


class Corner:
    def __init__(self, box, index, side, location, canvas, r=5, id_=None):
        self.canvas = canvas
        self.id = id(self)
        self.box = box  # None if connection is diagram input/output
        self.index = index
        self.side = side
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
        self.distance_from_x = 0
        self.distance_from_y = 0

    def move_to(self, location):
        self.canvas.coords(self.circle, location[0] - self.r, location[1] - self.r, location[0] + self.r,
                           location[1] + self.r)
        self.location = location
