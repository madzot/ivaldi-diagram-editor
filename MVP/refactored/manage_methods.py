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

        self.listbox = tk.Listbox(self, selectmode=tk.SINGLE, width=100, height=16)
        self.listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.cancel_button = ttk.Button(self.button_frame, text="Cancel", command=lambda: self.destroy())
        self.cancel_button.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.edit_button = ttk.Button(self.button_frame, text="Edit", command=self.open_code_editor)
        self.edit_button.pack(padx=5, side=tk.RIGHT, fill=tk.BOTH)

        self.main_diagram.load_functions()

        self.add_methods()

    def add_methods(self):
        for label, method in self.main_diagram.label_content.items():
            self.listbox.insert(tk.END, f"{label}: {method}")

    def open_code_editor(self):
        pass

