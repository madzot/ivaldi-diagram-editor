
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


