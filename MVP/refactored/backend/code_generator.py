import re
from queue import Queue
from io import StringIO
from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.custom_canvas import CustomCanvas


class CodeGenerator:

    @classmethod
    def generate_code(cls, canvas: CustomCanvas, canvasses: dict[str, CustomCanvas], processed_canvases=None) -> str:
        """
       Generate the code for a set of boxes on a canvas and write it to a file.

       This method generates code for each box function on the provided canvas by extracting code from each box’s
       function, ensuring that no duplicate functions are added. It constructs an entry point function, `get_result`,
       and saves all the code into a file called 'diagram.py'.

       Args:
           canvas (CustomCanvas): The main canvas containing boxes to generate code from.
           canvasses (dict[str, CustomCanvas]): A dictionary mapping canvas IDs to `CustomCanvas` objects.
           processed_canvases (set, optional): Tracks canvases that have been processed to prevent duplicates.

       Returns:
           str: The complete generated code as a string, also saved to 'diagram.py'.
       """
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
        """
        Create a dictionary mapping box IDs to their function code.

        For each box function, this method modifies the function’s code by replacing the function name with the box
        function name and adds the resulting code to a dictionary.

        Args:
            code_part (dict[BoxFunction, list[int]]): A dictionary mapping `BoxFunction` instances to lists of box IDs.

        Returns:
            dict[tuple[int], str]: A dictionary where keys are tuples of box IDs, and values are modified function code strings.
        """
        all_methods_code: dict[tuple[int], str] = dict()

        for function, box_ids in code_part.items():
            method_name = function.name
            index = function.code.find("def invoke")
            code = function.code[:index + 4] + method_name + function.code[index + 10:]
            all_methods_code[tuple(box_ids)] = code

        return all_methods_code

    @classmethod
    def construct_main_function(cls, code_part: dict[tuple[int], str], canvas: CustomCanvas) -> str:
        """
        Construct the main entry function that calls each box function in order.

        This method traverses the hypergraph corresponding to the canvas and constructs a `get_result` function that
        calls each box function based on the node dependencies.

        Args:
            code_part (dict[tuple[int], str]): A dictionary of box IDs and their associated function code.
            canvas (CustomCanvas): The main canvas from which nodes are retrieved.

        Returns:
            str: The constructed `get_result` function code as a string.
        """
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
        Retrieve the next level of child nodes based on the current nodes and input counts.

        This method checks each node's children and ensures that only children with all required inputs are added to
        the next level. It also updates the input count tracking dictionary.

        Args:
            current_level_nodes (list[Node]): The list of nodes currently being processed.
            node_input_count_check (dict[int, int]): Tracks the input count for each node ID.

        Returns:
            list[Node]: A list of nodes for the next level in the graph traversal.
        """
        children = set()

        for node in current_level_nodes:
            current_node_children = node.get_children()

            for node_child in current_node_children:
                node_input_count_check[node_child.id] = node_input_count_check.get(node_child.id, 0) + 1

                if node_input_count_check[node_child.id] == len(node_child.inputs):
                    children.add(node_child)

        return children
