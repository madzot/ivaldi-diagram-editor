import re
from queue import Queue
from io import StringIO
from MVP.refactored.backend.box_functions.box_function import functions, BoxFunction
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.custom_canvas import CustomCanvas


class CodeGenerator:

    @classmethod
    def generate_code(cls, canvas: CustomCanvas, canvasses: dict[str, CustomCanvas], processed_canvases=None) -> str:
        if processed_canvases is None:
            processed_canvases = set()

        processed_canvases.add(canvas.id)
        code_parts: dict[BoxFunction, list[int]] = {}
        file_content = ""

        for box in canvas.boxes:
            box_function = box.box_function

            if box.id in processed_canvases:
                continue

            if canvasses.get(str(box.id)) is None:
                if box_function not in code_parts.keys():
                    code_parts[box_function] = [box.id]
                else:
                    code_parts[box_function].append(box.id)
            else:
                sub_canvas: CustomCanvas = canvasses[str(box.id)]
                return cls.generate_code(sub_canvas, canvasses, processed_canvases)

        all_methods_code = cls.get_all_methods_code(code_parts)  # dict
        main_function = cls.construct_main_function(all_methods_code, canvas)  # str

        file_content += "".join(all_methods_code.values())
        file_content += "\n" + main_function

        with open("diagram.py", "w") as file:
            file.write(file_content)

        return file_content

    @classmethod
    def get_all_methods_code(cls, code_part: dict[BoxFunction, list[int]]) -> dict[tuple[int], str]:
        """Create dictionary that contain box indexes and theirs functions code."""
        all_methods_code: dict[tuple[int], str] = dict()
        for function, box_ids in code_part.items():
            method_name = function.name
            index = function.code.find("def invoke")
            code = function.code[:index + 4] + method_name + function.code[index + 10:]
            all_methods_code[tuple(box_ids)] = code
        return all_methods_code

    @classmethod
    def construct_main_function(cls, code_part: dict[tuple[int], str], canvas: CustomCanvas) -> str:
        main_function = StringIO()
        main_function.write("def get_result():\n\t")

        hypergraph = HypergraphManager.get_graph_by_id(canvas.id)
        nodes_queue = Queue()
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
        children = set()
        for node in current_level_nodes:
            current_node_children = node.get_children()
            for node_child in current_node_children:
                node_input_count_check[node_child.id] = node_input_count_check.get(node_child.id, 0) + 1
                if node_input_count_check[node_child.id] == len(node_child.inputs):
                    children.add(node_child)

        return children
