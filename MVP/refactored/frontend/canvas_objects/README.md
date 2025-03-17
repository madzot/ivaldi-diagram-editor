
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

### Box functions

    .set_id(id_)
        Set Box ID.

        Parameters:
            id_ (int): ID that the Box will be given.

    .bind_events()
        Binds events to Box rectangle and Box resizing handle.

    .show_context_menu(event)
        Create and display the Box context menu.

        Parameters:
            event (tkinter.Event): Event object that cointains information.

    .unfold()
        Unfolds the sub-diagram contained in the box. If the Box does not contain a sub-diagram this will not do
        anything.

    .open_editor()
        Opens a CodeEditor for the selected Box. Will display either existing code attached to the Box or will generate 
        a template for the user to enter code.

    .save_box_to_menu()
        Will save the selected Box to config files, allowing it to be selected and created from menus.

    .handle_double_click()
        Handles double click event on Box. If the Box has a sub-diagram it will open the sub-diagram.

    .set_inputs_outputs()
        Opens dialogs that will ask for input/output amounts on a Box. Afterwards the amount of inputs/outputs is
        changed depending on what was written in the dialogs.

    .edit_sub_diagram(save_to_canvasses, add_boxes, switch)
        Will create a sub-diagram in the Box. If a sub-diagram already exists it will open it. Returns sub-diagram
        CustomCanvas object.

        Parameters:
            save_to_canvasses (boolean): (Optional) If true will save the sub-diagram to existing canvases, accessible
                                                    from the left side treeview. Default value is True.
            add_boxes (boolean): (Optional) If true will add boxes to the created sub-diagram. This is used for
                                            CustomCanvas add_boxes value. Default value is True.
            switch (boolean): (Optional) If true will switch to the sub-diagram after creation. Default value is True.

    .close_menu()
        Closes context menu.

    .on_press()
        Handles pressing event on Box. Clears selection, selects box. Sets start_(x/y) and (x/y)_dif variables
        for movement.

    .on_control_press()
        Handles ctrl + button-1 on Box. Will select or unselect current Box depending on previous selection status.
        Will not clear previous selection.

    .on_drag(event)
        Handles dragging/moving the Box.

        Parameters:
            event (tkinter.Event): Event object that holds locations for moving the Box.

    .get_self_collision_ids()
        Updates the collision_ids variable by adding connection tags and label tags into the list.

    .find_collisions(go_to_x, go_to_y)
        Returns a list of tags that (go_to_x, go_to_y) is colliding with. Uses the size of the Box for checking.
    
        Parameters:
            go_to_x (int): x coordinate where to check for collisions.
            go_to_y (int): y coordinate where to check for collisions.

    .on_resize_scroll(event)
        Handles ctrl + scroll  on the Box. Will change the size of the Box.

        Parameters:
            event (tkinter.Event): Event object that determines whether the Box will be made smaller or larger, based on
                                   delta value.

    .on_resize_drag(event)
        Changes the size of the Box based on mouse movement. This is used when pressing and dragging the resize handle.

        Parameters:
            event (tkinter.Event): Event object holding the location of the mouse that the size is changed from.

    .resize_by_connections()
        Resizes the Box to allow all Connections to have space between them.

    .move_label()
        Moves label to the center of the Box.

    .bind_event_label()
        Bind events to the Box label, this is needed because otherwise clicking on the label would disable Box events.

    .edit_label(new_label)
        Asks the user to input a new label, unless a new label is given to the function. Will change the label text.

        Parameters:
            new_label (string): (Optional) If this is given then the application will not ask the user for input and
                                           will change the label to the given string.

    .change_label()
        Creates or updates a label or label text.

    .set_label(new_label)
        Changes label text to given string.

        Parameters:
            new_label (string): Text that the new label will be set to.

    .on_resize_press(event)
        Sets start_(x/y) variables to allow for dragging.

        Parameters:
            event (tkinter.Event): Event object used for start_(x/y) locations.

    .move(new_x, new_y)
        Moves the Box and all objects attached to it to a new location.

        Parameters:
            new_x (int): x coordinate of where to move the Box.
            new_y (int): y coordinate of thwere to move the Box.

    .select()
        Changes the Box outline along with the color of it's Connections to green.

    .search_highlight_secondary()
        Applies the secondary search highlight style to the Box. Changes outline color and Connections colors. Will
        add the Box to CustomCanvas list containing search highlighted objects.

    .search_highlight_primary()
        Applies the primary search highlight style to the Box. Changes outline color and Connections colors. Will 
        add the Box to CustomCanvas list containing search highlighted objects.

    .deselect()
        Turns the outline of the Box and its Connections to black.

    .lock_box()
        Changes locked value of the Box to True.

    .unlock_box()
        Changes locked value of the Box to False.

    .update_size(new_size_x, new_size_y)
        Changes size of the Box. Width to new_size_x and height to new_size_y.

        Parameters:
            new_size_x (int): New width of the Box.
            new_size_y (int): New height of the Box.

    .update_position()
        Updates the position of the Box on the CustomCanvas.

    .update_connections()
        Updates Connection locations that are attached to the Box.

    .update_wires()
        Updates Wire that are attached to the Box.

    .update_io()
        Updates Box inputs and outputs based on the Box code.

    .add_wire(wire)
        Adds Wire to Box.
        
        Parameters:
            wire (Wire): Wire that will be added to the Box.

    .add_left_connection(id_, connection_type)
        Adds a Connection to the left side of the Box. The type of the Connection can be specified.

        Parameters:
            id_ (int): ID that will be added to the Connection.
            connection_type (ConnectionType): The type that will be added to the Connection.

    .add_right_connection()
        Adds a Connection to the right side of the Box. The type of the Connection can be specified.

        Parameters:
            id_ (int): ID that will be added to the Connection.
            connection_type (ConnectionType): The type that will be added to the Connection.

    .remove_connection(circle)
        Removes a certain Connection from the Box.

        Parameters:
            circle (Connection): The Connection that will be removed from the Box.

    .delete_box(keep_sub_diagram, action)
        Deletes the Box.

        Parameters:
            keep_sub_diagram (boolean): Determines whether to delete the sub-diagram if it exists in the Box.
            action (string): Determines if the action of deleting the box is done for sub-diagram creation.
    
    .is_illegal_move(connection, new_x)
        Returns boolean stating whether or not movement to the new_x location is legal based on a given Connection.
            
        Parameters:
            connection (Connection): The Connection that move legality to new_x will be checked for.
            new_x (int): X coordinate where to check legality from.

    .get_connection_coordinates(side, index)

