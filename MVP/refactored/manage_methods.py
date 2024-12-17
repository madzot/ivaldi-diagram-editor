import json
from tkinter import simpledialog, messagebox

import ttkbootstrap as ttk
import tkinter as tk

from MVP.refactored.code_editor import CodeEditor


class ManageMethods(tk.Toplevel):
    def __init__(self, main_diagram, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_diagram = main_diagram
        self.aspect_ratio_x = 16
        self.aspect_ratio_y = 10

        self.window_size = 30

        self.minsize(400, 100)

        self.title('Manage Methods')

        self.table = ttk.Treeview(self, columns="Function", bootstyle=ttk.PRIMARY)
        self.table.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.table.bind("<Motion>", "break")

        self.table.column("#0", width=100, minwidth=100, anchor=tk.W)
        self.table.heading("#0", text="Label", anchor=tk.W)
        self.table.column("Function", width=400, minwidth=400, anchor=tk.W)
        self.table.heading('Function', text='Function', anchor=tk.W)

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.cancel_button = ttk.Button(self.button_frame, text="Cancel", command=self.destroy)
        self.cancel_button.pack(side=tk.RIGHT, fill=tk.X)

        self.add_new_button = ttk.Button(self.button_frame, text="Add new", command=self.add_new_function)
        self.add_new_button.pack(padx=5, side=tk.RIGHT, fill=tk.X)

        self.edit_button = ttk.Button(self.button_frame, text="Edit code", command=self.open_code_editor)
        self.edit_button.pack(padx=5, side=tk.LEFT, fill=tk.X)

        self.edit_label_button = ttk.Button(self.button_frame, text="Edit label", command=self.open_label_editor)
        self.edit_label_button.pack(padx=5, side=tk.LEFT, fill=tk.X)

        self.delete_button = ttk.Button(self.button_frame, text="Delete", command=self.delete_method, bootstyle=ttk.DANGER)
        self.delete_button.pack(padx=5, side=tk.LEFT, fill=tk.X)

        self.main_diagram.load_functions()

        self.add_methods()

    def add_new_function(self):
        label = simpledialog.askstring("Add label", "Please enter new label").strip()
        if not label or label in self.main_diagram.label_content.keys():
            messagebox.showerror(title="Error", message="Label is empty or already exists")
            self.add_new_function()
            return
        CodeEditor(self.main_diagram, label=label, code="")

    def add_methods(self):
        self.table.delete(*self.table.get_children())
        for label, method in self.main_diagram.label_content.items():
            self.table.insert('', tk.END, text=label, values=(method.replace('\n', ''),))
            # The tuple with a comma in values is necessary to prevent tkinter splitting string.

    def delete_method(self):
        label = self.table.item(self.table.focus())["text"]
        item = self.table.selection()[0]
        del self.main_diagram.label_content[label]
        self.table.delete(item)
        self.write_to_json(self.main_diagram.label_content)
        for canvas in self.main_diagram.canvasses.values():
            for box in canvas.boxes:
                if box.label_text == label:
                    box.edit_label(new_label="")

    def open_code_editor(self):
        label = self.table.item(self.table.focus())["text"]
        code = self.main_diagram.label_content[label]
        CodeEditor(self.main_diagram, label=label, code=code)

    def open_label_editor(self):
        label = self.table.item(self.table.focus())["text"]
        if label:
            new_label = simpledialog.askstring("Input", "Enter new label", initialvalue=label)
            if new_label:
                self.main_diagram.change_function_label(label, new_label)
                self.add_methods()
                self.write_to_json(self.main_diagram.label_content)

    @staticmethod
    def write_to_json(content):
        with open("conf/functions_conf.json", "r+") as file:
            json_object = json.dumps(content, indent=4)
            file.seek(0)
            file.truncate(0)
            file.write(json_object)

