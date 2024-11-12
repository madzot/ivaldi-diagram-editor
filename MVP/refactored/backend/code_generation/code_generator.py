import re
from queue import Queue
from io import StringIO
from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.backend.code_generation.renamer import Renamer
from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.custom_canvas import CustomCanvas


class CodeGenerator:  # TODO get_result, and remove extra spaces
    @classmethod
    def generate_code(cls, canvas: CustomCanvas, canvasses: dict[str, CustomCanvas]) -> str:
        code_parts: dict[BoxFunction, list[int]] = cls.get_all_code_parts(canvas, canvasses)
        file_content = cls.get_imports([f.code for f in code_parts.keys()]) + "\n"

        box_functions: dict[BoxFunction, set[str]] = {}

        for box_function in code_parts.keys():  # get all variables of code
            renamer = Renamer()
            variables = set()
            variables.update(renamer.find_globals(box_function.code))
            variables.update(renamer.find_function_names(box_function.code))
            box_functions[box_function] = variables

        function_list = cls.rename(box_functions)
        function_list = cls.remove_meta(function_list)
        function_list = cls.remove_imports(function_list)

        file_content += "\n".join(function_list)

        return file_content

    @classmethod
    def get_all_code_parts(cls, canvas: CustomCanvas, canvasses: dict[str, CustomCanvas]) -> dict[BoxFunction, list[int]]:
        code_parts: dict[BoxFunction, list[int]] = dict()
        for box in canvas.boxes:
            if str(box.id) in canvasses:
                code_parts.update(cls.get_all_code_parts(canvasses.get(str(box.id)), canvasses))
            else:
                if box.box_function in code_parts:
                    code_parts[box.box_function].append(box.id)
                else:
                    code_parts[box.box_function] = [box.id]
        return code_parts

    @classmethod
    def get_imports(cls, code_parts: list[str]) -> str:
        regex = r"(^import .+)|(^from .+)"
        imports = set()
        for part in code_parts:
            code_imports = re.finditer(regex, part, re.MULTILINE)
            for code_import in code_imports:
                imports.add(code_import.group())
        return "\n".join(imports)

    @classmethod
    def rename(cls, names: dict[BoxFunction, set[str]]) -> list[str]:
        renamed_code_parts: list[str] = list()
        for i, (box_function, names) in enumerate(names.items()):
            renamer = Renamer()
            code_part = box_function.code
            for name in names:
                if name == "meta":
                    continue
                new_name = f'{name}_{i}'
                code_part = renamer.refactor_code(code_part, name, new_name)
            renamed_code_parts.append(code_part)
        return renamed_code_parts

    @classmethod
    def remove_imports(cls, code_parts: list[str]) -> list[str]:
        regex = r"(^import .+)|(^from .+)"
        regex2 = r"^\n+"
        result = []

        for part in code_parts:
            cleaned_part = re.sub(regex, "", part, flags=re.MULTILINE)
            cleaned_part = re.sub(regex2, "", cleaned_part)
            result.append(cleaned_part)
        return result

    @classmethod
    def remove_meta(cls, code_parts: list[str]) -> list[str]:
        regex = r"^meta\s=\s{[\s\S]+?}"
        regex2 = r"^\n+"
        result = []

        for part in code_parts:
            cleaned_part = re.sub(regex, "", part, flags=re.MULTILINE)
            cleaned_part = re.sub(regex2, "", cleaned_part)
            result.append(cleaned_part)
        return result

    @classmethod
    def construct_main_function(cls, canvas: CustomCanvas, box_functions: dict[BoxFunction, set[str]]) -> str:
        main_function = ""
        hypergraph: Hypergraph = HypergraphManager().get_graph_by_id(canvas.id)
        input_nodes: list[Node] = list(hypergraph.get_node_by_input(input_id) for input_id in hypergraph.inputs)
        nodes_queue: Queue[Node] = Queue()
        node_input_count_check: dict[int, int] = dict()

        for node in input_nodes:
            node_input_count_check[node.id] = 0
            for node_input in node.inputs:
                if hypergraph.get_node_by_input(node_input) is not None:
                    node_input_count_check[node.id] += 1
            if node_input_count_check[node.id] == len(node.inputs):
                nodes_queue.put(node)
            nodes_queue.put(node)

        while len(input_nodes) > 0:
            input_nodes = cls.get_children_nodes(input_nodes, node_input_count_check)
            for node in input_nodes:
                nodes_queue.put(node)

        main_function += cls.create_definition_of_main_function(input_nodes)

        return main_function

    @classmethod
    def create_definition_of_main_function(cls, input_nodes: list[Node]) -> str:
        definition = "def main("
        variables_count = sum(map(lambda node: len(node.inputs), input_nodes))
        for i in range(variables_count):
            definition += f"input_{i + 1} = None, "
        definition = definition[:-2] + "):\n\t"

        return definition

    @classmethod
    def create_main_function_content(cls, nodes_queue: Queue[Node]) -> str:
        content = ""
        while not nodes_queue.empty():
            ...
        return content

    @classmethod
    def get_children_nodes(cls, current_level_nodes: list[Node], node_input_count_check: dict[int, int]) -> list:
        children = set()

        for node in current_level_nodes:
            current_node_children = node.get_children()

            for node_child in current_node_children:
                node_input_count_check[node_child.id] = node_input_count_check.get(node_child.id, 0) + 1

                if node_input_count_check[node_child.id] == len(node_child.inputs):
                    children.add(node_child)

        return children

# TODO check

#     """
#     def copy():
#
#     def fac(n):
#         return fac(n - 1)....
#         _________
#
#     def sum():
#
#     def fac(m):
#         return fac(m - 1)....
#
#     """
