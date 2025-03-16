
# Canvas objects

This folder holds objects that can be used in `CustomCanvas`.

---
## Connection

Connection is an object that allows wires to be connected to it. It is represented as a black circle on the canvas.

Connections are used as diagram inputs and outputs as well as box connections. Connection is a superclass of Spider.

### Connection parameters

| **Param**             | **Type**     | **Description**                                                                                                                                                                                                                                                                                                     |
|-----------------------|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| box                   | Box          | Used if Connection is a box input or output. `None` if connection is not attached to a box.                                                                                                                                                                                                                         |
| index                 | int          | Index of Connection among the same side of the box or diagram.                                                                                                                                                                                                                                                      |
| side                  | str          | A string ("left" or "right"), that tells which side of a box or diagram the Connection is created on.<br/> Values are flipped when regarding inputs and outputs of a connection, side="left" connections are on the right side of the diagram (outputs), side="right" are on the left side of the diagram (inputs). |
| location              | tuple        | Tuple of x and y coordinates as integers. Example: (100, 200).                                                                                                                                                                                                                                                      |
| canvas                | CustomCanvas | CustomCanvas object that the Connection will be drawn on and connected to.                                                                                                                                                                                                                                          |
|                       |              | 
| # **Optional params** |              |                                                                                                                                                                                                                                                                                                                     |
| r                     | int          | Radius of the Connection.<br/> Default value is `5`                                                                                                                                                                                                                                                                 |
| id_                   | int          | ID.<br/> Default value is `None`                                                                                                                                                                                                                                                                                    |

### Connection variables

Below is a description of all available variables in the Connection class. It will not include variables of Connection parameters.

| **Variable**        | **Type**     | **Description**                                                                                                                    |
|---------------------|--------------|------------------------------------------------------------------------------------------------------------------------------------|
| wire                | Wire         | Wire object that is connected to the Connection. `None` if no wire.                                                                |
| has_wire            | boolean      | Boolean that is True if a wire is connected to the Connection. Otherwise False.                                                    |
| context_menu        | tkinter.Menu | Used to create a context menu for Connections.                                                                                     |
| circle              | int          | CustomCanvas tagOrId for the circle that represents a Connection.                                                                  |
| width_between_boxes | int          | Integer that is used to describe how close to the x axis another connected Connection can come before being unable to move closer. |


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

        Parameters:
            location (tuple): Tuple of x, y coordinates that Connection will move to.

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

        Parameters:
            wire (Wire): Used when dealing with Spider (not Connection). It is the wire that will be removed from the Spider.
                          If dealing with a Connection, this parameter will have no function.

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

| **Param**             | **Type**     | **Description**                                                                                                                           |
|-----------------------|--------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| location              | list         | Location of the Spider in the form of a list. Example: [111, 222]                                                                         |
| canvas                | CustomCanvas | CustomCanvas that the Spider is located and displayed on.                                                                                 |
| receiver              | Receiver     | Receiver used for sending events to the backend proportion of the application. The receiver is usually taken from the MainDiagram object. |
|                       |              |                                                                                                                                           |
| # **Optional params** |              |                                                                                                                                           |
| id_                   | int          | ID.<br/> Default value is `None`                                                                                                          |


## Spider variables

Along with these variables Spider has Connection variables as well. Although all of them might not be used.

| **Variable**    | **Type**     | **Description**                                                                                                                                                                      |
|-----------------|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| x               | int          | Quick variable to get the x coordinate of the Spider. It is the first number of location.                                                                                            |
| y               | int          | Quick variable to get the y coordinate of the Spider. It is the second number of location.                                                                                           |
| connections     | list         | List of containing Connections, it is used in algebraic notation creation. During diagram editing it will not contain connections                                                    |
| context_menu    | tkinter.Menu | Variable that holds the context menu of the Spider.                                                                                                                                  |
| wires           | list         | List that contains Wire class objects that have been connected to the Spider.<br/> This is the spider version of Connection.wire.<br/> For Spiders the variable `.wire` is not used. |
| receiver        | Receiver     | Receiver object, usually taken from MainDiagram. Used to send information to the back end portion                                                                                    |
| is_snapped      | bool         | Boolean stating if the Spider is currently snapped to a column or not.                                                                                                               |

### Spider functions

```
    .on_resize_scroll(event)
        Changes Spider size based on mouse scroll event. Used as a keybind function to change Spider sizes when needed.

        Parameters:
            event (tkinter.Event): Event object that is sent on key presses.

    .on_press()
        Handles Button-1 (mouse left click) press event in Spider. Clears previous selection and selects the Spider.

    .on_control_press()
        Handles ctrl + Button-1 press event bind. Toggles selection on the Spider, while not clearing previous selection.
        
    .on_drag(event)
        Handles dragging the Spider. Checks snapping into columns and other collision related actions. Moves and updates Spider location.

        Parameters:
            event (tkinter.Event): Event object that is sent on key presses.

    .align_wire_ends()
        Checks if the ends of a connected wire need to be switched. Due to start connection always being on the left and end being on the right,
         this function is used to check and realign the ends of a wire thats attached to the Spider.

    .find_collisions(go_to_x, go_to_y)
        Checks the canvas for overlapping widgets in the location of (go_to_x, go_to_y), covers the area equal to a square around spider.
         Wires are excluded from this. Returns list of canvas tags that are in the designated area.
        
        Parameters:
            go_to_x (int): x coordinate that is at the center of the desired collision checking location.
            go_to_y (int): y coordinate that is at the center of the desired collision checking location.
        
    .is_illegal_move(new_x)
        Checks if movement to new_x is legal. Returns boolean.
        
        Parameters:
            new_x (int): x coordinate that Spider would be moved to/what location legality is checked for.
```


---

## Box

A box is a rectangle on the CustomCanvas. A box can have Connections on it's left and right side. 

Boxes represent a function, the function itself can be defined by the user. 

Boxes are also used to contain sub-diagrams. The sub-diagram is accessible from the treeview on canvases on the left side of the application.

Boxes can contain code. The functions are findable in the "Manage methods" window. Applying code to boxes can be done
by renaming them to match an existing function or by adding code to them yourself through the code editor.
Code can only be added to a box with an existing label.

The coordinates of a Box are the top left corner for it.

### Box parameters

| **Parameter**         | **Type**     | **Description**                                                                                                                 |
|-----------------------|--------------|---------------------------------------------------------------------------------------------------------------------------------|
| canvas                | CustomCanvas | The CustomCanvas object that the Box will be drawn on.                                                                          |
| x                     | int          | X coordinate for the Box.                                                                                                       |
| y                     | int          | Y coordinate for the Box.                                                                                                       |
| receiver              | Receiver     | Receiver object used to send information to the backend.                                                                        |
|                       |              |                                                                                                                                 |
| # **Optional params** |              |                                                                                                                                 |
| size                  | tuple        | A list containing the height and width of the box. Default value is (60, 60)                                                    |
| id_                   | int          | Box ID. If no value is given then Box will receive a random ID.                                                                 |
| shape                 | string       | String describing the shape of the Box. Default value is "rectangle".<br/> Usable values for this are: `rectangle`,  `triangle` |


### Box variables

| **Variable**      | **Type**     | **Description**                                                                                                                                                                                         |
|-------------------|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| shape             | string       | Describes shape of Box, as described in Box parameters.                                                                                                                                                 |
| canvas            | CustomCanvas | The CustomCanvas object that the Box is drawn on.                                                                                                                                                       |
| x                 | int          | X coordinate of the top left corner of the Box.                                                                                                                                                         |
| y                 | int          | Y coordinate of the top left corner of the Box.                                                                                                                                                         |
| start_x           | int          | Used as the x position where to start moving the Box from when dragging.                                                                                                                                |
| start_y           | int          | Used as the y position where to start moving the Box from when dragging.                                                                                                                                |
| size              | tuple        | Contains the height and width in a tuple.                                                                                                                                                               |
| x_dif             | int          | Used in dragging to determine the x distance of the mouse from the top left corner.                                                                                                                     |
| y_dif             | int          | Used in dragging to determine the y distance of the mouse from the top left corner.                                                                                                                     |
| connections       | list         | List of Connections attached to the Box.                                                                                                                                                                |
| left_connections  | int          | Number of connections on the left side.                                                                                                                                                                 |
| right_connections | int          | Number of Connections on the right side.                                                                                                                                                                |
| label             | int          | CustomCanvas tag that represents the Box label.                                                                                                                                                         |
| label_text        | string       | Text that is in the label of the Box.                                                                                                                                                                   |
| wires             | list         | List of Wires attached to the Box's Connections.                                                                                                                                                        |
| id                | int          | ID of the Box.                                                                                                                                                                                          |
| context_menu      | tkinter.Menu | Context menu used for Box.                                                                                                                                                                              |
| rect              | int          | CustomCanvas tag that represents the Box rectangle or other shape in the canvas.                                                                                                                        |
| resize_handle     | int          | CustomCanvas tag that represents the resizing handle in the Box.                                                                                                                                        |
| locked            | boolean      | Determines if the Box is locked or not. While locked some feature's are hidden.                                                                                                                         |
| sub_diagram       | CustomCanvas | CustomCanvas object that is the sub-diagram of the Box. It is None if the Box is not a sub-diagram Box.                                                                                                 |
| receiver          | Receiver     | Receiver object used to send information to the backend.                                                                                                                                                |
| is_snapped        | boolean      | Shows if the Box is currently snapped to a column or not.                                                                                                                                               |
| collision_ids     | list         | List of integers that hold all tags that are attached to the Box. Connections, labels, box rext and resize handle.<br/> This is used to remove collision with self when checking for colliding objects. |


