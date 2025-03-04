
# Canvas objects

This folder holds objects that can be used in `CustomCanvas`.

---
## Connection

Connection is an object that allows wires to be connected to it. It is represented as a black circle on the canvas.

Connections are used as diagram inputs and outputs as well as box connections. Connection is a superclass of Spider.

### Connection parameters

| Param                | Description                                                                                                                                                                                                                                                                                                    |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| box: Box             | Used if Connection is a box input or output. `None` if connection is not attached to a box.                                                                                                                                                                                                                    |
| index: int           | Index of Connection among the same side of the box or diagram.                                                                                                                                                                                                                                                 |
| side: str            | A string ("left" or "right"), that tells which side of a box or diagram the Connection is created on. Values are flipped when regarding inputs and outputs of a connection, side="left" connections are on the right side of the diagram (outputs), side="right" are on the left side of the diagram (inputs). |
| location: tuple      | Tuple of x and y coordinates as integers. Example: (100, 200).                                                                                                                                                                                                                                                 |
| canvas: CustomCanvas | CustomCanvas object that the Connection will be drawn on and connected to.                                                                                                                                                                                                                                     |
| r=5: int             | Radius of the Connection.                                                                                                                                                                                                                                                                                      |
| id_=None: int        | ID.                                                                                                                                                                                                                                                                                                            |

### Connection variables

Below is a description of all available variables in the Connection class. It will not include variables of Connection parameters.

| Variable                   | Description                                                                                                                        |
|----------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| wire: Wire                 | Wire object that is connected to the Connection. `None` if no wire.                                                                |
| has_wire: boolean          | Boolean that is True if a wire is connected to the Connection. Otherwise False.                                                    |
| context_menu: tkinter.Menu | Used to create a context menu for Connections.                                                                                     |
| circle: int                | CustomCanvas tagOrId for the circle that represents a Connection.                                                                  |
| width_between_boxes: int   | Integer that is used to describe how close to the x axis another connected Connection can come before being unable to move closer. |


### Connection functions

    .bind_events()
        Binds events to the circle on the canvas.

    .show_context_menu(event)
        Creates a context menu for Connection and displays it at event.x_root and event.y_root.

    .close_menu()
        Destroys the context menu.

    .delete_from_parent()
        Activated from choosing 'Delete Connection' in the context menu. Deletes the selected Connection from Canvas.

    .color_black()
        Changes Connection color to black

    .color_green()
        Changes Connection color to green

    .move_to(location)
        Updates the canvas location of the Connection and updates the location variable
        :param location - tuple of x and y coordinates.