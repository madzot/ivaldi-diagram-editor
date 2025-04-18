import ast
import os
import random
import string
from typing import List
from typing import TextIO

from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.frontend.canvas_objects.box import Box
from MVP.refactored.frontend.components.custom_canvas import CustomCanvas
from MVP.refactored.util.importer.importer import Importer
from MVP.refactored.util.importer.json_importer.function_call import FunctionCall


class PythonImporter(Importer):

    def start_import(self, python_files: List[TextIO]) -> str:
        all_functions = {}
        all_imports = []
        main_logic = None
        main_diagram_name = None

        for python_file in python_files:
            file_functions, file_imports, file_main_logic = PythonImporter._extract_data_from_file(python_file)

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

        self.load_everything_to_canvas({"functions": all_functions, "main_logic": main_logic}, self.canvas)
        return main_diagram_name

    def load_everything_to_canvas(self, data: dict, canvas: CustomCanvas) -> None:
        functions = data["functions"]
        main_logic: List[FunctionCall] = data["main_logic"]

        elements_y_position = 300
        boxes_gap = 900 // (len(main_logic) - 1)
        box_x = 100

        possible_outputs = {}
        box_right_connection_spiders = {}

        for function_call in main_logic:
            function_name = function_call.function_name
            function_arguments = function_call.arguments

            for assigned_variable in function_call.assigned_variables:
                possible_outputs[assigned_variable] = function_name

            box_position = (box_x, elements_y_position)
            new_box = PythonImporter._add_box_to_canvas(canvas, box_position, functions, function_name)

            for function_argument in function_arguments:
                left_connection = new_box.add_left_connection()
                canvas.start_wire_from_connection(left_connection)

                wire_end_function_name = PythonImporter._find_function_that_returns_variable(main_logic, function_argument)

                if wire_end_function_name:
                    possible_outputs.pop(function_argument, None)
                    PythonImporter._end_wire_to_previous_connected_box(
                        canvas, function_argument, wire_end_function_name,
                        box_right_connection_spiders, boxes_gap, elements_y_position
                    )
                else:
                    diagram_input = canvas.add_diagram_input()
                    canvas.end_wire_to_connection(diagram_input, True)

            new_box.lock_box()
            box_x += boxes_gap

        PythonImporter._add_outputs_to_canvas(canvas, possible_outputs)

    @staticmethod
    def _add_box_to_canvas(canvas: CustomCanvas, box_position: tuple, functions: dict, function_name: str) -> Box:
        new_box = canvas.add_box(box_position)
        new_box.set_label(function_name)

        box_function: BoxFunction = functions[function_name]
        new_box.set_box_function(box_function)

        canvas.main_diagram.add_function_to_label_content(function_name, box_function.main_function)
        return new_box

    @staticmethod
    def _find_function_that_returns_variable(main_logic: List[FunctionCall], variable_to_find: str) -> str | None:
        for possible_right_connection_function in main_logic:
            for assigned_variable in possible_right_connection_function.assigned_variables:
                if assigned_variable == variable_to_find:
                    return possible_right_connection_function.function_name

        return None

    @staticmethod
    def _end_wire_to_previous_connected_box(canvas: CustomCanvas,
                                            function_argument: str,
                                            previous_connected_box_label: str,
                                            box_right_connection_spiders: dict,
                                            boxes_gap: int,
                                            elements_y_position: int) -> None:
        for box in canvas.boxes:
            if box.label_text == previous_connected_box_label:

                new_spider_added = False
                if function_argument not in box_right_connection_spiders.keys():
                    spider_x_position = box.x + boxes_gap / 2
                    new_spider = canvas.add_spider(loc=(spider_x_position, elements_y_position))
                    box_right_connection_spiders[function_argument] = new_spider
                    new_spider_added = True

                connection_spider = box_right_connection_spiders[function_argument]
                canvas.end_wire_to_connection(connection_spider, True)

                if new_spider_added:
                    wire_end_connection = box.add_right_connection()
                    canvas.start_wire_from_connection(connection_spider)
                    canvas.end_wire_to_connection(wire_end_connection, True)

                break

    @staticmethod
    def _add_outputs_to_canvas(canvas: CustomCanvas, outputs: dict) -> None:
        for box_label in outputs.values():
            for box in canvas.boxes:
                if box.label_text == box_label:
                    wire_start_connection = box.add_right_connection()
                    canvas.start_wire_from_connection(wire_start_connection)
                    break

            output = canvas.add_diagram_output()
            canvas.end_wire_to_connection(output, True)

    @staticmethod
    def _extract_data_from_file(python_file: TextIO) -> tuple:
        functions = {}
        imports = []
        main_logic = None

        source_code = python_file.read()
        tree = ast.parse(source_code)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                PythonImporter._extract_function(node, source_code, functions)

        for node in tree.body:
            if isinstance(node, ast.Import):
                PythonImporter._extract_imports(node, imports)

            elif isinstance(node, ast.ImportFrom):
                PythonImporter._extract_imports_from(node, imports)

            elif (isinstance(node, ast.If)
                    and isinstance(node.test, ast.Compare)
                    and isinstance(node.test.left, ast.Name)
                    and node.test.left.id == "__name__"
                    and isinstance(node.test.comparators[0], ast.Constant)
                    and node.test.comparators[0].value == "__main__"):
                main_logic = PythonImporter._extract_main_logic(node.body)
                PythonImporter._convert_mutable_variables_to_immutable(main_logic)

        return functions, imports, main_logic

    @staticmethod
    def _extract_function(node, source_code: str, functions: dict) -> None:
        func_name = node.name
        function = ast.get_source_segment(source_code, node)
        num_inputs = len(node.args.args)

        box_function = BoxFunction(
            main_function_name=func_name, function=function, min_args=num_inputs, max_args=num_inputs
        )
        functions[func_name] = box_function

    @staticmethod
    def _extract_main_logic(nodes) -> List[FunctionCall]:
        """Extract function calls from the main block."""
        main_logic = []
        functions_to_ignore = {"print"}

        for stmt in nodes:
            node_function_call = stmt.value
            function_name = node_function_call.func.id if isinstance(node_function_call.func, ast.Name) else None
            if function_name is None or function_name in functions_to_ignore:
                continue

            arguments = []
            for arg in node_function_call.args:
                if isinstance(arg, ast.Name):
                    arguments.append(arg.id)
                else:
                    arguments.append(ast.dump(arg))

            assigned_variables = []
            for target in stmt.targets:
                if isinstance(target, ast.Tuple):
                    assigned_variables.extend([t.id for t in target.elts if isinstance(t, ast.Name)])
                elif isinstance(target, ast.Name):
                    assigned_variables.append(target.id)

            function_call = FunctionCall(function_name, arguments, assigned_variables)
            main_logic.append(function_call)

        return main_logic

    @staticmethod
    def _convert_mutable_variables_to_immutable(function_calls: List[FunctionCall]) -> None:
        used_variable_names = set()
        for function_call in function_calls:
            for assigned_variable in function_call.assigned_variables:
                used_variable_names.add(assigned_variable)

        declared_variable_names = set()
        variables_new_names = {}

        for function_call in function_calls:

            arguments = function_call.arguments
            for index in range(len(arguments)):
                argument = arguments[index]

                if argument in variables_new_names.keys():
                    arguments[index] = variables_new_names[argument]

            assigned_variables = function_call.assigned_variables
            for index in range(len(assigned_variables)):
                assigned_variable = assigned_variables[index]

                if assigned_variable in declared_variable_names:
                    new_variable_name = assigned_variable
                    while new_variable_name in used_variable_names :
                        new_variable_name = PythonImporter._generate_new_variable_name(assigned_variable)

                    assigned_variables[index] = new_variable_name
                    variables_new_names[assigned_variable] = new_variable_name
                else:
                    declared_variable_names.add(assigned_variable)

    @staticmethod
    def _check_and_replace_variables(variables: List[str],
                                     declared_variable_names: set,
                                     variables_new_names: dict,
                                     used_variable_names: set) -> None:
        for index in range(len(variables)):
            variable = variables[index]

            if variable in declared_variable_names:
                if variable in variables_new_names.keys():
                    variables[index] = variables_new_names[variable]
                else:
                    new_variable_name = variable
                    while new_variable_name in used_variable_names:
                        new_variable_name = PythonImporter._generate_new_variable_name(variable)

                    variables[index] = new_variable_name
                    variables_new_names[variable] = new_variable_name
            else:
                declared_variable_names.add(variable)

    @staticmethod
    def _generate_new_variable_name(variable_name: str) -> str:
        """Generate a new variable name by appending a random suffix."""
        chars = string.ascii_letters + string.digits
        suffix = ''.join(random.choice(chars) for _ in range(10))
        return f"{variable_name}_{suffix}"

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
