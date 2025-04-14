import hashlib
import json
import random
import string
from tkinter import messagebox
from typing import List
from typing import TextIO

from MVP.refactored.frontend.components.custom_canvas import CustomCanvas
from MVP.refactored.util.importer.importer import Importer
from constants import *


class JsonImporter(Importer):

    def __init__(self, canvas: CustomCanvas):
        super().__init__(canvas)
        self.id_randomize = {}
        self.seed = ""
        self.random_id = False
        self.boxes_json_conf = "./MVP/refactored/conf/boxes_conf.json"

    def start_import(self, json_files: List[TextIO]) -> str:
        json_file = json_files[0]

        data = json.load(json_file)
        data = data["main_canvas"]

        self.load_everything_to_canvas(data)
        return os.path.basename(json_file.name)

    def load_everything_to_canvas(self, data: dict):
        self.load_boxes_to_canvas(data, self.canvas)
        self.load_spiders_to_canvas(data, self.canvas)
        self.load_io_to_canvas(data, self.canvas)
        self.load_wires_to_canvas(data, self.canvas)

    def load_boxes_to_canvas(self, d, canvas):
        for box in d["boxes"]:
            new_box = canvas.add_box((box["x"], box["y"]), box["size"], self.get_id(box["id"]), shape=box.get("shape"))
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

    def load_spiders_to_canvas(self, d, canvas):
        for s in d["spiders"]:
            canvas.add_spider((s["x"], s["y"]), self.get_id(s["id"]))

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

    @staticmethod
    def generate_random_string(length):
        # Define the possible characters for the random string
        characters = string.ascii_letters + string.digits + string.punctuation
        # Generate a random string using the specified characters
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

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

    def load_boxes_to_menu(self):
        try:
            with open(self.boxes_json_conf, 'r') as json_file:
                data = json.load(json_file)
                return data
        except FileNotFoundError or IOError or json.JSONDecodeError:
            messagebox.showinfo("Info", "Loading custom boxes failed!")
            return {}

    def add_box_from_menu(self, canvas, box_name, loc=(100, 100), return_box=False):
        with open(BOXES_CONF, 'r') as json_file:
            self.seed = self.generate_random_string(10)
            self.random_id = True
            data = json.load(json_file)
            box = data[box_name]
            new_box = canvas.add_box(loc, shape=box["shape"])
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
