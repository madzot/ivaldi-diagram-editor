
# Canvas objects

This folder holds objects that can be used in `CustomCanvas`.

---
## Connection

Connection is an object that allows wires to be connected to it. It is represented as a black circle on the canvas.

Connections are used as diagram inputs and outputs as well as box connections. Connection is a superclass of Spider.

Connections have multiple different types that are differentiated by a different color of outline around the Connection.

### Connection parameters

| **Param**             | **Type**       | **Description**                                                                                                                                                                                                                                                                                                     |
|-----------------------|----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| box                   | Box            | Used if Connection is a box input or output. `None` if connection is not attached to a box.                                                                                                                                                                                                                         |
| index                 | int            | Index of Connection among the same side of the box or diagram.                                                                                                                                                                                                                                                      |
| side                  | str            | A string ("left" or "right"), that tells which side of a box or diagram the Connection is created on.<br/> Values are flipped when regarding inputs and outputs of a connection, side="left" connections are on the right side of the diagram (outputs), side="right" are on the left side of the diagram (inputs). |
| location              | tuple          | Tuple of x and y coordinates as integers. Example: (100, 200).                                                                                                                                                                                                                                                      |
| canvas                | CustomCanvas   | CustomCanvas object that the Connection will be drawn on and connected to.                                                                                                                                                                                                                                          |
|                       |                | 
| # **Optional params** |                |                                                                                                                                                                                                                                                                                                                     |
| r                     | int            | Radius of the Connection.<br/> Default value is `5`.                                                                                                                                                                                                                                                                |
| id_                   | int            | ID.<br/> Default value is `None`.                                                                                                                                                                                                                                                                                   |
| connection_type       | ConnectionType | ConnectionType that will define the outline style of the Connection. Default value is ConnectionType.GENERIC.                                                                                                                                                                                                       |

### Connection variables

Below is a description of all available variables in the Connection class. It will not include variables of Connection parameters.

| **Variable**        | **Type**       | **Description**                                                                                                                                                       |
|---------------------|----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| canvas              | CustomCanvas   | CustomCanvas object the Connection is created on.                                                                                                                     |
| box                 | Box            | Box object that Connection is attached to. This will be `None` if the Connection is root diagram input/output or a Spider.                                            |
| index               | int            | Connection index.                                                                                                                                                     |
| side                | str            | String that describes what side the Connection is on. `left` and `right` for Box sides, but flipped for diagram input/output. `Spider` if the Connection is a Spider. |
| location            | list           | List containing x, y coordinates of the Connection.                                                                                                                   |
| type                | ConnectionType | ConnectionType that defines the style of the Connection.                                                                                                              |
| wire                | Wire           | Wire object that is connected to the Connection. `None` if no wire.                                                                                                   |
| has_wire            | boolean        | Boolean that is True if a wire is connected to the Connection. Otherwise False.                                                                                       |
| r                   | int            | Radius of the circle.                                                                                                                                                 |
| id                  | int            | Connection ID.                                                                                                                                                        |
| context_menu        | tkinter.Menu   | Used to create a context menu for Connections.                                                                                                                        |
| circle              | int            | CustomCanvas tagOrId for the circle that represents a Connection.                                                                                                     |
| width_between_boxes | int            | Integer that is used to describe how close to the x axis another connected Connection can come before being unable to move closer.                                    |


### Connection functions

    .update()
        Updates the circle style using the type style.

    .bind_events()
        Binds events to the circle on the canvas.

    .increment_type()
        Changes the Connection type to the next possible type. Will not change if a Wire is connected to it.

    .change_type(type_id)
        Changes the type of the Connection to the selected type and update the style.

        Parameters:
            type_id (int): Value of the ConnectionType to change to.

    .get_tied_connection()
        Return the Connection that is tied to this Connection in a sub-diagram. If a Connection has a Box that's a sub-diagram
        it will return it's counterpart in the sub-diagram or sub-diagram box.

    .show_context_menu(event)
        Creates a context menu for Connection and displays it at event.x_root and event.y_root.

    .add_type_choice()
        Adds a type choosing sub-menu into the context menu that is created for the Connection. A type choice sub-menu
        will not be added if the Connection has a Wire.

    .add_active_type()
        Adds a new active type that can be chosen from the sub-menu in Connection context menu.

    .increment_active_types()
        Increments active_types. It will increase the active_types amount by 1, unless incrementing the value would be
        larger than the total amount of different Connection types.

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

| **Param**             | **Type**       | **Description**                                                                                                                           |
|-----------------------|----------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| location              | list           | Location of the Spider in the form of a list. Example: [111, 222]                                                                         |
| canvas                | CustomCanvas   | CustomCanvas that the Spider is located and displayed on.                                                                                 |
| receiver              | Receiver       | Receiver used for sending events to the backend proportion of the application. The receiver is usually taken from the MainDiagram object. |
|                       |                |                                                                                                                                           |
| # **Optional params** |                |                                                                                                                                           |
| id_                   | int            | ID.<br/> Default value is `None`.                                                                                                         |
| connection_type       | ConnectionType | Connection type.                                                                                                                          |


### Spider variables

Along with these variables Spider has Connection variables as well. Although all of them might not be used.

| **Variable** | **Type**     | **Description**                                                                                                                                                                      |
|--------------|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| r            | int          | Radius of Spider circle.                                                                                                                                                             |
| canvas       | CustomCanvas | CustomCanvas that the Spider is created on.                                                                                                                                          |
| x            | int          | Quick variable to get the x coordinate of the Spider. It is the first number of location.                                                                                            |
| y            | int          | Quick variable to get the y coordinate of the Spider. It is the second number of location.                                                                                           |
| location     | list         | List of x, y coordinates.                                                                                                                                                            |
| id           | int          | Spider ID.                                                                                                                                                                           |
| connections  | list         | List of containing Connections, it is used in algebraic notation creation. During diagram editing it will not contain connections                                                    |
| context_menu | tkinter.Menu | Variable that holds the context menu of the Spider.                                                                                                                                  |
| wires        | list         | List that contains Wire class objects that have been connected to the Spider.<br/> This is the spider version of Connection.wire.<br/> For Spiders the variable `.wire` is not used. |
| receiver     | Receiver     | Receiver object, usually taken from MainDiagram. Used to send information to the back end portion                                                                                    |
| is_snapped   | bool         | Boolean stating if the Spider is currently snapped to a column or not.                                                                                                               |

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

## Wire

A Wire is a line that connects to Connections, it ties Connections to one-another. On the canvas it is represented as
a line.

The Wire object has multiple types, the types are differentiated by different styles of dashes and colors.

The Wire type can not be manually changed, it is defined by the type of Connections it is added to.

### Wire parameters

| **Param**             | **type**     | **Description**                                                                                                                                        |
|-----------------------|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| canvas                | CustomCanvas | The CustomCanvas that the Wire will be created on.                                                                                                     |
| start_connection      | Connection   | The starting Connection of the Wire. This represents the Connection on the left side of the wire.                                                      |
| receiver              | Receiver     | Receiver object used to send information back to the backend.                                                                                          |
| end_connection        | Connection   | The end Connection of the Wire. This represents the Connection on the right side of the wire.                                                          |
|                       |              |                                                                                                                                                        |
| # **Optional params** |              |                                                                                                                                                        |
| id_                   | int          | An ID for the Wire. Default value is None.                                                                                                             |
| is_temporary          | boolean      | A boolean that tells whether the Wire created is a temporary Wire used for Wire pulling. If this is True it will disable backend for the created Wire. |

### Wire variables

| **Variable** | **Type**     | **Description**                                                             |
|--------------|--------------|-----------------------------------------------------------------------------|
| context_menu | tkinter.Menu | The Menu that is used for creating a context menu on the Wire.              |
| line         | int          | A tag that represents the line created on the CustomCanvas.                 |
| wire_width   | int          | An integer that controls the width of the line created on the CustomCanvas. |
| id           | int          | An ID that represents the Wire.                                             |

### Wire functions

    Wire.

    .delete(action)
        Deletes Wire and removes itself from it's Connections and deletes the line in CustomCanvas.
        
        Parameters:
            action (string): A string that contains the action that will be sent to the backend

    .select()
        Turns the color of the line to green. Used for displaying a selected line.

    .search_highlight_secondary()
        Used as a secondary highlight when conducting searches. Function turns the object orange and adds it to a list of search highlighted items in CustomCanvas.

    .search_highlight_primary()
        Used as the primary highlight when conducting searches. Function turns the object cyan and adds it to a list of search highlighted items in CustomCanvas.

    .deselect()
        Turns the line back to it's original color. This method also readds the wire to it's start and end connection.
        
    .update()
        Creates or moves the Wire line as well as labels at wire ends if type name is defined.

    .show_context_menu(event)
        Creates and displays a context menu for the Wire. 

        Parameters:
            event (tkinter.Event): Event object sent from key press. It holds the location for where the context menu will be displayed.
    
    .define_type()
        Opens an askstring dialog, where you can define the select wire type. This will then add the Wire type to defined wires
         and labels will be created for wires of that type.

    .delete_labels()
        Removes Wire labels from the canvas if they exist.

    .create_spider(event)
        Adds a Spider to the selected part of the Wire.

        Parameters:
            event (tkinter.Event): Event object sent from key press.

    .close_menu()
        Destroys the context menu.

    .connection_data_optimizer()
        Returns 2 lists containing information about the Connections the Wire is attached to.

    .handle_wire_addition_callback()
        Sends Wire creation information to the backend.

    .handle_wire_deletion_callback(action)
        Sends Wire deletion information to the backend.

        Parameters:
            action (string): string detailing whether action is done for a sub-diagram or not.

    .add_end_connection(connection)
        Sends Wire end connection information to the backend.

        Parameters:
            connection (Connection): the end Connection of the Wire.
        