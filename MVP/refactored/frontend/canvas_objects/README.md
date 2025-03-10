
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
        Changes Connection color to black.

    .color_green()
        Changes Connection color to green.

    .move_to(location)
        Updates the canvas location of the Connection and updates the location variable
        :param location - tuple of x and y coordinates.

    .lessen_index_by_one()
        Lowers the index of a connection by 1.

    .delete()
        Used to delete the connection. Removes circle from the canvas as well as deletes connected wires.

    .add_wire(wire)
        Adds a wire to the connection if the connection is not wired already.

    .is_spider()
        Used to check if the connection is a sub-class of Connection named Spider. Returns True if it is of a Spider class.

    .remove_wire(wire=None)
        Removes the connected wire from the connection. The wire parameter is used for Spiders that need specification on what wire to remove.
        :param wire - Wire object to be removed from Connection (if dealing with Spider sub-class)

    .select()
        Turns the color of the connection circle green.

    .search_highlight_secondary()
        Used as a secondary highlight when conducting searches. Function turns the object orange and adds it to a list of search highlighted items in CustomCanvas.

    .search_highlight_primary()
        Used as the primary highlight when conducting searches. Function turns the object cyan and adds it to a list of search highlighted items in CustomCanvas.

    .deselect()
        Changes Connectino color to black.


---

## Spider

Spider is a subclass of Connection. Difference between Connection and Spider is mostly Spiders allowing multiple wires to be connected to it.

### Spider parameters

| Param                | Description                                                                                                                               |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| location: list       | Location of the Spider in the form of a list. Example: [111, 222]                                                                         |
| canvas: CustomCanvas | CustomCanvas that the Spider is located and displayed on.                                                                                 |
| receiver: Receiver   | Receiver used for sending events to the backend proportion of the application. The receiver is usually taken from the MainDiagram object. |
| id_=None: int        | ID.                                                                                                                                       |


## Spider variables
| Variable          | Description                                                                                |
|-------------------|--------------------------------------------------------------------------------------------|
| x: int            | Quick variable to get the x coordinate of the Spider. It is the first number of location.  |
| y: int            | Quick variable to get the y coordinate of the Spider. It is the second number of location. |
| connections: list |                                                                                            |

































