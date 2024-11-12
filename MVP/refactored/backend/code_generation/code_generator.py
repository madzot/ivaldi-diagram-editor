import re
from queue import Queue
from io import StringIO
from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.backend.code_generation.renamer import Renamer
from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.custom_canvas import CustomCanvas


class CodeGenerator: # TODO get_result, and remove extra spaces
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
    def get_all_methods_code(cls, code_part: dict[BoxFunction, list[int]]) -> dict[tuple[int], str]:
        # check
        all_methods_code: dict[tuple[int], str] = dict()

        for function, box_ids in code_part.items():
            method_name = function.name
            index = function.code.find("def invoke")
            code = function.code[:index + 4] + method_name + function.code[index + 10:]
            all_methods_code[tuple(box_ids)] = code

        return all_methods_code

    @classmethod
    def construct_main_function(cls, code_part: dict[tuple[int], str], canvas: CustomCanvas) -> str:
        nodes_queue = Queue()
        main_function = StringIO()
        main_function.write("def get_result():\n\t")

        hypergraph = HypergraphManager.get_graph_by_id(canvas.id)
        node_input_count_check: dict[int, int] = {}
        current_level_nodes = set(hypergraph.get_node_by_input(input_id) for input_id in hypergraph.inputs)

        for node in current_level_nodes:
            nodes_queue.put(node.id)

        while current_level_nodes:
            current_level_nodes = cls.get_children_nodes(current_level_nodes, node_input_count_check)

            for node in current_level_nodes:
                nodes_queue.put(node.id)

        while not nodes_queue.empty():
            node_id = nodes_queue.get()

            for nodes_ids, code in code_part.items():
                if node_id in nodes_ids:
                    pattern = r"def\s+([a-zA-Z_][\w]*)\s*\(([^)]*)\)"
                    match = re.search(pattern, code)

                    if match:
                        func_name = match.group(1)
                        params = [param.split(":")[0].strip() for param in match.group(2).split(",")]
                        function_signature = f"{func_name}({', '.join(params)})"
                        main_function.write(function_signature + '\n\t')

        return main_function.getvalue()

    @classmethod
    def get_children_nodes(cls, current_level_nodes: list[Node], node_input_count_check: dict[int, int]) -> list:
        """
        Get the next level of child nodes.
        This method checks each node’s children and adds them if they have all required inputs.
        Args:
            current_level_nodes: The nodes being processed at the current level.
            node_input_count_check: A dictionary tracking input counts for each node ID.
        Returns:
            list: The next level of child nodes.
        """
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
