
# Components

This directory holds application 'components'. These are parts of the application that do not have their own
window. Things such as `CustomCanvas` or `toolbar` because they do not have their own window and are both rendered
inside MainDiagram
---

## CustomCanvas

`CustomCanvas` is a wrapper for `tkinter.Canvas` that all `canvas_objects` are drawn on.

### CustomCanvas parameters

| **Parameter**         | **Type**     | **Description**                                                                                                                                                                 | 
|-----------------------|--------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| master                | Tk           | The parent widget of this canvas. If None, tkinter will attempt to use the default root.                                                                                        |
| main_diagram          | MainDiagram  | MainDiagram object used for accessing variables across the application.                                                                                                         |
|                       |              |                                                                                                                                                                                 |
| # **Optional params** |              |                                                                                                                                                                                 |
| id_                   | int          | Custom ID for canvas.                                                                                                                                                           |
| search                | boolean      | States whether the CustomCanvas object is created for the search window and is not part of the regular diagram.<br/> Default value is `False`                                   |
| diagram_source_box    | Box          | Source Box for sub-diagram. A Box object that the currently CustomCanvas is located in. This is only used if the a CustomCanvas is a sub-diagram.<br/> Default value is `None`. |
| parent_diagram        | CustomCanvas | The parent diagram of this CustomCanvas. `None` if root diagram. Used only when CustomCanvas is a sub-diagram.                                                                  |
| **kwargs              |              | Kwargs for `tkinter.Canvas`                                                                                                                                                     |


### CustomCanvas variables

| **Variable**             | **Type**               | **Descriptions**                                                                                                                                                    |
|--------------------------|------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| selector                 | Selector               | The Selector object used for dealing with Selected objects.                                                                                                         |
| parent_diagram           | CustomCanvas           | The parent diagram of the CustomCanvas.                                                                                                                             |
| main_diagram             | MainDiagram            | The MainDiagram object.                                                                                                                                             |
| master                   | Tk                     | The parent widget of this canvas.                                                                                                                                   |
| is_search                | boolean                | Specifies whether the canvas is created for the searching window.                                                                                                   |
| boxes                    | list                   | List of Boxes. Contains every Box objects that exists on the Canvas at the moment.                                                                                  |
| outputs                  | list                   | List of Connections. Contains the outputs of the diagram (the Connections on the right side).                                                                       |
| inputs                   | list                   | List of Connections. Contains the inputs of the diagram (the Connections on the left side).                                                                         |
| spiders                  | list                   | List of Spiders. Contains all Spider objects present in the CustomCanvas.                                                                                           |
| wires                    | list                   | List of Wires. Contains all Wire objects present in the CustomCanvas.                                                                                               |
| corners                  | list                   | List of Corners. Contains all Corner objects that are on the CustomCanvas.                                                                                          |
| temp_wire                | Wire                   | Temporary Wire variable. Used when pulling/creating wires, the temporary wire is the Wire that is seen during Wire pulling.                                         |
| temp_end_connection      | Connection             | Temporary end connection Variable. During Wire pulling an end Connection is required to create a temporary Wire. This is the variable for the temporary Connection. |
| pulling_wire             | boolean                | Boolean stating whether or not wire pulling is currently active.                                                                                                    |
| quick_pull               | boolean                | Boolean stating whether quick pull (wire pulling from double clicking a Connection) is active.                                                                      |
| receiver                 | Receiver               | The Receiver object that is used to send information to the backend.                                                                                                |
| current_wire_start       | Connection             | Connection that is used to remember where the Wire creation was started from.                                                                                       |
| draw_wire_mode           | boolean                | Boolean stating whether the CustomCanvas is in draw wire mode.                                                                                                      |
| diagram_source_box       | Box                    | Box that holds the CustomCanvas object, used when CustomCanvas is a sub-diagram.                                                                                    |
| name                     | int                    | Tag that represents the name of the CustomCanvas on the Canvas.                                                                                                     |
| name_text                | string                 | String of CustomCanvas name.                                                                                                                                        |
| select_box               | int                    | The rectangle that is created when selecting items.                                                                                                                 |
| selecting                | boolean                | Boolean stating if selecting is active.                                                                                                                             |
| copier                   | Copier                 | Copier object.                                                                                                                                                      |
| hypergraph_exporter      | HypergraphExporter     | HypergraphExporter object.                                                                                                                                          |
| context_menu             | tkinter.Menu           | Tkinter Menu object used for creating context menus on the CustomCanvas.                                                                                            |
| tree_logo                | PIL.ImageTk.PhotoImage | Logo that is used for the button that opens the treeview.                                                                                                           |
| search_result_button     | SearchResultButton     | SearchResultButton object.                                                                                                                                          |
| box_shape                | string                 | Default shape of a Box created in CustomCanvas.                                                                                                                     |
| copy_logo                | PIL.ImageTk.PhotoImage | Logo that is used for in the copy button of TikZ interface.                                                                                                         |
| total_scale              | float                  | The current scale of the CustomCanvas. Minimum scale is `1.0`.                                                                                                      |
| delta                    | float                  | The amount that will be zoomed in or out. Default is `0.75`.                                                                                                        |
| prev_width_max           | int                    | Previous maximum width of the CustomCanvas. Updated on CustomCanvas size change.                                                                                    |
| prev_height_max          | int                    | Previous maximum height of the CustomCanvas. Updated on CustomCanvas size change.                                                                                   |
| prev_width_min           | int                    | Previous minimum width of the CustomCanvas. Updated on CustomCanvas size change.                                                                                    |
| prev_height_min          | int                    | Previous minimum height of the CustomCanvas. Updated on CustomCanvas size change.                                                                                   |
| prev_scale               | float                  | Previous zoom scale of CustomCanvas.                                                                                                                                |
| pan_speed                | int                    | Speed of panning.                                                                                                                                                   |
| hover_item               | Any                    | Item that is currently being hovered over. This may not show all items being hovered on.                                                                            |
| search_result_highlights | list                   | List containing highlighted objects when showing search results.                                                                                                    |
| wire_label_tags          | list                   | List of tags that represent the Wire labels on the CustomCanvas.                                                                                                    |


### CustomCanvas functions

    .on_hover(item)
        Activated when some items are being hovered over. Updates the hover_item variable.

        Parameters:
            item (Any): A canvas_object widget to change hover_item to.

    .on_leave_hover()
        Changes hover_item to `None`. Activated when leaving hover over objects.

    .scale_item(event)
        Activates `.on_resize_scroll(event)` on the item that is being hovered over.

        Parameters:
            event (tkinter.Event): Event object passed from key press.

    .toggle_search_results_button()
        Toggles visibility of search result button based on active search status. Search result button is the button
        used for moving between search results and cancelling search results.

    .update_search_result_button()
        Updates the search result button, moving it to the correct location.

    .remove_search_highlights()
        Removes search highlights from CustomCanvas. Toggles search results button.

    .select_all()
        Selects all the objects on the CustomCanvas.

    .update_prev_winfo_size()
        Updates previous height/width variables with current CustomCanvas size.

    .pan_horizontal(event)
        Moves objects on the CustomCanvas horizontally.
        
        Parameters:
            event (tkinter.Event): Event object passed from key press.

    .pan_vertical(event)
        Moves objects on the CustomCanvas vertically.

        Parameters:
            event (tkinter.Event): Event object passed from key press.

    .move_boxes_spider(attr, multiplier)
        Moves boxes and spiders on the CustomCanvas along the x or y axis. 

        Parameters:
            attr (string): `x` or `y`. Axis to move objects along.
            multiplier (int): -1 or 1. Determines whether objects will be moved towards negative coordinates or positive coordinates.

    .delete(*args)
        Tkinter.Canvas delete function with added hypergraph changes.

        *args: Tkinter.Canvas .delete(*args)

    .update_after_treeview(canvas_width, treeview_width, to_left)
        Updates item locations on the CustomCanvas to account for new space created or space taken away by the treeview.
        
        Parameters:
            canvas_width (int): Current CustomCanvas width.
            treeview_width (int): Treeview width if open.
            to_left (bool): Determines if boxes should be moved to the left due to treeview being opened.

    .handle_right_click(event)
        Handles right click event on CustomCanvas. Possible actions are finishing selection, cancelling wire pulling,
        showing context menu.

        Parameters:
            event (tkinter.Event): Event object passed on key press.

    .set_name(name)
        Set new name for CustomCanvas.

        Parameters:
            name (string): New name for CustomCanvas.

    .reset_zoom()
        Resets the scale of the CustomCanvas to be zoomed out all the way.

    .zoom(event)
        Zooming main function, actived on scrolling on CustomCanvas. Scales the canvas.

        Parameters:
            event (tkinter.Event): Event object passed on key press.

















