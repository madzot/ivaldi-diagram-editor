
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

| **Variable**             | **Type**               | **Descriptions**                                                                                |
|--------------------------|------------------------|-------------------------------------------------------------------------------------------------|
| selector                 | Selector               | The Selector object used for dealing with Selected objects.                                     |
| parent_diagram           | CustomCanvas           | The parent diagram of the CustomCanvas.                                                         |
| main_diagram             | MainDiagram            | The MainDiagram object.                                                                         |
| master                   | Tk                     | The parent widget of this canvas.                                                               |
| is_search                | boolean                | Specifies whether the canvas is created for the searching window.                               |
| boxes                    | list                   | A list of Boxes. Contains every Box that exists on the Canvas at the moment.                    |
| outputs                  | list                   | A list of Connections. Contains the outputs of the diagram (the Connections on the right side). |
| inputs                   | list                   | A list of Connections. Contains the inputs of the diagram (the Connections on the left side).   |
| spiders                  | list                   |                                                                                                 |
| wires                    | list                   |                                                                                                 |
| corners                  | list                   |                                                                                                 |
| temp_wire                | Wire                   |                                                                                                 |
| temp_end_connection      | Connection             |                                                                                                 |
| pulling_wire             | boolean                |                                                                                                 |
| quick_pull               | boolean                |                                                                                                 |
| receiver                 | Receiver               |                                                                                                 |
| current_wire_start       | Connection             |                                                                                                 |
| current_wire             | Wire                   |                                                                                                 |
| draw_wire_mode           | boolean                |                                                                                                 |
| diagram_source_box       | Box                    |                                                                                                 |
| name                     | int                    |                                                                                                 |
| name_text                | string                 |                                                                                                 |
| select_box               | int                    |                                                                                                 |
| selecting                | boolean                |                                                                                                 |
| copier                   | Copier                 |                                                                                                 |
| hypergraph_exporter      | HypergraphExporter     |                                                                                                 |
| context_menu             | tkinter.Menu           |                                                                                                 |
| tree_logo                | PIL.ImageTk.PhotoImage |                                                                                                 |
| search_result_button     | SearchResultButton     |                                                                                                 |
| box_shape                | string                 |                                                                                                 |
| copy_logo                | PIL.ImageTk.PhotoImage |                                                                                                 |
| total_scale              | float                  |                                                                                                 |
| delta                    | float                  |                                                                                                 |
| prev_width_max           | int                    |                                                                                                 |
| prev_height_max          | int                    |                                                                                                 |
| prev_width_min           | int                    |                                                                                                 |
| prev_height_min          | int                    |                                                                                                 |
| prev_scale               | float                  |                                                                                                 |
| pan_history_x            | int                    |                                                                                                 |
| pan_history_y            | int                    |                                                                                                 |
| pan_speed                | int                    |                                                                                                 |
| hover_item               | Any                    |                                                                                                 |
| search_result_highlights | list                   |                                                                                                 |
| wire_label_tags          | list                   |                                                                                                 |



