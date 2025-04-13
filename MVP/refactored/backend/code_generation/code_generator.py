from typing import Optional

import autopep8
from queue import Queue

from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.backend.code_generation.code_inspector import CodeInspector
from MVP.refactored.backend.diagram import Diagram
from MVP.refactored.backend.diagram_callback import Receiver
from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge
from MVP.refactored.backend.resource import Resource
from MVP.refactored.backend.types.connection_info import ConnectionInfo
from MVP.refactored.frontend.components.custom_canvas import CustomCanvas


class CodeGenerator:
    @classmethod
    def generate_code(cls, canvas: CustomCanvas, canvasses: dict[int, CustomCanvas]) -> str:
        """
            Generates Python code based on the structure and functional elements of the provided canvas and related canvasses.

            This method processes a set of box functions associated with the given canvas, extracts global statements, helper
            functions, and main functions, renames them for uniqueness, and constructs the final composite Python script.
            The resulting script is formatted using the autopep8 library and written to a file named "diagram.py".
            The formatted code is also returned by the method as a string.

            Arguments:
                canvas (CustomCanvas): The main canvas from which the function hierarchy
                    and code elements are derived.
                canvasses (dict[int, CustomCanvas]): A dictionary mapping canvas IDs to
                    their corresponding CustomCanvas objects. This is used to retrieve
                    data interconnected with the primary canvas.

            Returns:
                str: The generated and auto formatted Python code as a single string.
        """
        box_functions: set[BoxFunction] = cls.get_all_box_functions(canvas, canvasses)

        box_functions_items_names: dict[BoxFunction, set[str]] = cls.get_box_functions_items_names(box_functions)

        (global_statements,
         helper_functions,
         main_functions,
         main_functions_new_names) = CodeInspector.rename(box_functions_items_names)

        # imports
        file_content = "".join(set(imp for f in box_functions for imp in f.imports))
        # global statements
        file_content += "".join(global_statements) + "\n"
        # helper functions
        file_content += "\n\n".join(helper_functions) + "\n\n"
        # functions
        file_content += "\n\n".join(main_functions)
        # main functions
        hypergraphs_on_this_canvas = HypergraphManager.get_graphs_by_canvas_id(canvas.id)
        for i, hypergraph in enumerate(hypergraphs_on_this_canvas):
            func_name = f"main_{i}"
            file_content += "\n\n" + cls.construct_main_function(hypergraph, main_functions_new_names, func_name,
                                                                 canvas)

        return autopep8.fix_code(file_content)

    @classmethod
    def get_all_box_functions(cls, canvas: CustomCanvas, canvasses: dict[int, CustomCanvas]) -> set[BoxFunction]:
        """
            Retrieve all unique BoxFunctions from the specified canvas and related canvasses.

            Iterates through all boxes in the provided canvas and recursively collects BoxFunctions
            from referenced canvasses. This method is designed to explore a hierarchical or nested
            structure of canvasses and boxes, ensuring all connected BoxFunctions are gathered.
        """
        box_functions: set[BoxFunction] = set()
        for box in canvas.boxes:
            if str(box.id) in canvasses:
                box_functions.update(cls.get_all_box_functions(canvasses.get(str(box.id)), canvasses))
            else:
                box_functions.add(box.box_function)
        return box_functions

    @classmethod
    def get_box_functions_items_names(cls, box_functions: set[BoxFunction]) -> dict[BoxFunction, set[str]]:
        """
        Retrieve a mapping of BoxFunction objects to the set of names of globals and
        functions associated with each BoxFunction.
        """
        box_functions_items_names: dict[
            BoxFunction, set[str]] = {}  # {box_func: set(of all names of globals and functions)}

        for box_function in box_functions:
            variables = set()
            variables.update(CodeInspector.get_names(box_function.global_statements))
            variables.update(CodeInspector.get_names(box_function.helper_functions))
            variables.update(CodeInspector.get_names([box_function.main_function]))

            box_functions_items_names[box_function] = variables
        return box_functions_items_names

    @classmethod
    def construct_main_function(cls,
                                hypergraph: Hypergraph,
                                renamed_functions: dict[BoxFunction, str],
                                func_name: str,
                                canvas: CustomCanvas,
                                ) -> str:

        main_function: str = ""

        receiver: Receiver = canvas.receiver
        diagram_inputs_as_nodes = sorted(
            (s for s in hypergraph.get_hypergraph_source()
             if receiver.diagrams[canvas.id].get_input_by_id(s.id) is not None),
            key=lambda s: receiver.diagrams[canvas.id].get_input_by_id(s.id).index
        )

        (function_definition,
         node_and_hyper_edge_to_variable_name) = cls.create_definition_of_main_function(diagram_inputs_as_nodes,
                                                                                        func_name,
                                                                                        receiver)

        hyper_edge_queue: Queue[HyperEdge] = Queue()
        cls.get_queue_of_hyper_edges(hypergraph, hyper_edge_queue)
        reversed_items = list(reversed(list(hyper_edge_queue.queue)))
        hyper_edge_queue.queue.clear()
        [hyper_edge_queue.put(item) for item in reversed_items]

        (main_function_content,
         node_and_hyper_edge_to_variable_name) = cls.create_main_function_content(hyper_edge_queue,
                                                                                  renamed_functions,
                                                                                  node_and_hyper_edge_to_variable_name,
                                                                                  receiver)

        main_function_return = "\n\treturn "
        added: set[int] = set()
        for output in hypergraph.get_hypergraph_target():  # TODO it can be wrong order
            if cls.get_actual_node_group_hash(output,
                                              receiver) in node_and_hyper_edge_to_variable_name and output.node_group_hash() not in added:
                main_function_return += f"{node_and_hyper_edge_to_variable_name[cls.get_actual_node_group_hash(output, receiver)]}, "
                added.add(output.node_group_hash())
        main_function_return = main_function_return[:-2 if len(added) > 0 else -1]

        main_function += function_definition
        main_function += main_function_content
        main_function += main_function_return
        return main_function

    @classmethod
    def create_definition_of_main_function(cls, diagram_inputs_as_nodes: list[Node], func_name: str,
                                           receiver: Receiver) -> str:
        """
            Create the definition of a main function for the given hypergraph.
        """
        definition: str = f"def {func_name}("

        node_and_hyper_edge_to_variable_name: dict[int, str] = dict()
        index: int = -1

        # Iterate over the source nodes to construct the function's input parameters
        for node in diagram_inputs_as_nodes:
            actual_hash: int = (
                cls.get_actual_node_group_hash(node, receiver)
            )
            index += 1
            var_name = f"input_{index}"
            definition += f"{var_name} = None, "
            node_and_hyper_edge_to_variable_name[actual_hash] = var_name

        definition = (definition[:-2] if index > 0 else definition) + "):"

        return definition, node_and_hyper_edge_to_variable_name

    @classmethod
    def create_main_function_content(cls,
                                     queue: Queue[HyperEdge],
                                     renamed_functions: dict[BoxFunction, str],
                                     node_and_hyper_edge_to_variable_name: dict[int, str],
                                     receiver: Receiver
                                     ) -> str:
        """
            Create the content of the main function.
        """
        main_function_content = ""
        index = 0
        while not queue.empty():
            hyper_edge = queue.get()
            variable = f"res_{index}"
            variable_definition = f"{variable} = {renamed_functions[hyper_edge.get_box_function()]}("

            for source_node in hyper_edge.get_source_nodes():
                key = cls.get_actual_node_group_hash(source_node, receiver)
                variable_definition += f"{node_and_hyper_edge_to_variable_name[key]}, "
            variable_definition = variable_definition[:-2] + ")"
            main_function_content += f"\n\t{variable_definition}"

            if len(hyper_edge.get_target_nodes()) > 1:
                for i, target_node in enumerate(hyper_edge.get_target_nodes()):
                    key = cls.get_actual_node_group_hash(target_node, receiver)
                    if key not in node_and_hyper_edge_to_variable_name:
                        node_and_hyper_edge_to_variable_name[key] = f"{variable}[{i}]"
            else:
                target_node = hyper_edge.get_target_nodes()[0]
                key = cls.get_actual_node_group_hash(target_node, receiver)
                node_and_hyper_edge_to_variable_name[key] = variable

            index += 1
        return main_function_content, node_and_hyper_edge_to_variable_name

    @classmethod
    def get_actual_node_group_hash(cls, node: Node, receiver: Receiver) -> int:
        for hyper_edge in node.get_output_hyper_edges():
            if hyper_edge.is_compound():
                con_i: int = next(
                    (k for k, v in hyper_edge.source_nodes.items() if v.node_group_hash() == node.node_group_hash()),
                    None)
                sub_diagram: Diagram = receiver.diagrams[hyper_edge.id]
                sub_diagram_input: ConnectionInfo = sub_diagram.get_input_by_index(con_i)
                resource: Resource = next(r for r in sub_diagram.resources if
                                          sub_diagram_input in (r.get_left_connections() + r.get_right_connections()))
                deeper_node: Node = HypergraphManager.get_node_by_node_id(resource.id)
                return cls.get_actual_node_group_hash(deeper_node, receiver)
        return node.node_group_hash()

    @classmethod
    def get_queue_of_hyper_edges(cls,
                                 hypergraph: Hypergraph,
                                 hyper_edge_queue: Queue[HyperEdge],
                                 seen_hyper_edges: set[HyperEdge] = None
                                 ) -> Queue[HyperEdge]:

        if seen_hyper_edges is None:
            seen_hyper_edges = set()

        nodes_with_inputs: set[Node] = set(hypergraph.get_hypergraph_source())
        to_check: list[HyperEdge] = hypergraph.get_all_hyper_edges()
        hyper_edge_input_count_check: dict[HyperEdge, int] = {}

        while to_check:
            to_check_new: list[HyperEdge] = []
            for hyper_edge in to_check:
                if hyper_edge in seen_hyper_edges:
                    continue

                for subgraph in hyper_edge.get_hypergraphs_inside():
                    cls.get_queue_of_hyper_edges(subgraph, hyper_edge_queue, seen_hyper_edges)

                if hyper_edge not in hyper_edge_input_count_check:
                    hyper_edge_input_count_check[hyper_edge] = 0

                for node in hyper_edge.get_source_nodes():
                    if node in nodes_with_inputs:
                        hyper_edge_input_count_check[hyper_edge] += 1

                if hyper_edge_input_count_check[hyper_edge] == len(hyper_edge.get_source_nodes()):
                    hyper_edge_queue.put(hyper_edge)
                    seen_hyper_edges.add(hyper_edge)
                    for target_node in hyper_edge.get_target_nodes():
                        nodes_with_inputs.add(target_node)
                else:
                    to_check_new.append(hyper_edge)

            if to_check == to_check_new:
                break
            to_check = to_check_new
