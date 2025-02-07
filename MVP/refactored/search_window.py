import tkinter as tk
import ttkbootstrap as tkk

from MVP.refactored.custom_canvas import CustomCanvas
from MVP.refactored.search_algorithm import SearchAlgorithm


class SearchWindow(tk.Toplevel):
    def __init__(self, main_diagram):
        super().__init__()
        self.main_diagram = main_diagram

        self.resizable(False, False)
        self.title("Search in Project")

        self.options_frame = tkk.Frame(self)
        self.options_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.options_frame.rowconfigure(0, weight=1)
        self.options_frame.rowconfigure(1, weight=1)
        self.options_frame.columnconfigure(0, weight=1)
        self.options_frame.columnconfigure(1, weight=1)

        self.settings_label = tk.Label(self.options_frame, text="Settings", font=("Arial", 14, "bold"))
        self.settings_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=(30, 0), pady=10)

        self.search_all_canvases = tk.IntVar()
        self.search_all_canvases.set(1)
        self.search_all_option_button = tkk.Checkbutton(self.options_frame, text="Search all canvases",
                                                        variable=self.search_all_canvases)
        self.search_all_option_button.grid(row=1, column=0, sticky=tk.NSEW, padx=(50, 0))

        self.match_sub_diagrams = tk.IntVar()
        self.match_sub_diagrams.set(0)
        self.match_sub_canvases_button = tkk.Checkbutton(self.options_frame, text="Match labels",
                                                         variable=self.match_sub_diagrams)
        self.match_sub_canvases_button.grid(row=1, column=1, sticky=tk.NSEW, padx=(0, 0))

        self.canvas_label_frame = tk.Frame(self)
        self.canvas_label_frame.rowconfigure(0, weight=1)
        self.canvas_label_frame.columnconfigure(0, weight=1)
        self.canvas_label_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(20, 0))

        self.canvas_label = tk.Label(self.canvas_label_frame, text="Canvas", font=("Arial", 14, "bold"))
        self.canvas_label.grid(row=1, column=0, sticky=tk.W, padx=(30, 0))
        self.canvas_frame = tkk.Frame(self, bootstyle=tkk.PRIMARY)
        self.canvas_frame.pack(padx=2, pady=9)
        self.search_canvas = CustomCanvas(self.canvas_frame, None, self.main_diagram.receiver,
                                          self.main_diagram, self.main_diagram, False, search=True)
        self.search_canvas.set_name("")
        self.search_canvas.pack(padx=1, pady=1)

        self.result_frame = tkk.Frame(self)
        self.result_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.search_button = tkk.Button(self.result_frame, text="Search", command=self.search)
        self.search_button.pack(side=tk.RIGHT)

    def search(self):
        algorithm = SearchAlgorithm(self.search_canvas, self.main_diagram.custom_canvas, self)
        found = algorithm.contains_searchable()
        print(f"Found: {found}")
        self.main_diagram.is_search_active = found
        if found:
            for canvas in self.main_diagram.canvasses.values():
                canvas.toggle_displaying_results_button()

