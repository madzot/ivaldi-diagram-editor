import hashlib
import json
import random
import string
from tkinter import filedialog
from tkinter import messagebox
from constants import *


from MVP.refactored.frontend.components.custom_canvas import CustomCanvas


class Importer:
    def __init__(self, canvas):
        self.canvas: CustomCanvas = canvas
        self.id_randomize = {}
        self.seed = ""
        self.random_id = False

    def get_id(self, id_):
        if not self.random_id:
            return id_
        if id_ in self.id_randomize:
            return self.id_randomize[id_]
        else:
            input_string = str(id_) + self.seed
            hash_object = hashlib.sha256()
            hash_object.update(input_string.encode('utf-8'))
            hex_dig = hash_object.hexdigest()
            self.id_randomize[id_] = hex_dig
            return hex_dig

    def start_import(self, d):
        d = d["main_canvas"]
        self.load_everything_to_canvas(d, self.canvas)

    def load_everything_to_canvas(self, d, canvas):
        multi_x, multi_y = self.find_multiplier(d)
        self.load_boxes_to_canvas(d, canvas, multi_x, multi_y)
        self.load_spiders_to_canvas(d, canvas, multi_x, multi_y)
        self.load_io_to_canvas(d, canvas)
        self.load_wires_to_canvas(d, canvas)

    def load_boxes_to_canvas(self, d, canvas, multi_x, multi_y):
        for box in d["boxes"]:
            new_box = canvas.add_box((box["x"] * multi_x, box["y"] * multi_y), (box["size"][0] * multi_x,
                                                                                box["size"][1] * multi_y),
                                     self.get_id(box["id"]), shape=box.get("shape", "rectangle"))
            if box["label"]:
                new_box.set_label(box["label"])
            for c in box["connections"]:
                if c["side"] == "left":
                    new_box.add_left_connection(self.get_id(c["id"]))
                if c["side"] == "right":
                    new_box.add_right_connection(self.get_id(c["id"]))

            if box["sub_diagram"]:
                sub_diagram: CustomCanvas = new_box.edit_sub_diagram(save_to_canvasses=False, add_boxes=False)
                self.load_everything_to_canvas(box["sub_diagram"], sub_diagram)
                if box["label"]:
                    name = box["label"]
                else:
                    name = str(sub_diagram.id)
                sub_diagram.set_name(name)
                canvas.main_diagram.add_canvas(sub_diagram)
                canvas.itemconfig(new_box.rect, fill="#dfecf2")

            new_box.lock_box()

    def import_diagram(self):
        file_path = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if file_path:
            try:
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)
                    self.start_import(data)
                    messagebox.showinfo("Info", "Imported successfully")
                    return file_path

            except FileNotFoundError or IOError or json.JSONDecodeError:
                messagebox.showerror("Error", "File import failed, loading new empty canvas.")
        else:
            return False

    def load_spiders_to_canvas(self, d, canvas, multi_x, multi_y):
        for s in d["spiders"]:
            canvas.add_spider((s["x"] * multi_x, s["y"] * multi_y), self.get_id(s["id"]))

    def load_io_to_canvas(self, d, canvas):
        d = d["io"]
        for i in d["inputs"]:
            canvas.add_diagram_input(self.get_id(i["id"]))
        for o in d["outputs"]:
            canvas.add_diagram_output(self.get_id(o["id"]))

    def load_wires_to_canvas(self, d, canvas):
        for w in d["wires"]:
            start_c_id = self.get_id(w["start_c"]["id"])
            end_c_id = self.get_id(w["end_c"]["id"])
            for con in [c for box in canvas.boxes for c in
                        box.connections] + canvas.inputs + canvas.outputs + canvas.spiders:

                if con.id == start_c_id:
                    canvas.start_wire_from_connection(con)
                    break

            for con in [c for box in canvas.boxes for c in
                        box.connections] + canvas.inputs + canvas.outputs + canvas.spiders:
                if con.id == end_c_id:
                    canvas.end_wire_to_connection(
                        con, True)
                    break

    def load_boxes_to_menu(self):
        try:
            with open(BOXES_CONF, 'r') as json_file:
                data = json.load(json_file)
                return data
        except FileNotFoundError or IOError or json.JSONDecodeError:
            messagebox.showinfo("Info", "Loading custom boxes failed!")
            return {}

    @staticmethod
    def generate_random_string(length):
        # Define the possible characters for the random string
        characters = string.ascii_letters + string.digits + string.punctuation
        # Generate a random string using the specified characters
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

    def add_box_from_menu(self, canvas, box_name, loc=(100, 100), return_box=False):
        with open(BOXES_CONF, 'r') as json_file:
            self.seed = self.generate_random_string(10)
            self.random_id = True
            data = json.load(json_file)
            box = data[box_name]
            new_box = canvas.add_box(loc, shape=box.get("shape", "rectangle"))
            if box["label"]:
                new_box.set_label(box["label"])
            for _ in range(box["left_c"]):
                new_box.add_left_connection()
            for _ in range(box["right_c"]):
                new_box.add_right_connection()

            if box["sub_diagram"]:
                sub_diagram: CustomCanvas = new_box.edit_sub_diagram(save_to_canvasses=False, add_boxes=False)

                self.load_everything_to_canvas(box["sub_diagram"], sub_diagram)
                if box["label"]:
                    name = box["label"]
                else:
                    name = str(sub_diagram.id)
                sub_diagram.set_name(name)
                canvas.main_diagram.add_canvas(sub_diagram)
                canvas.itemconfig(new_box.rect, fill="#dfecf2")
            new_box.lock_box()
            self.random_id = False
            self.id_randomize = {}
            if return_box:
                return new_box

    def find_multiplier(self, d):
        max_x = 0
        min_x = float('inf')
        max_y = 0
        for box in d["boxes"]:
            if box["x"] + box["size"][0] > max_x:
                max_x = box["x"] + box["size"][0]
            if box["x"] < min_x:
                min_x = box["x"]
            if box["y"] + box["size"][1] > max_y:
                max_y = box["y"] + box["size"][1]
        for spider in d["spiders"]:
            if spider["x"] + 10 > max_x:
                max_x = spider["x"] + 10
            if spider["y"] + 10 > max_y:
                max_y = spider["y"] + 10

        multi_x = 1
        multi_y = 1

        if self.canvas.main_diagram.custom_canvas.winfo_width() < max_x:
            max_x += min_x
            multi_x = round(self.canvas.main_diagram.custom_canvas.winfo_width() / max_x, 3)
        if self.canvas.main_diagram.custom_canvas.winfo_height() < max_y:
            max_y += 30
            multi_y = round(self.canvas.main_diagram.custom_canvas.winfo_height() / max_y, 3)
        return multi_x, multi_y
