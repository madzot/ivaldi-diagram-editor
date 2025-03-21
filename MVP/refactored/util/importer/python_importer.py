import ast
from typing import TextIO

from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.frontend.components.custom_canvas import CustomCanvas
from MVP.refactored.util.importer.importer import Importer


class PythonImporter(Importer):

    @staticmethod
    def extract_main_logic(nodes, main_logic):
        """Extract function calls from the main block."""
        for stmt in nodes:
            func_call = stmt.value
            func_name = func_call.func.id if isinstance(func_call.func, ast.Name) else None
            if func_name == "print":
                continue

            args = [
                arg.id if isinstance(arg, ast.Name) else ast.dump(arg)
                for arg in func_call.args
            ]

            assigned_vars = []
            for target in stmt.targets:
                if isinstance(target, ast.Tuple):
                    assigned_vars.extend([t.id for t in target.elts if isinstance(t, ast.Name)])
                elif isinstance(target, ast.Name):
                    assigned_vars.append(target.id)

            main_logic.append({
                "function_name": func_name,
                "args": args,
                "assigned_variables": assigned_vars
            })

    def start_import(self, python_file: TextIO) -> None:
        source_code = python_file.read()
        tree = ast.parse(source_code)

        functions = {}
        main_logic = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):

                func_name = node.name
                func_code = ast.get_source_segment(source_code, node)
                num_inputs = len(node.args.args)

                # Analyze return statements to count outputs
                num_outputs = 0
                for child in ast.walk(node):
                    if isinstance(child, ast.Return):
                        if isinstance(child.value, (ast.Tuple, ast.List)):
                            num_outputs = len(child.value.elts)
                        else:
                            num_outputs = 1

                namespace = {}
                exec(func_code, namespace)
                function = namespace[func_name]

                box_function = BoxFunction(
                    name=func_name, function=function, min_args=num_inputs, max_args=num_inputs   # TODO: add imports
                )
                functions[func_name] = box_function

        # Analyze the main method for function calls
        for node in tree.body:
            if isinstance(node, ast.If):
                # Check for `if __name__ == "__main__"` structure
                if (isinstance(node.test, ast.Compare)
                        and isinstance(node.test.left, ast.Name)
                        and node.test.left.id == "__name__"
                        and isinstance(node.test.comparators[0], ast.Constant)
                        and node.test.comparators[0].value == "__main__"):
                    # Traverse the body of the main block
                    self.extract_main_logic(node.body, main_logic)

        print({"functions": functions, "main_logic": main_logic})
        self.load_everything_to_canvas({"functions": functions, "main_logic": main_logic}, self.canvas)


    def load_everything_to_canvas(self, data: dict, canvas: CustomCanvas) -> None:
        elements_y_position = 300
        #TODO: refactor this to appropriate condition
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

            new_box = canvas.add_box(loc=(box_x, elements_y_position))

            box_function = functions[function_name]
            new_box.set_box_function(box_function)

            for arg in args:
                left_connection = new_box.add_left_connection()
                canvas.start_wire_from_connection(left_connection)

                wire_end = None
                for possible_right_connection_function in main_logic:
                    for assigned_variable in possible_right_connection_function["assigned_variables"]:
                        if assigned_variable == arg:
                            wire_end = possible_right_connection_function["function_name"]
                            if assigned_variable in possible_outputs.keys():
                                possible_outputs.pop(assigned_variable)
                            break

                if wire_end:
                    for box in canvas.boxes:
                        if box.label_text == wire_end:

                            new_spider_added = False
                            if arg not in box_right_connection_spiders.keys():
                                spider_x_position = box.x + boxes_gap / 2
                                new_spider = canvas.add_spider(loc=(spider_x_position, elements_y_position))
                                box_right_connection_spiders[arg] = new_spider

                                new_spider_added = True


                            connection_spider = box_right_connection_spiders[arg]


                            canvas.end_wire_to_connection(connection_spider, True)

                            if new_spider_added:
                                wire_end_connection = box.add_right_connection()
                                canvas.start_wire_from_connection(connection_spider)
                                canvas.end_wire_to_connection(wire_end_connection, True)

                            break
                else:
                    diagram_input = canvas.add_diagram_input()
                    canvas.end_wire_to_connection(diagram_input, True)

            new_box.lock_box()
            box_x += boxes_gap

        for diagram_output_variable, box_label in possible_outputs.items():
            for box in canvas.boxes:
                if box.label_text == box_label:
                    wire_start_connection = box.add_right_connection()
                    canvas.start_wire_from_connection(wire_start_connection)
                    break

            output = canvas.add_diagram_output()
            canvas.end_wire_to_connection(output, True)
