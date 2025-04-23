import tkinter as tk

from PIL import Image
from PIL.ImageTk import PhotoImage

import constants as const


class RotationButton(tk.LabelFrame):
    """
    A LabelFrame wrapper that is used as an indicator for showing the direction/rotation of the diagram.

    Clicking on it will change the direction/rotation of the diagram.
    """

    def __init__(self, master, custom_canvas, **kwargs):
        super().__init__(master, **kwargs)
        self.custom_canvas = custom_canvas

        self.config(height=60, width=60, text="Direction")

        self.arrow_base = Image.open(const.ASSETS_DIR + "/arrow-right-thin.png").resize((60, 50))
        self.arrow_image = PhotoImage(self.arrow_base)

        self.bind("<Button-1>", lambda event: self.rotate_arrow())

        self.button = None
        self.update()

    def update(self):
        self.place_forget()
        gap_size = 5
        self.place(x=self.custom_canvas.winfo_width() - self.winfo_width() - gap_size,
                   y=self.custom_canvas.winfo_height() - self.winfo_height() - gap_size)
        self.update_arrow()

    def update_arrow(self):
        # rotating arrow based on direction variable here
        arrow = self.arrow_base
        arrow = PhotoImage(arrow.rotate(self.custom_canvas.rotation))

        if self.button:
            self.button.pack_forget()
        self.button = tk.Label(self, image=arrow)
        self.button.image = self.arrow_image
        self.button.bind("<Button-1>", lambda event: self.rotate_arrow())
        self.button.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)

    def rotate_arrow(self):
        #  This should be deleted when #132 merged and changing rotation should be done in update_arrow
        #  It is currently just for testing rotating the arrow inside the button
        self.arrow_base = self.arrow_base.rotate(-90)
        self.arrow_image = PhotoImage(self.arrow_base)
        self.update_arrow()
