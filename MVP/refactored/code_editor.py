import os
import tkinter as tk
import re
import json


class CodeEditor:
    def __init__(self, box):
        self.box = box
        self.window = tk.Toplevel()
        self.window.title('Code Editor')
        self.window.geometry("1000x750")
        self.previous_text = ""

        normal = self.rgb((234, 234, 234))
        keywords = self.rgb((234, 95, 95))
        comments = self.rgb((95, 234, 165))
        string = self.rgb((234, 162, 95))
        background = self.rgb((42, 42, 42))
        font = 'Consolas 15'

        self.repl = [
            [
                '(^| )(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)($| )',
                keywords],
            ['".*?"', string],
            ['\'.*?\'', string],
            ['#.*?$', comments],
        ]

        self.edit_area = tk.Text(
            self.window,
            background=background,
            foreground=normal,
            insertbackground=normal,
            relief=tk.FLAT,
            borderwidth=30,
            font=font
        )

        self.edit_area.pack(
            fill=tk.BOTH,
            expand=1
        )

        self.save_button = tk.Button(
            self.window,
            text="Save",
            command=self.save,
            background=background,
            foreground=normal,
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
            text = self.box.canvas.master.label_content[self.box.label_text]

        self.edit_area.insert('1.0', text)

        self.edit_area.bind('<KeyRelease>', self.changes)

        self.changes()

    def changes(self, event=None):

        if self.edit_area.get('1.0', tk.END) == self.previous_text:
            return

        for tag in self.edit_area.tag_names():
            self.edit_area.tag_remove(tag, "1.0", "end")

        i = 0
        for pattern, color in self.repl:
            for start, end in self.search_re(pattern, self.edit_area.get('1.0', tk.END)):
                self.edit_area.tag_add(f'{i}', start, end)
                self.edit_area.tag_config(f'{i}', foreground=color)

                i += 1

        self.previous_text = self.edit_area.get('1.0', tk.END)

    def save(self):
        if os.stat("conf/functions_conf.json").st_size != 0:
            with open("conf/functions_conf.json", "r+") as file:
                existing_json = json.load(file)
                existing_json[self.box.label_text] = self.edit_area.get('1.0', tk.END)
                json_object = json.dumps(existing_json, indent=4)
                file.write(json_object)
        else:
            with open("conf/functions_conf.json", "w") as file:
                json_object = json.dumps({f"{self.box.label_text}": self.edit_area.get('1.0', tk.END)}, indent=4)
                file.write(json_object)
        self.box.canvas.master.label_content[self.box.label_text] = self.edit_area.get("1.0", tk.END)
        self.window.destroy()

    @staticmethod
    def search_re(pattern, text):
        matches = []

        text = text.splitlines()
        for i, line in enumerate(text):
            for match in re.finditer(pattern, line):
                matches.append(
                    (f"{i + 1}.{match.start()}", f"{i + 1}.{match.end()}")
                )

        return matches

    @staticmethod
    def rgb(rgb):
        return "#%02x%02x%02x" % rgb
