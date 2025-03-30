




## SearchResultButton

SearchResultButton is a button that is shown after a search has been conducted on the CustomCanvas. 

The buttons purpose is to display information about the search and allow moving between results.

It shows the number of results as well as the currently primarily highlighted parts index.

It has 2 buttons that allow moving between results.

It has a button to turn off search results. It will turn off search highlights and toggle off the button.

### SearchResultButton parameters

| **Params**   | **Type**    | **Description**                                      |
|--------------|-------------|------------------------------------------------------|
| master       | Tk          | Master Tk object that the button will be created on. |
| main_diagram | MainDiagram | MainDiagram object to access functions.              |
| **kwargs     |             | Keyword arguments for LabelFrame.                    |

### SearchResultButton variables

| **Variable**       | **Type**           | **Description**                                                   |
|--------------------|--------------------|-------------------------------------------------------------------|
| main_diagram       | MainDiagram        | MainDiagram object used for accessing functions.                  |
| close_button_frame | tkinter.LabelFrame | LabelFrame that holds the close button.                           |
| close_icon         | ImageTk.PhotoImage | Close icon that is displayed on close button.                     |
| up_icon            | ImageTk.PhotoImage | Up icon that is displayed on the up button.                       |
| down_icon          | ImageTk.PhotoImage | Down icon that is displayed on the down button.                   |
| info_frame         | tkinter.LabelFrame | LabelFrame that holds information text.                           |
| info_text          | tkinter.StringVar  | Holds string that is displayed in information part of the button. |
| info_label         | tkinter.Label      | Label that holds info_text and is displayed on info_frame.        |
