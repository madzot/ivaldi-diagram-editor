import json
from tkinter import simpledialog

import ttkbootstrap as ttk
import tkinter as tk


class ManageMethods(tk.Toplevel):
    def __init__(self, main_diagram, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_diagram = main_diagram
        self.aspect_ratio_x = 16
        self.aspect_ratio_y = 10

        self.window_size = 30

        self.title('Manage Methods')

        self.treeview = ttk.Treeview(self, columns="Function", bootstyle=ttk.PRIMARY)
        self.treeview.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.treeview.column("#0", stretch=False, width=100, minwidth=100)
        self.treeview.heading("#0", text="Label")
        self.treeview.column("Function", stretch=False, width=400, minwidth=400)
        self.treeview.heading('Function', text='Function')

        # self.listbox = tk.Listbox(self, selectmode=tk.SINGLE, width=100, height=16)

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.cancel_button = ttk.Button(self.button_frame, text="Cancel", command=lambda: self.destroy())
        self.cancel_button.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.edit_button = ttk.Button(self.button_frame, text="Edit", command=self.open_code_editor)
        self.edit_button.pack(padx=5, side=tk.RIGHT, fill=tk.BOTH)

        self.edit_label_button = ttk.Button(self.button_frame, text="Edit label", command=self.open_label_editor)
        self.edit_label_button.pack(padx=5, side=tk.RIGHT, fill=tk.BOTH)

        self.main_diagram.load_functions()

        self.add_methods()

    def add_methods(self):
        self.treeview.delete(*self.treeview.get_children())
        for label, method in self.main_diagram.label_content.items():
            method = method.replace("\n", "")
            self.treeview.insert('', tk.END, 'functions', text=label, values=(method, ))
            # The tuple with a comma in values is necessary to prevent tkinter splitting string.

    def open_code_editor(self):
        pass

    def open_label_editor(self):
        label = self.treeview.item(self.treeview.focus())["text"]
        if label:
            new_label = simpledialog.askstring("Input", "Enter new label", initialvalue=label)
            if new_label:
                self.main_diagram.change_function_label(label, new_label)
                self.add_methods()
                with open("conf/functions_conf.json", "r+") as file:
                    json_object = json.dumps(self.main_diagram.label_content, indent=4)
                    file.seek(0)
                    file.truncate(0)
                    file.write(json_object)

