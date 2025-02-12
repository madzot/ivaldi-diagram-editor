import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Toplevel, Frame, Label

from PIL import Image, ImageTk
from constants import *


class HelpWindow(Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Help")
        self.focus_set()
        self.resizable(False, False)
        self.geometry("400x450")
        self.bind("<FocusOut>", lambda event: self.destroy())

        self.keybind_frame = Frame(self)
        self.keybind_frame.pack(fill=tk.BOTH, expand=True)

        font = ("Arial", 11)

        key_binds = []
        descriptions = []

        self.sub_diagram_keybind = Label(self.keybind_frame, text="CTRL + N", font=font)

        self.sub_diagram_text = Label(self.keybind_frame, text="Create a sub-diagram from selected items",
                                      wraplength=200, justify=tk.CENTER, font=font)

        self.copy_keybind = Label(self.keybind_frame, text="CTRL + C", font=font)

        self.copy_text = Label(self.keybind_frame, text="Copy the selected items", wraplength=200, justify=tk.CENTER, font=font)

        self.paste_keybind = Label(self.keybind_frame, text="CTRL + V", font=font)

        self.paste_text = Label(self.keybind_frame, text="Paste the copied items", wraplength=200, justify=tk.CENTER, font=font)

        self.search_keybind = Label(self.keybind_frame, text="CTRL + F", font=font)

        self.search_text = Label(self.keybind_frame, text="Open search window", wraplength=200, justify=tk.CENTER, font=font)

        key_binds.append(self.sub_diagram_keybind)
        key_binds.append(self.copy_keybind)
        key_binds.append(self.paste_keybind)
        key_binds.append(self.search_keybind)

        descriptions.append(self.sub_diagram_text)
        descriptions.append(self.copy_text)
        descriptions.append(self.paste_text)
        descriptions.append(self.search_text)

        ttk.Separator(self.keybind_frame, orient=tk.VERTICAL).grid(column=0, row=0, rowspan=10, sticky="nse")
        ttk.Separator(self.keybind_frame, orient=tk.HORIZONTAL).grid(column=0, row=9, columnspan=2, sticky="ews")

        self.keybind_frame.columnconfigure(0, weight=1)
        self.keybind_frame.columnconfigure(1, weight=1)
        for i in range(10):
            self.keybind_frame.rowconfigure(i, weight=1)

        for i in range(len(key_binds)):
            keybind = key_binds[i]
            keybind.grid(column=0, row=i)

        for i in range(len(descriptions)):
            description = descriptions[i]
            description.grid(column=1, row=i)

        self.pagination_frame = Frame(self, pady=10)
        self.pagination_frame.pack(side=tk.BOTTOM, fill=tk.BOTH)

        # These pagination buttons are for the future when we need to have more than 1 page of help

        self.backward_logo = (Image.open(ASSETS_DIR + "/chevron-left-circle-outline.png"))
        self.backward_logo = self.backward_logo.resize((35, 35))
        self.backward_logo = ImageTk.PhotoImage(self.backward_logo)

        self.backward = Label(self.pagination_frame, image=self.backward_logo)

        self.forward_logo = (Image.open(ASSETS_DIR + "/chevron-right-circle-outline.png"))
        self.forward_logo = self.forward_logo.resize((35, 35))
        self.forward_logo = ImageTk.PhotoImage(self.forward_logo)

        self.forward = Label(self.pagination_frame, image=self.forward_logo)

        self.pagination_frame.columnconfigure(0, weight=1)
        self.pagination_frame.columnconfigure(1, weight=1)

        self.pagination_frame.rowconfigure(9, weight=1)

        self.backward.grid(column=0, row=0, sticky="e", padx=(0, 15))
        self.forward.grid(column=1, row=0, sticky="w", padx=(15, 0))






