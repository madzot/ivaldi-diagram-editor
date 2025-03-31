















## Toolbar

Toolbar is the file menu bar of our application. It holds different save, generation, importing functions along with settings.

```
Toolbar
|
└--- File
|    └--- Save as
|    |    └--- png file
|    |    └--- project
|    |    └--- hypergraph
|    |
|    └--- Generate
|    |    └--- TikZ
|    |    └--- code
|    |
|    └--- New
|    └--- Import new diagram
|    └--- Import as sub-diagram
|
└--- Edit
|    └--- Search in Project
|
└--- View
     └--- Visualize hypergraph

```

### Toolbar parameters

| **Param**    | **Type**    | **Description**                                             | 
|--------------|-------------|-------------------------------------------------------------|
| main_diagram | MainDiagram | MainDiagram used to access functions offered in the toolbar |

### Toolbar variables

| **Variable**     | **Type**           | **Description**                                                                   |
|------------------|--------------------|-----------------------------------------------------------------------------------|
| main_diagram     | MainDiagram        | MainDiagram object used to access functions.                                      |
| file_button      | tkinter.Menubutton | Menubutton that holds File menu.                                                  |
| file_menu        | tkinter.Menu       | Menu that is opened when pressing file_button. Holds File sub-menus and commands. |
| save_submenu     | tkinter.Menu       | Save sub-menu. Holds commands about saving.                                       |
| generate_submenu | tkinter.Menu       | Generation sub-menu. Holds commands about generation.                             |
| edit_button      | tkinter.Menubutton | Menubutton that holds Edit menu.                                                  |
| edit_menu        | tkinter.Menu       | Menu that is opened when pressing edit_button.                                    |
| view_button      | tkinter.Menubutton | Menubutton that holds View menu.                                                  |
| view_menu        | tkinter.Menu       | Menu for View commands.                                                           |
| help_logo        | ImageTk.PhotoImage | Help logo that is used to open the help window.                                   |

### Toolbar functions.

    .open_help_window()
        Creates HelpWindow object. Displaying it in a new window.
    
    .import_sub_diagram()
        Imports a new diagram as a sub-diagram of the currently opened diagram.
    
    .confirm_deletion()
        Opens a dialog for the user asking for confirmation about unsaved progress deletion.

    .handle_new_graph(import_)
        Handles creating new diagram. Will delete everything except root canvas if root canvas has any objects.
        If specified with parameter then it will also load a new diagram to the new blank canvas.
        
        Parameters:
            import_ (bool): (Optional) Specifies whether a new diagram should be imported after deleting the old diagram. Default is False.

