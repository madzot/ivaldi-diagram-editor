import os
import tkinter as tk
import re
import json
import chlorophyll
from chlorophyll import CodeView
import pygments.lexers


class CodeEditor:
    def __init__(self, box):
        self.box = box
        self.window = tk.Toplevel()
        self.window.title('Code Editor')
        self.window.geometry("1000x750")
        self.code_view = CodeView(self.window, lexer=pygments.lexers.PythonLexer, tab_width=4)
        self.code_view.pack(fill=tk.BOTH, expand=True)
        self.previous_text = ""

        self.save_button = tk.Button(
            self.code_view,
            text="Save",
            command=self.save,
        )
        self.save_button.pack(
            anchor=tk.E
        )

        param_list = []
        return_list = []
        input_count = 0
        output_count = 0
        for i in self.box.connections:
            if i.side == "left":
                param_list.append(f"x{input_count}")
                input_count += 1
            else:
                return_list.append(f"y{output_count}")
                output_count += 1
        param_str = tuple(param_list).__str__().replace("'", "")
        return_str = tuple(return_list).__str__().replace("'", "")
        if len(param_list) == 1:
            param_str = param_str.replace(",", "")
        if len(return_list) == 1:
            return_str = return_str.replace(",", "")
        text = f"def {self.box.label_text}{param_str}:\n    return {return_str}"
        if self.box.label_text in self.box.canvas.master.label_content.keys():
            text = self.box.canvas.master.label_content[self.box.label_text].strip()

        self.code_view.insert('1.0', text)

    def save(self):
        if os.stat("conf/functions_conf.json").st_size != 0:
            with open("conf/functions_conf.json", "r+") as file:
                existing_json = json.load(file)
                existing_json[self.box.label_text] = self.code_view.get('1.0', tk.END).strip()
                json_object = json.dumps(existing_json, indent=4)
                file.seek(0)
                file.truncate(0)
                file.write(json_object)
        else:
            with open("conf/functions_conf.json", "w") as file:
                json_object = json.dumps(
                    {f"{self.box.label_text}": self.code_view.get('1.0', tk.END).strip()},
                    indent=4
                )
                file.write(json_object)
        for box in self.box.canvas.boxes:
            if box.label_text in self.box.label_text:
                box.update_io()
        self.box.canvas.master.label_content[self.box.label_text] = self.code_view.get("1.0", tk.END)
        self.window.destroy()
