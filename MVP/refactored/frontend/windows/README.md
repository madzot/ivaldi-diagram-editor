
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

| **Variable**            | **Type**                | **Description**                                                                                                                                           |
|-------------------------|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| receiver                | Receiver                | Receiver object used for sending information to the backend.                                                                                              |
| toolbar                 | Toolbar                 | Component for MainDiagram.                                                                                                                                |
| is_search_active        | bool                    | Boolean that is True when search results are active.                                                                                                      |
| selector                | Selector                | Selector object used for selecting items on the CustomCanvas.                                                                                             |
| search_results          | list                    | List containing the results of a search.                                                                                                                  |
| active_search_index     | int                     | Integer that holds the index of which search result is currently primarily highlighted.                                                                   |
| search_objects          | dict                    | A dictionary that holds the search result and a list of its objects.                                                                                      |
| wire_objects            | dict                    | A dictionary that holds the search result and a list of Wires that are highlighted with the result.                                                       |
| custom_canvas           | CustomCanvas            | The currently displayed CustomCanvas.                                                                                                                     |
| search_window           | SearchWindow            | SearchWindow object.                                                                                                                                      |
| is_tree_visible         | bool                    | Boolean showing if tree_view is visible or hidden.                                                                                                        |
| canvasses               | dict                    | A dictionary holding the ID and CustomCanvas object of all CustomCanvases in the MainDiagram.                                                             |
| tree_root_id            | str                     | Root canvas ID used for tree_view.                                                                                                                        |
| control_frame           | ttkbootstrap.Frame      | Frame on the right of the application that holds buttons for diagram editing.                                                                             |
| project_exporter        | ProjectExporter         | ProjectExporter object used for exporting diagrams.                                                                                                       |
| importer                | Importer                | Importer object used for importing diagrams.                                                                                                              |
| undefined_box_button    | ttkbootstrap.Button     | Button to add an undefined Box onto the CustomCanvas.                                                                                                     |
| shape_dropdown_button   | ttkbootstrap.Menubutton | A dropdown button that allows the user to select the shape of newly created Boxes.                                                                        |
| shape_dropdown_menu     | ttkbootstrap.Menu       | The menu that the shape_dropdown_button will show.                                                                                                        |
| boxes                   | dict                    | Preset Boxes taken from the boxes_conf.json file.                                                                                                         |
| quick_create_boxes      | list                    | Preset Boxes that can be created from the context menu on CustomCanvas.                                                                                   |
| add_box_dropdown_button | ttkbootstrap.Menubutton | Button to open the dropdown menu for preset Box adding.                                                                                                   |
| add_box_dropdown_menu   | ttkbootstrap.Menu       | Menu that is shown after pressing on the add_box_dropdown_button.                                                                                         |
| manage_boxes            | ttkbootstrap.Button     | Button that opens a window to manage Box presets.                                                                                                         |
| quick_create_booleans   | list                    | List containing tkinter.BooleanVar that is used for remembering what preset Boxes are added to quick create when displaying quick creation manage window. |
| manage_quick_create     | ttkbootstrap.Button     | Button to open the quick creation management window.                                                                                                      |
| manage_methods_button   | ttkbootstrap.Button     | Button to open method management window.                                                                                                                  |
| spider_box              | ttkbootstrap.Button     | Button to add a Spider to the CustomCanvas.                                                                                                               |
| rename                  | ttkbootstrap.Button     | Button to rename the currently opened CustomCanvas.                                                                                                       |
| random                  | ttkbootstrap.Button     | Button to create Wires at random on current CustomCanvas.                                                                                                 |
| alg_not                 | ttkbootstrap.Button     | Button to generate algebraic notation for the current diagram.                                                                                            |
| draw_wire_button        | ttkbootstrap.Button     | Button to activate draw wire mode on the CustomCanvas.                                                                                                    |
| save_buttons            | dict                    | Dictionary holding the label and function of input/output adding and removal buttons.                                                                     |
| json_file_hash          | str                     | Hash of boxes_conf file to check for updates.                                                                                                             |
| label_content           | dict                    | Dictionary that holds function labels and their content.                                                                                                  |
| manage_methods          | ManageMethods           | ManageMethods window.                                                                                                                                     |
| import_counter          | int                     | Import counter used to change IDs of objects when same diagram has been imported multiple times as sub-diagrams.                                          |


### MainDiagram functions

    .calculate_boxes_json_file_hash()
        Returns a hash of the boxes_conf.json file.
        
        This is used to check if a file has been changed.

    .load_functions()
        Load functions configuration.

        Loads configuration from functions_conf.json file and adds it to the label_content variable.

    .generate_code()
        Generate code from diagram and display it in the CodeEditor.

    .open_search_window()
        Opens a search window, or highlights the existing one.

    .cancel_search_results()
        Disable current search result highlighting.

    .move_between_search_results(up)
        Moves the primary highlight to the next or previous result.
        
        Parameters:
            up (bool): Boolean if movement is to next result.

    .update_search_result_button_texts()
        Update text on SearchResultButton.

    .check_search_result_canvas(index)
        Check CustomCanvas of search result items at index in results.

        Checks if the items at index of search results are on the same CustomCanvas.
        If they are on a different CustomCanvas then the active canvas will be changed to the new one.

        Parameters:
            index (int): Index of search result to check.

    .highlight_search_result_by_index(index)
        Highlight search results at index.

        Will take search results and use primary highlighting on the result at given index.

    .change_function_label(old_label, new_label)
        Changes old_label of function to new_label.

    .create_algebraic_notation()
        Opens a window to display algebraic notation of the diagram.

    .visualize_as_graph(canvas)
        Opens a window that displays the hypergraph visualization of the given CustomCanvas.

        Parameters:
            canvas (CustomCanvas): CustomCanvas that will be visualized.

    .copy_to_clipboard(text_box)
        Takes text from tkinter.Text and copies it.

        Parameters:
            text_box (tkinter.Text): Text object of which the contents will be copied.

    .open_children(parent)
        Opens the children of a parent in the treeview.

        Parameters:
            parents (str): treeview item id

    .get_canvas_by_id(canvas_id)
        Returns the CustomCanvas object with the given ID.

        Parameters:
            canvas_id (int): ID of CustomCanvas to return.

    .update_canvas_name(canvas)
        Update the CustomCanvas name in the treeview.

        Parameters: 
            canvas (CustomCanvas): CustomCanvas to update name for.

    .rename()
        Rename the currently opened CustomCancas.

        Opens a dialog for the user to enter a new name.

    .switch_canvas(canvas)
        Switch the currently displayed canvas to the given canvas.

        Parameters:
            canvas (CustomCanvas): CustomCanvas that will be switched to.

    .del_from_canvasses(canvas)
        Removes given canvas from treeview and canvasses variable.

        Parameters:
            canvas (CustomCanvas): CustomCanvas to delete.

    .on_tree_select()
        Handles selection on treeview. Will switch to selected canvas.

    .add_diagram_input(id_)
        Add an input connection to the currently opened diagram.
        If a canvas is a sub-diagram then an input connection is also added to its source box.
    
        Parameters:
            id_ (int): (Optional) ID that will be given to the diagram input Connection.

    .add_diagram_output(id_)
        Add an output connection to the currently opened diagram.
        If a canvas is a sub-diagram then an output connection is also added to its source box.

        Parameters:
            id_ (int) (Optional) ID that will be given to the diagram output Connection.

    .remove_diagram_input()
        Remove an input connection from the diagram.

    .remove_diagram_output()
        Remove an output connection from the diagram.

    .find_connection_to_remove(side)
        Return diagram input or output Connection to remove.

        Parameters: 
            side (str): Side of where to remove Connection from.

    .manage_boxes_method()
        Opens the manage boxes window.

    .manage_quick_create()
        Opens the manage quick create window.

    .update_add_box_dropdown_menu()
        Update the add_box_dropdown_menu to hold all Box presets.

    .remove_option(option)
        Remove a preset Box option from the configuration files.
    
        Parameters:
            option (str): Name of the preset Box that will be removed.

    .get_boxes_from_file()
        Load Boxes from configuration files into the application.

    .add_custom_box(name, canvas)
        Adds a custom preset Box to the canvas.

        Parameters: 
            name (str): Name of the preset that will be added.
            canvas (CustomCanvas): CustomCanvas that the Box will be added to.

    .save_box_to_diagram_menu(box)
        Save a new Box to presets.
    
        Parameters:
            box (Box): Box that will be saved as a preset.

    .set_title(filename)
        Changes the title of the MainDiagram window. 

        Parameters:
            filename (str): New title of MainDiagram window.

    .confirm_exit()
        Ask user for confirmation about exiting the application.

    .save_to_file()
        Save current diagram to json file.

    .load_from_file()
        Load a diagram into the diagram.

    .update_shape_dropdown_menu()
        Update the shape dropdown menu to include all shapes.

    .toggle_treeview()
        Toggles the treeview on the left side of the application.

    .pairwise(iterable)
        Creates pairs of an iterable.
        s -> (s0, s1), (s2, s3), (s4, s5), ...

        Parameters:
            iterable (iterable): Iterable that pairs will be made from.

    .generate_tikz(canvas)
        Return TikZ code for given CustomCanvas.

        Parameters:
            camvas (CustomCanvas): Canvas that TikZ will be generated for.

    .generate_png(canvas, file_path)
        Generates a png file of the given canvas to the file_path location.

        Parameters:
            canvas (CustomCanvas): CustomCanvas to generate png for.
            file_path (str): Location where png file will be created.

    .generate_matplot(canvas, show_connections)
        Generates a matplot figure of a given canvas.
    
        Parameters:
            canvas (CustomCanvas): CustomCanvas that matplot is generated for.
            show_connections (bool): States whether to show regular connections on the figure.

    .get_wire_style(wire)
        Get style for Wire in matplot. Returns a tuple of color and dash style for Wire.

        Parameters:
            wire (Wire): Wire that style is gotten for.






































































