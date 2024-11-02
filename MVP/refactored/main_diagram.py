import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from MVP.refactored.custom_canvas import CustomCanvas
from MVP.refactored.modules.notations.hypergraph_notation.hypergraph_notation import HypergraphNotation
from MVP.refactored.modules.notations.notation_tool import get_notations, is_canvas_complete
from MVP.refactored.util.exporter.project_exporter import ProjectExporter
from MVP.refactored.util.importer import Importer


class MainDiagram(tk.Tk):
    def __init__(self, receiver, load=False):
        super().__init__()
        self.title("Dynamic String Diagram Canvas")
        self.receiver = receiver

        screen_width_min = round(self.winfo_screenwidth() / 1.5)
        screen_height_min = round(self.winfo_screenheight() / 1.5)

        self.custom_canvas = CustomCanvas(self, None, self.receiver, self, self, False, width=screen_width_min,
                                          height=screen_height_min, bg="white")

        self.tree = ttk.Treeview(self)
        self.tree.pack(side=tk.LEFT)
        self.tree.config(height=20)  # Number of visible rows

        # Add some items to the tree
        self.tree.insert("", "end", str(self.custom_canvas.id), text="Root")
        self.canvasses = {str(self.custom_canvas.id): self.custom_canvas}
        self.custom_canvas.set_name("root")
        self.tree_root_id = str(self.custom_canvas.id)
        # Bind the treeview to the click event
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

        self.custom_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.control_frame = tk.Frame(self)
        self.wm_minsize(screen_width_min, screen_height_min)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.protocol("WM_DELETE_WINDOW", self.do_i_exit)
        self.project_exporter = ProjectExporter(self.custom_canvas)
        self.importer = Importer(self.custom_canvas)
        # Add undefined box
        self.undefined_box_button = tk.Button(self.control_frame, text="Add Undefined Box",
                                              command=self.custom_canvas.add_box, bg="white", width=18)
        self.undefined_box_button.pack(side=tk.TOP, padx=5, pady=5)

        self.boxes = {}

        # Create Menubutton and Menu for dropdown
        self.dropdown_button = tk.Menubutton(self.control_frame, text="Select Box to Add", relief="raised")
        self.dropdown_menu = tk.Menu(self.dropdown_button, tearoff=0)
        self.dropdown_button.config(menu=self.dropdown_menu)
        self.dropdown_button.pack(side=tk.TOP, padx=5, pady=5)
        self.dropdown_button.config(width=20, background="white")
        self.update_dropdown_menu()

        self.manage_boxes = tk.Button(self.control_frame, text="Manage Boxes",
                                      command=self.manage_boxes_method, bg="white", width=18)
        self.manage_boxes.pack(side=tk.TOP, padx=5, pady=5)
        # Add Spider
        self.spider_box = tk.Button(self.control_frame, text="Add Spider",
                                    command=self.custom_canvas.add_spider, bg="white", width=18)
        self.spider_box.pack(side=tk.TOP, padx=5, pady=5)

        self.rename = tk.Button(self.control_frame, text="Rename Diagram",
                                command=self.rename, bg="white", width=18)
        self.rename.pack(side=tk.TOP, padx=5, pady=5)

        self.random = tk.Button(self.control_frame, text="Connect At Random",
                                command=self.custom_canvas.random, bg="white", width=18)
        self.random.pack(side=tk.TOP, padx=5, pady=5)

        self.alg_not = tk.Button(self.control_frame, text="Get Algebraic Notation",
                                 command=self.create_algebraic_notation, bg="white", width=18)
        self.alg_not.pack(side=tk.TOP, padx=5, pady=5)

        self.alg_not = tk.Button(self.control_frame, text="Visualize as graph",
                                 command=self.visualize_as_graph, bg="light sea green", width=18)
        self.alg_not.pack(side=tk.TOP, padx=5, pady=5)

        # Button for Draw Wire Mode
        self.draw_wire_button = tk.Button(self.control_frame, text="Draw Wire Mode",
                                          command=self.custom_canvas.toggle_draw_wire_mode, bg="white", width=18)
        self.draw_wire_button.pack(side=tk.TOP, padx=5, pady=25)

        # Bottom buttons
        buttons = {
            "Save project": self.save_to_file,
            "Save png": self.custom_canvas.save_as_png,
            "Export hypergraph": self.custom_canvas.export_hypergraph,
            "Remove input": self.custom_canvas.remove_diagram_input,
            "Remove output": self.custom_canvas.remove_diagram_output,
            "Add input": self.custom_canvas.add_diagram_input,
            "Add output": self.custom_canvas.add_diagram_output,
        }
        self.saved_buttons = {}
        for name, method in buttons.items():
            button = tk.Button(self.control_frame, text=name, command=method, bg="white", width=18)
            button.pack(side=tk.BOTTOM, padx=5, pady=5)
            self.saved_buttons[name] = button

        if load:
            self.load_from_file()
        self.mainloop()

    def create_algebraic_notation(self):
        if not is_canvas_complete(self.custom_canvas):
            text = "Diagram is incomplete!"
            text_window = tk.Toplevel(self)
            text_window.title("Algebraic Notation")

            text_box = tk.Text(text_window, wrap='word', width=40,
                               height=10)
            text_box.pack(padx=10, pady=10)

            text_box.insert(tk.END, text)

            text_box.config(state=tk.DISABLED)

        else:
            texts = get_notations(self.custom_canvas)

            text_window = tk.Toplevel(self)
            text_window.title("Algebraic Notation")
            notebook = ttk.Notebook(text_window)
            notebook.pack(fill='both', expand=True)

            for name, text in texts.items():
                frame = ttk.Frame(notebook)
                notebook.add(frame, text=name)

                text_box = tk.Text(frame, wrap='word', font=('Times New Roman', 15))
                text_box.pack(padx=10, pady=10, fill='both', expand=True)
                text_box.insert(tk.END, text)
                text_box.config(state=tk.DISABLED)
                # Create a button to copy text to clipboard
                copy_button = tk.Button(frame, text="Copy", command=lambda tb=text_box: self.copy_to_clipboard(tb))
                copy_button.pack(pady=5)

    def visualize_as_graph(self):
        plot_window = tk.Toplevel(self)
        plot_window.title("Graph Visualization")

        hypergraph_notation = HypergraphNotation(self.custom_canvas.receiver.diagram)

        figure = hypergraph_notation.get_hypergraph_figure()

        # Embed the figure in the Tkinter window
        canvas = FigureCanvasTkAgg(figure, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def copy_to_clipboard(self, text_box):
        self.clipboard_clear()  # Clear the clipboard
        text = text_box.get("1.0", tk.END)  # Get the content of the text box
        self.clipboard_append(text)  # Append the text to the clipboard
        self.update()  # Now it stays on the clipboard even after the window is closed

    def open_children(self, parent):
        self.tree.item(parent, open=True)  # open parent
        for child in self.tree.get_children(parent):
            self.open_children(child)  # recursively open children

    def bind_buttons(self):
        self.undefined_box_button.configure(command=self.custom_canvas.add_box)
        self.manage_boxes.configure(command=self.manage_boxes_method)
        self.spider_box.configure(command=self.custom_canvas.add_spider)

        self.draw_wire_button.configure(command=self.custom_canvas.toggle_draw_wire_mode)

        self.random.configure(command=self.custom_canvas.random)
        # TODO figure out why this is needed! and change it!
        if not self.custom_canvas.diagram_source_box:
            buttons = {
                "Save project": self.save_to_file,
                "Save png": self.custom_canvas.save_as_png,
                "Export hypergraph": self.custom_canvas.export_hypergraph,
                "Remove input": self.custom_canvas.remove_diagram_input,
                "Remove output": self.custom_canvas.remove_diagram_output,
                "Add input": self.custom_canvas.add_diagram_input,
                "Add output": self.custom_canvas.add_diagram_output
            }
        else:
            buttons = {
                "Save project": self.save_to_file,
                "Save png": self.custom_canvas.save_as_png,
                "Export hypergraph": self.custom_canvas.export_hypergraph,
                "Remove input": self.remove_diagram_input,
                "Remove output": self.remove_diagram_output,
                "Add input": self.add_diagram_input,
                "Add output": self.add_diagram_output
            }
        for name, button in self.saved_buttons.items():
            button.configure(command=buttons[name])

    def add_canvas(self, canvas):
        # Add some items to the tree

        self.tree.insert(str(canvas.parent_diagram.id), "end", str(canvas.id), text=canvas.name_text)
        self.canvasses[str(canvas.id)] = canvas
        for box in canvas.boxes:
            if box.sub_diagram:
                self.tree.move(str(box.sub_diagram.id), str(canvas.id), "end")

        # Expand all items in the tree
        self.open_children(self.tree_root_id)

    def change_canvas_name(self, canvas):
        self.tree.item(str(canvas.id), text=canvas.name_text)

    def rename(self):
        # TODO SET limit on how long name can be, same for boxes
        if self.custom_canvas.diagram_source_box:
            txt = "Enter label for sub-diagram:"
        else:
            txt = "Enter label for root diagram:"
        new_name = simpledialog.askstring("Input", txt, initialvalue=self.custom_canvas.name_text)

        if new_name:
            self.custom_canvas.set_name(new_name)
            self.change_canvas_name(self.custom_canvas)
            if self.custom_canvas.diagram_source_box:
                self.custom_canvas.diagram_source_box.set_label(new_name)

    def switch_canvas(self, canvas):
        self.custom_canvas.pack_forget()
        self.custom_canvas = canvas
        # Show the selected canvas
        self.custom_canvas.pack(fill='both', expand=True)
        self.bind_buttons()

        self.tree.selection_remove(self.tree.selection())

        self.tree.selection_set(str(canvas.id))
        self.tree.see(str(canvas.id))

    def del_from_canvasses(self, canvas):
        self.tree.delete(str(canvas.id))

    def on_tree_select(self, _):
        # Get the selected item
        selected_item = self.tree.focus()  # Get the ID of the selected item
        if selected_item:
            new_canvas = self.canvasses[selected_item]
            self.switch_canvas(new_canvas)

    def add_diagram_input(self, id_=None):
        box_c = None
        if self.custom_canvas.diagram_source_box:
            box_c = self.custom_canvas.diagram_source_box.add_left_connection()
        canvas_i = self.custom_canvas.add_diagram_input(id_=id_)
        return box_c, canvas_i

    def add_diagram_output(self, id_=None):
        box_c = None
        if self.custom_canvas.diagram_source_box:
            box_c = self.custom_canvas.diagram_source_box.add_right_connection()
        canvas_o = self.custom_canvas.add_diagram_output(id_=id_)
        return box_c, canvas_o

    def remove_diagram_input(self):
        if self.custom_canvas.diagram_source_box:
            c = self.find_connection_to_remove("left")
            if c:
                self.custom_canvas.diagram_source_box.remove_connection(c)
            self.custom_canvas.remove_diagram_input()
            if self.receiver.listener:
                self.receiver.receiver_callback("remove_inner_left",
                                                generator_id=self.custom_canvas.diagram_source_box.id)
        else:
            self.custom_canvas.remove_diagram_input()

    def remove_diagram_output(self):
        if self.custom_canvas.diagram_source_box:

            c = self.find_connection_to_remove("right")
            if c:
                self.custom_canvas.diagram_source_box.remove_connection(c)
            self.custom_canvas.remove_diagram_output()
            if self.receiver.listener:
                self.receiver.receiver_callback("remove_inner_right",
                                                generator_id=self.custom_canvas.diagram_source_box.id)
        else:
            self.custom_canvas.remove_diagram_input()

    def find_connection_to_remove(self, side):
        c_max = 0
        c = None
        for connection in self.custom_canvas.diagram_source_box.connections:
            if connection.side == side and connection.index >= c_max:
                c_max = connection.index
                c = connection
        return c

    def manage_boxes_method(self):
        list_window = tk.Toplevel(self)
        list_window.title("List of Elements")

        def remove_selected_item():
            selected_item_index = listbox.curselection()
            if selected_item_index:
                name = listbox.get(selected_item_index)
                self.remove_option(name)
                listbox.delete(selected_item_index)

        listbox = tk.Listbox(list_window, selectmode=tk.SINGLE)
        listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        [listbox.insert(tk.END, item) for item in self.boxes]

        button_frame = tk.Frame(list_window)
        button_frame.pack(pady=10)

        remove_button = tk.Button(button_frame, text="Remove Item", command=remove_selected_item)
        remove_button.pack(side=tk.LEFT, padx=5)

    def update_dropdown_menu(self):
        self.boxes = {}

        self.get_boxes_from_file()
        # Clear existing menu items

        # add undefined box button as well to make width greater
        self.dropdown_menu.delete(0, tk.END)
        self.dropdown_menu.add_command(label="Add Undefined Box",
                                       command=self.custom_canvas.add_box)
        self.dropdown_menu.add_separator()

        # Add options to the dropdown menu
        for i, name in enumerate(self.boxes):
            self.dropdown_menu.add_command(label=name, command=lambda n=name: self.boxes[n](n, self.custom_canvas))

    def remove_option(self, option):
        self.project_exporter.del_box_menu_option(option)
        self.update_dropdown_menu()

    def get_boxes_from_file(self):
        d = self.importer.load_boxes_to_menu()
        for k in d:
            self.boxes[k] = self.add_custom_box

    def add_custom_box(self, name, canvas):
        self.importer.add_box_from_menu(canvas, name)

    def save_box_to_diagram_menu(self, box):
        self.project_exporter.export_box_to_menu(box)
        self.update_dropdown_menu()

    def set_title(self, filename):
        self.title(filename.replace(".json", ""))

    def do_i_exit(self):
        if messagebox.askokcancel("Exit", "Do you really want to exit?"):
            self.destroy()

    def save_to_file(self):
        filename = self.project_exporter.export()
        self.set_title(filename)

    def load_from_file(self):
        filename = self.importer.import_diagram()
        if filename:
            self.set_title(filename.replace(".json", ""))
