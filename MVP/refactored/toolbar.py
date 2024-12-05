import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttk


class Titlebar(ttk.Frame):
    def __init__(self, main_diagram, custom_canvas):
        super().__init__(main_diagram)
        self.main_diagram = main_diagram
        self.custom_canvas = custom_canvas
        self.config(bootstyle=ttk.LIGHT)

        self.file_button = tk.Menubutton(self, text="File",
                                         width=5, indicatoron=False)
        self.file_menu = ttk.Menu(self.file_button, tearoff=False)
        self.file_button.config(menu=self.file_menu)

        self.save_submenu = tk.Menu(self.file_menu, tearoff=False)
        self.save_submenu.add_command(label="png file", command=lambda: self.custom_canvas.save_as_png())
        self.save_submenu.add_command(label="project", command=lambda: self.main_diagram.save_to_file())
        self.save_submenu.add_command(label="hypergraph", command=lambda: self.custom_canvas.export_hypergraph())

        self.generate_submenu = tk.Menu(self.file_menu, tearoff=False)
        self.generate_submenu.add_command(label="TikZ", command=lambda: self.custom_canvas.open_tikz_generator())
        self.generate_submenu.add_command(label="code", command=lambda: self.main_diagram.generate_code())

        self.file_menu.add_cascade(menu=self.save_submenu, label="Save as")
        self.file_menu.add_cascade(menu=self.generate_submenu, label="Generate")
        self.file_button.pack(side=ttk.LEFT)

        self.file_menu.add_command(label="New", command=self.handle_new_graph)

        self.view_button = tk.Menubutton(self, text="View",
                                         width=5, indicatoron=False)
        self.view_menu = tk.Menu(self.view_button, tearoff=False)
        self.view_button.config(menu=self.view_menu)

        self.view_menu.add_command(label="Visualize hypergraph",
                                   command=lambda: self.main_diagram.visualize_as_graph(self.custom_canvas))
        self.view_button.pack(side=ttk.LEFT)

    def set_custom_canvas(self, custom_canvas):
        self.custom_canvas = custom_canvas

    def handle_new_graph(self):
        root_canvas = list(self.main_diagram.canvasses.items())[0][1]
        if root_canvas.boxes or root_canvas.spiders or root_canvas.wires or root_canvas.outputs or root_canvas.inputs:
            dialog = messagebox.askyesnocancel(title="Warning",
                                               message="All unsaved progress will be deleted. Do you wish to save?")
            if dialog == tk.NO:
                pass
            elif dialog == tk.YES:
                self.main_diagram.save_to_file()
            else:
                return
            self.main_diagram.switch_canvas(root_canvas)
            root_canvas.delete_everything()


