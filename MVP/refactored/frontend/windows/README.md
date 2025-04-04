
# Windows

The `windows` directory holds classes that are separate windows. Such as MainDiagram, CodeEditor, HelpWindow.

---

## CodeEditor

`CodeEditor` is the class that holds the window for the code editor and its functions.

The editor itself is imported from `chlorophyll` package.

### CodeEditor parameters

| **Param**             | **Type**    | **Description**                                                                                                 | 
|-----------------------|-------------|-----------------------------------------------------------------------------------------------------------------|
| main_diagram          | MainDiagram | MainDiagram object used for accessing functions.                                                                |
|                       |             |                                                                                                                 |
| # **Optional params** |             |                                                                                                                 |
| box                   | Box         | Box object that the CodeEditor was opened from.                                                                 |
| label                 | String      | Label that is used for the function. This param is used when the editor is opened from ManageMethods.           |
| code                  | String      | Code is the string that will be displayed in the editor when it is opened.                                      |
| is_generated          | bool        | Boolean that defines whether the code in the editor is generated, if it is generated then saving is turned off. |

### CodeEditor variables

| **Variable**   | **Type**             | **Description**                                                               | 
|----------------|----------------------|-------------------------------------------------------------------------------|
| main_diagram   | MainDiagram          | MainDiagram object used for accessing functions.                              |
| box            | Box                  | Box object that the code editor was opened from, if it was opened from a Box. |
| label          | str                  | Label that is attached to the code.                                           |
| window         | tkinter.Toplevel     | Toplevel object that is the actual window where everything is rendered.       |
| code_view      | chlorophyll.CodeView | CodeView object where code is written. This is a wrapper of tkinter.Text      |
| save_as_button | tkinter.Button       | Button that is used for exporting the code file.                              |
| save_button    | tkinter.Button       | Button that is used for saving the code inside the application.               |
| code_exporter  | CodeExporter         | CodeExporter object that deals with exporting code.                           |

### CodeEditor functions

    .generate_function_name_from_label()
        Takes the label of the Box that the editor has been opened from and generates a python usable function name from 
        the label. Returns the generated name.

    .confirm_exit()
        Asks for confirmation before closing the window.

    .save_handler(destroy)
        Handles saving.

        Parameters:
            destroy (bool): (Optional) Specify whether to close the CodeEditor after handling save.

    .save_as()
        Activates exporting from CodeExporter and then activates regular save handling.

    .save_to_file()
        Saves the current function to functions_conf json file.

    .update_boxes()
        Updates i/o of Boxes on the canvas and adds new code to label_content variable.

---

## HelpWindow

`HelpWindow` is the window that shows the user keybind that are usable in the application.
It is opened when pressing on the help icon on the right side of the `Toolbar`, it is represented by a circle with a
question mark in the middle.


### HelpWindow params

| **Param**             | **Type** | **Description**                           |
|-----------------------|----------|-------------------------------------------|
|                       |          |                                           |
| # **Optional params** |          |                                           |
| master                | Tk       | Used for attaching window to application. |

### HelpWindow variables

| **Variable**           | **Type**           | **Description**                                                |
|------------------------|--------------------|----------------------------------------------------------------|
| keybind_frame          | tkinter.Frame      | Frame object that all key-binds and descriptions are added to. |
| key_binds_descriptions | list               | List that holds tuples of keybind and its description.         |
| items_per_page         | int                | Defines how many key-binds are shown per page.                 |
| current_page           | int                | Current page number.                                           |
| pagination_frame       | tkinter.Frame      | Frame that pagination buttons are added to.                    |
| backward_logo          | ImageTk.PhotoImage | Icon used to show backwards movement between pages.            |
| backward               | tkinter.Button     | Button that goes backwards in pagination.                      |
| forward_logo           | ImageTk.PhotoImage | Icon used to show forward movement between pages.              |
| forward                | tkinter.Button     | Button that moves page forward.                                |
| page_label             | tkinter.Label      | Label that shows current page number in the pagination frame.  |

### HelpWindow functions

    .display_key_binds()
        Adds items from key_binds_descriptions to the keybind_frame.

    .next_page()
        Goes to the next set of keybinds.

    .previous_page()
        Goes to the previous set of keybinds.

    .update_page_label()
        Updates page_label. Updates page numbers displayed on the pagination frame.

---

## MainDiagram

`MainDiagram` is the main class of the application. All objects are accessible through this. It is the main window that
you see when using the application.

### MainDiagram params

| **Param**             | **Type** | **Description**                                          | 
|-----------------------|----------|----------------------------------------------------------|
| receiver              | Receiver | Receiver object used to send information to the backend. |
|                       |          |                                                          |
| # **Optional params** |          |                                                          |
| load                  | bool     | Boolean to load items in to the MainDiagram on creation. |


### MainDiagram variable

| **Variable**            | **Type**                | **Description**                                                                                                                                          |
|-------------------------|-------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| receiver                | Receiver                | Receiver object used for sending information to the backend.                                                                                             |
| toolbar                 | Toolbar                 | Component for MainDiagram.                                                                                                                               |
| is_search_active        | bool                    | Boolean that is True when search results are active.                                                                                                     |
| selector                | Selector                | Selector object used for selecting items on the CustomCanvas.                                                                                            |
| search_results          | list                    | List containing the results of a search.                                                                                                                 |
| active_search_index     | int                     | Integer that holds the index of which search result is currently primarily highlighted.                                                                  |
| search_objects          | dict                    | A dictionary that holds the search result and a list of its objects.                                                                                     |
| wire_objects            | dict                    | A dictionary that holds the search result and a list of Wires that are highlighted with the result.                                                      |
| custom_canvas           | CustomCanvas            | The currently displayed CustomCanvas.                                                                                                                    |
| search_window           | SearchWindow            | SearchWindow object.                                                                                                                                     |
| is_tree_visible         | bool                    | Boolean showing if tree_view is visible or hidden.                                                                                                       |
| canvasses               | dict                    | A dictionary holding the ID and CustomCanvas object of all CustomCanvases in the MainDiagram.                                                            |
| tree_root_id            | str                     | Root canvas ID used for tree_view.                                                                                                                       |
| control_frame           | ttkbootstrap.Frame      | Frame on the right of the application that holds buttons for diagram editing.                                                                            |
| project_exporter        | ProjectExporter         | ProjectExporter object used for exporting diagrams.                                                                                                      |
| importer                | Importer                | Importer object used for importing diagrams.                                                                                                             |
| undefined_box_button    | ttkbootstrap.Button     | Button to add an undefined Box onto the CustomCanvas.                                                                                                    |
| shape_dropdown_button   | ttkbootstrap.Menubutton | A dropdown button that allows the user to select the shape of newly created Boxes.                                                                       |
| shape_dropdown_menu     | ttkbootstrap.Menu       | The menu that the shape_dropdown_button will show.                                                                                                       |
| boxes                   | dict                    | Preset Boxes taken from the boxes_conf.json file.                                                                                                        |
| quick_create_boxes      | list                    | Preset Boxes that can be created from the context menu on CustomCanvas.                                                                                  |
| add_box_dropdown_button | ttkbootstrap.Menubutton | Button to open the dropdown menu for preset Box adding.                                                                                                  |
| add_box_dropdown_menu   | ttkbootstrap.Menu       | Menu that is shown after pressing on the add_box_dropdown_button.                                                                                        |
| manage_boxes            | ttkbootstrap.Button     | Button that opens a window to manage Box presets.                                                                                                        |
| quick_create_booleans   | list                    | List containing tkinter.BooleanVar that is used for remembering what preset Boxes are added to quick create when displaying quick creation manage window. |
| manage_quick_create     | ttkbootstrap.Button     | Button to open the quick creation management window.                                                                                                     |
| manage_methods_button   | ttkbootstrap.Button     | Button to open method management window.                                                                                                                 |
| spider_box              | ttkbootstrap.Button     | Button to add a Spider to the CustomCanvas.                                                                                                              |
| rename                  | ttkbootstrap.Button     | Button to rename the currently opened CustomCanvas.                                                                                                      |
| random                  | ttkbootstrap.Button     | Button to create Wires at random on current CustomCanvas.                                                                                                |
| alg_not                 | ttkbootstrap.Button     | Button to generate algebraic notation for the current diagram.                                                                                           |
| draw_wire_button        | ttkbootstrap.Button     | Button to activate draw wire mode on the CustomCanvas.                                                                                                   |
| save_buttons            | dict                    | Dictionary holding the label and function of input/output adding and removal buttons.                                                                    |
| json_file_hash          | str                     | Hash of boxes_conf file to check for updates.                                                                                                            |
| label_content           | dict                    | Dictionary that holds function labels and their content.                                                                                                 |
| manage_methods          | ManageMethods           | ManageMethods window.                                                                                                                                    |
| import_counter          | int                     | Import counter used to change IDs of objects when same diagram has been imported multiple times as sub-diagrams.                                         |