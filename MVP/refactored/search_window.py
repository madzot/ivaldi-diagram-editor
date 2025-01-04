import tkinter as tk
import ttkbootstrap as tkk

from MVP.refactored.custom_canvas import CustomCanvas


class SearchWindow(tk.Toplevel):
    def __init__(self, main_diagram):
        super().__init__()
        self.main_diagram = main_diagram

        self.minsize(400, 100)
        self.title("Search")

        self.options_frame = tkk.Frame(self, bootstyle=tkk.LIGHT)
        self.options_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.search_all_canvases = tk.IntVar()
        self.search_all_canvases.set(1)
        self.search_all_option_button = tkk.Checkbutton(self.options_frame, text="Search all canvases",
                                                        variable=self.search_all_canvases)
        self.search_all_option_button.pack()

        self.search_canvas = CustomCanvas(self, None, self.main_diagram.receiver,
                                          self.main_diagram, self.main_diagram, False, search=True)
        self.search_canvas.set_name("")
        self.search_canvas.pack()

        self.result_frame = tkk.Frame(self, bootstyle=tkk.LIGHT)
        self.result_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.search_button = tkk.Button(self.result_frame, text="Search")
        self.search_button.pack(side=tk.LEFT)
