import ast
import os
from typing import List
from typing import TextIO

from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.util.importer.importer import Importer


class PythonImporter(Importer):

    def start_import(self, python_files: List[TextIO]) -> str:
        all_functions = {}
        all_imports = []
        main_logic = None
        main_diagram_name = None

        for python_file in python_files:
            file_functions, file_imports, file_main_logic = self._extract_data_from_file(python_file)

            all_functions.update(file_functions)
            all_imports.extend(file_imports)

            if file_main_logic:
                if main_logic is None:
                    main_logic = file_main_logic
                    main_diagram_name = os.path.basename(python_file.name)
                else:
                    raise ValueError("Multiple main execution blocks found in the imported files!\n"
                                     "Only one file should contain 'if __name__ == \"__main__\":'.")

        if not main_logic:
            raise ValueError("The Python code in imported files does not contain a main execution block!\n"
                             "One of the selected files must include 'if __name__ == \"__main__\":'.")

        first_function = next(iter(all_functions.values()))
        first_function.imports = all_imports

        self.load_everything_to_canvas({"functions": all_functions, "main_logic": main_logic})
        return main_diagram_name

    def load_everything_to_canvas(self, data: dict) -> None:
        elements_y_position = 300
        # TODO: refactor this to appropriate condition
        functions = data["functions"]
        main_logic = data["main_logic"]

        possible_outputs = {}
        boxes_gap = 900 / (len(main_logic) - 1)
        box_x = 100

        box_right_connection_spiders = {}

        for function_call in main_logic:
            function_name = function_call["function_name"]
            args = function_call["args"]

            for assigned_variable in function_call["assigned_variables"]:
                possible_outputs[assigned_variable] = function_name

            new_box = self.canvas.add_box(loc=(box_x, elements_y_position))
            new_box.set_label(function_call["function_name"])

            box_function = functions[function_name]
            new_box.set_box_function(box_function)

            for arg in args:
                left_connection = new_box.add_left_connection()
                self.canvas.start_wire_from_connection(left_connection)

                wire_end = None
                for possible_right_connection_function in main_logic:
                    for assigned_variable in possible_right_connection_function["assigned_variables"]:
                        if assigned_variable == arg:
                            wire_end = possible_right_connection_function["function_name"]
                            if assigned_variable in possible_outputs.keys():
                                possible_outputs.pop(assigned_variable)
                            break

                if wire_end:
                    for box in self.canvas.boxes:
                        if box.label_text == wire_end:

                            new_spider_added = False
                            if arg not in box_right_connection_spiders.keys():
                                spider_x_position = box.x + boxes_gap / 2
                                new_spider = self.canvas.add_spider(loc=(spider_x_position, elements_y_position))
                                box_right_connection_spiders[arg] = new_spider

                                new_spider_added = True

                            connection_spider = box_right_connection_spiders[arg]

                            self.canvas.end_wire_to_connection(connection_spider, True)

                            if new_spider_added:
                                wire_end_connection = box.add_right_connection()
                                self.canvas.start_wire_from_connection(connection_spider)
                                self.canvas.end_wire_to_connection(wire_end_connection, True)

                            break
                else:
                    diagram_input = self.canvas.add_diagram_input()
                    self.canvas.end_wire_to_connection(diagram_input, True)

            new_box.lock_box()
            box_x += boxes_gap

        for diagram_output_variable, box_label in possible_outputs.items():
            for box in self.canvas.boxes:
                if box.label_text == box_label:
                    wire_start_connection = box.add_right_connection()
                    self.canvas.start_wire_from_connection(wire_start_connection)
                    break

            output = self.canvas.add_diagram_output()
            self.canvas.end_wire_to_connection(output, True)

    def _extract_data_from_file(self, python_file: TextIO) -> tuple:
        functions = {}
        imports = []
        main_logic = None

        source_code = python_file.read()
        tree = ast.parse(source_code)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._extract_function(node, source_code, functions)

        for node in tree.body:
            if isinstance(node, ast.Import):
                self._extract_imports(node, imports)

            elif isinstance(node, ast.ImportFrom):
                self._extract_imports_from(node, imports)

            elif (isinstance(node, ast.If)
                    and isinstance(node.test, ast.Compare)
                    and isinstance(node.test.left, ast.Name)
                    and node.test.left.id == "__name__"
                    and isinstance(node.test.comparators[0], ast.Constant)
                    and node.test.comparators[0].value == "__main__"):
                main_logic = self.extract_main_logic(node.body)

        return functions, imports, main_logic

    @staticmethod
    def _extract_function(node, source_code: str, functions: dict) -> None:
        func_name = node.name
        func_code = ast.get_source_segment(source_code, node)
        num_inputs = len(node.args.args)

        namespace = {}
        exec(func_code, namespace)
        function = namespace[func_name]

        box_function = BoxFunction(name=func_name, function=function, min_args=num_inputs, max_args=num_inputs)
        functions[func_name] = box_function

    @staticmethod
    def extract_main_logic(nodes) -> List[dict]:
        """Extract function calls from the main block."""
        main_logic = []
        functions_to_ignore = {"print"}

        for stmt in nodes:
            function_call = stmt.value
            function_name = function_call.func.id if isinstance(function_call.func, ast.Name) else None
            if function_name is None or function_name in functions_to_ignore:
                continue

            args = [
                arg.id if isinstance(arg, ast.Name) else ast.dump(arg)
                for arg in function_call.args
            ]

            assigned_vars = []
            for target in stmt.targets:
                if isinstance(target, ast.Tuple):
                    assigned_vars.extend([t.id for t in target.elts if isinstance(t, ast.Name)])
                elif isinstance(target, ast.Name):
                    assigned_vars.append(target.id)

            function_data = {"function_name": function_name, "args": args, "assigned_variables": assigned_vars}
            main_logic.append(function_data)

        return main_logic


    @staticmethod
    def _extract_imports(node, imports):
        for alias in node.names:
            imports.append(f"import {alias.name}")

    @staticmethod
    def _extract_imports_from(node, imports):
        if node.module:
            module = node.module
        else:
            module = "." * node.level

        for alias in node.names:
            imports.append(f"from {module} import {alias.name}")
