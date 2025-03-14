import tkinter as tk


class Connection:
    """
    Connection.

    A CustomCanvas widget that allows a Wire to be connected to it. This object is represented as a circle on
    CustomCanvas. It is used as diagram inputs and outputs as well as Box input and outputs.
    """
    def __init__(self, box, index, side, location, canvas, r=5, id_=None):
        """
        Connection constructor.

        :param box: Box that the connection is attached to.
        :type box: Box
        :param index: Index of the Connection, shows index of Connection in the same place
        :type index: int
        :param side: String that states what side the Connection is created on.
        :type side: str
        :param location: Tuple of coordinates that the Connection will be created at.
        :type location: tuple
        :param canvas: CustomCanvas that the Connection is created on.
        :type canvas: CustomCanvas
        :param r: Radius of the circle that represents the Connection.
        :type r: int
        :param id_: ID of Connection
        :type id_: int
        """
        self.canvas = canvas
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

        self.context_menu = tk.Menu(self.canvas, tearoff=0)

        self.circle = self.canvas.create_oval(location[0] - self.r, location[1] - self.r, location[0] + self.r,
                                              location[1] + self.r, fill="black", outline="black")
        self.width_between_boxes = 1  # px
        self.bind_events()

    def bind_events(self):
        """
        Bind events to circle created on CustomCanvas.

        :return: None
        """
        self.canvas.tag_bind(self.circle, '<ButtonPress-3>', self.show_context_menu)

    def show_context_menu(self, event):
        """
        Create and display a context menu for the selected Connection.

        :param event: Event sent from keybind. Location used for context menu to be created at.
        :type event: tkinter.Event
        :return: None
        """
        if not self.wire or not self.wire.is_temporary:
            self.close_menu()
            if (self.box and not self.box.locked) or self.box is None:
                self.context_menu = tk.Menu(self.canvas, tearoff=0)

                self.context_menu.add_command(label="Delete Connection", command=self.delete_from_parent)
                self.context_menu.add_command(label="Cancel")

                self.context_menu.post(event.x_root, event.y_root)

    def close_menu(self):
        """
        Close context menu if exists.

        :return: None
        """
        if self.context_menu:
            self.context_menu.destroy()

    def delete_from_parent(self):
        """
        Delete the selected Connection from their parent.

        This deletes the specific Connection from its diagram input or outputs, or it deletes it from the Box.
        :return: None
        """
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

    def change_color(self, color='black'):
        """
        Change the color of the connection. Without a parameter it will turn the Connection to black.

        The function allows usage of all Tkinter built in colors as well as hex code.
        It will change the 'fill' color of the item.

        :param color: string of color name.
        :type color: str
        """
        self.canvas.itemconfig(self.circle, fill=color)

    def move_to(self, location):
        """
        Move the Connection to the given location.

        Takes a coordinate location and moves it to the given location on the canvas.

        :param location: tuple of coordinates. (x, y)
        :type location: tuple
        :return: None
        """
        self.canvas.coords(self.circle, location[0] - self.r, location[1] - self.r, location[0] + self.r,
                           location[1] + self.r)
        self.location = location

    def lessen_index_by_one(self):
        """
        Lowers the index of Connection by one.

        :return: None
        """
        self.index -= 1

    def delete(self):
        """
        Delete Connection and Wires connected to it.

        Deletes and removes the Connection from the Canvas. It will also delete the Wire connected to it.

        :return: None
        """
        self.canvas.delete(self.circle)
        if self.has_wire:
            self.canvas.delete(self.wire)
            self.wire.delete()

            if self.box and self.wire in self.box.wires:
                self.box.wires.remove(self.wire)

            if self.wire in self.canvas.wires:
                self.canvas.wires.remove(self.wire)

    def add_wire(self, wire):
        """
        Add Wire to the Connection.

        A Wire will be attached to the Connection, accessible through the wire class variable.

        :param wire: Wire that will be added to the Connection.
        :type wire: Wire
        :return: None
        """
        if not self.has_wire and self.wire is None:
            self.wire = wire
            self.has_wire = True

    def is_spider(self):
        """
        Used to check if the Connection is a Spider Connection or a regular Connection.

        :return: boolean
        """
        return False

    def remove_wire(self, wire=None):
        """
        Remove attached wire from Connection.

        This function has an optional parameter to specify the wire to be removed, but this is used
        only in the Spider version of this function.

        :param wire: Optional parameter that specifies what wire will be removed from the Connection
        :type wire: Wire
        :return:
        """
        if self.wire:
            self.wire = None
            self.has_wire = False

    def select(self):
        """
        Turns the Connection green.

        :return: None
        """
        self.change_color(color="green")

    def search_highlight_secondary(self):
        """
        Apply the secondary highlight to the Connection as a result of a search.

        This method will change the Connection to the secondary search highlight color. Additionally,
        it will the Connection to the search_result_highlights list in CustomCanvas.

        :return: None
        """
        self.change_color(color="orange")
        self.canvas.search_result_highlights.append(self)

    def search_highlight_primary(self):
        """
        Apply the primary highlight to the Connection as a result of a search.

        This method will change the Connection to the primary search highlight color. Additionally,
        it will the Connection to the search_result_highlights list in CustomCanvas.

        :return: None
        """
        self.change_color(color="cyan")
        self.canvas.search_result_highlights.append(self)

    def deselect(self):
        """
        Turns the Connection color to black.

        This is used as turning back to the original color before item selection.

        :return: None
        """
        self.change_color(color="black")
