import tkinter as tk

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class SearchResultButton(tk.LabelFrame):
    def __init__(self, master, main_diagram, custom_canvas, **kwargs):
        super().__init__(master, **kwargs)
        self.main_diagram = main_diagram
        self.custom_canvas = custom_canvas
        cancel_button = ttk.Button(self, text="X", bootstyle=(SECONDARY, OUTLINE),
                                   command=self.custom_canvas.on_displaying_results_click)
        cancel_button.pack(side=tk.RIGHT)

        up_down_frame = ttk.LabelFrame(self, bootstyle=SECONDARY)

        up_button = tk.Label(up_down_frame, text="^")
        up_button.bind("<Button-1>", lambda event: self.main_diagram.move_between_search_results(up=True))
        up_button.pack(side=tk.LEFT, anchor=tk.CENTER)
        up_down_frame.pack(side=tk.LEFT)






