
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

HelpWindow is the window that shows the user keybind that are usable in the application.
It is opened when pressing on the help icon on the right side of the Toolbar, it is represented by a circle with a
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
