from typing import Optional

import autopep8
from queue import Queue

from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.backend.code_generation.code_inspector import CodeInspector
from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.frontend.components.custom_canvas import CustomCanvas
from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge
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
        for i, hypergraph in enumerate(HypergraphManager.get_graphs_by_canvas_id(canvas.id)):
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
    def construct_main_function(
            cls,
            hypergraph: Hypergraph,
            renamed_functions: dict[BoxFunction, str],
            func_name: str,
            canvas: CustomCanvas) \
            -> str:

        main_function = ""
        diagram_inputs_as_nodes = sorted(
            (s for s in hypergraph.get_hypergraph_source()
             if canvas.receiver.diagrams[canvas.id].get_input_by_id(s.id) is not None),
            key=lambda s: canvas.receiver.diagrams[canvas.id].get_input_by_id(s.id).index
        )

        # --- Step 1: Build the function definition and initialize mappings ---
        (function_definition,
         node_and_hyper_edge_to_variable_name) = (cls.create_definition_of_main_function(
                                                                                        diagram_inputs_as_nodes,
                                                                                        func_name))

        hyper_edge_queue: Queue[HyperEdge] = cls.get_queue_of_hyper_edges(hypergraph)

        # --- Step 5: Generate code lines for hyper edge execution ---
        # This block generates the Python code for executing each hyper edge in the
        # order determined by the topological sort. It maps source nodes to input
        # variables and target nodes to output variables or tuple elements.

        main_function_content = ""  # Initialize the content of the main function
        index = 0  # Index to track the result variable names
        while not hyper_edge_queue.empty():
            hyper_edge = hyper_edge_queue.get()  # Get the next hyper edge from the queue
            variable = f"res_{index}"  # Generate a unique variable name for the result
            # Create the function call for the hyper edge's associated box function
            variable_definition = f"{variable} = {renamed_functions[hyper_edge.get_box_function()]}("
            for source_node in hyper_edge.get_source_nodes():  # Add source node variables as function arguments
                variable_definition += f"{node_and_hyper_edge_to_variable_name[source_node.new_hash()]}, "
            variable_definition = variable_definition[:-2] + ")"  # Remove trailing comma and close the function call
            main_function_content += f"\n\t{variable_definition}"  # Append the function call to the main function content

            # --- Step 6: Map target nodes to output variable or tuple elements ---
            # This block maps the result of the function call to the target nodes of the hyper edge.
            if len(hyper_edge.get_target_nodes()) > 1:  # If there are multiple target nodes
                target_node_index = 0  # Index to track tuple elements
            for source_node in hyper_edge.get_source_nodes():
                variable_definition += f"{node_and_hyper_edge_to_variable_name[source_node.node_group_hash()]}, "
            variable_definition = variable_definition[:-2] + ")"
            main_function_content += f"\n\t{variable_definition}"
            if len(hyper_edge.get_target_nodes()) > 1:
                target_node_index = 0
                for target_node in hyper_edge.get_target_nodes():
                    if target_node.new_hash() not in node_and_hyper_edge_to_variable_name:
                        # Map the target node to a specific tuple element
                        node_and_hyper_edge_to_variable_name[
                            target_node.new_hash()] = f"{variable}[{target_node_index}]"
                    if target_node.node_group_hash() not in node_and_hyper_edge_to_variable_name:
                        node_and_hyper_edge_to_variable_name[target_node.node_group_hash()] = f"{variable}[{target_node_index}]"
                        target_node_index += 1
            else:  # If there is a single target node
                # Map the target node to the result variable
                node_and_hyper_edge_to_variable_name[hyper_edge.get_target_nodes()[0].new_hash()] = variable
            index += 1  # Increment the result variable index
            else:
                node_and_hyper_edge_to_variable_name[hyper_edge.get_target_nodes()[0].node_group_hash()] = variable
            index += 1

        # --- Step 7: Construct the return statement with output variables ---
        main_function_return = "\n\treturn "
        added: set[int] = set()
        for output in hypergraph.get_hypergraph_target():  # TODO it can be wrong order
            if output.new_hash() in node_and_hyper_edge_to_variable_name and output.new_hash() not in added:
                main_function_return += f"{node_and_hyper_edge_to_variable_name[output.new_hash()]}, "
                added.add(output.new_hash())
        for output in hypergraph.get_hypergraph_target(): # TODO it can be wrong order
            if output.node_group_hash() in node_and_hyper_edge_to_variable_name and output.node_group_hash() not in added:
                main_function_return += f"{node_and_hyper_edge_to_variable_name[output.node_group_hash()]}, "
                added.add(output.node_group_hash())
        main_function_return = main_function_return[:-2 if len(added) > 0 else -1]

        # --- Step 8: Combine everything into final function string ---
        main_function += function_definition
        main_function += main_function_content
        main_function += main_function_return
        return main_function

    @classmethod
    def create_definition_of_main_function(cls, diagram_inputs_as_nodes: list[Node], func_name: str) -> str:
        """
            Create the definition of a main function for the given hypergraph.
        """
        definition = f"def {func_name}("

        node_and_hyper_edge_to_variable_name: dict[int, str] = dict()
        index = 0

        # Iterate over the source nodes to construct the function's input parameters
        for node in diagram_inputs_as_nodes:
            node_and_hyper_edge_to_variable_name[node.new_hash()] = f"input_{index}"
            definition += f"{node_and_hyper_edge_to_variable_name[node.new_hash()]} = None, "
            index += 1

        definition = (definition[:-2] if index > 0 else definition) + "):\n\t"

        return definition, node_and_hyper_edge_to_variable_name

    @classmethod
    def get_queue_of_hyper_edges(cls, hypergraph: Hypergraph) -> Queue[HyperEdge]:

        hyper_edge_queue: Queue[HyperEdge] = Queue()
        nodes_with_inputs: list[Node] = list()
        nodes_with_inputs.extend(hypergraph.get_hypergraph_source())
        to_check = hypergraph.get_all_hyper_edges()
        hyper_edge_input_count_check: dict[HyperEdge, int] = dict()

        while len(to_check) > 0:
            to_check_new = list()  # Temporary list to hold hyper edges that cannot be executed yet
            for hyper_edge in to_check:
                hyper_edge_is_hypergraph: Optional[Hypergraph] = HypergraphManager.get_graphs_by_canvas_id(hyper_edge.id)
                if hyper_edge not in hyper_edge_input_count_check.keys():
                    hyper_edge_input_count_check[hyper_edge] = 0  # Initialize input count for the current hyper edge
                if hyper_edge_is_hypergraph:
                    cls.get_queue_of_hyper_edges()
                for node in hyper_edge.get_source_nodes():  # Iterate over source nodes of the hyper edge
                    if node in nodes_with_inputs:  # Check if the source node has inputs
                        hyper_edge_input_count_check[hyper_edge] += 1
                # If all source nodes have inputs, the hyper edge is ready for execution
                if hyper_edge_input_count_check[hyper_edge] == len(hyper_edge.get_source_nodes()):
                    hyper_edge_queue.put(hyper_edge)  # Add the hyper edge to the execution queue
                    for target_node in hyper_edge.get_target_nodes():  # Update target nodes with inputs
                        if target_node not in nodes_with_inputs:
                            nodes_with_inputs.append(target_node)
                else:
                    to_check_new.append(hyper_edge)  # Keep the hyper edge for the next iteration
            to_check = to_check_new  # Update the list of hyper edges to process
        return hyper_edge_queue

    @classmethod
    def create_main_function_content(cls, canvas: CustomCanvas, nodes_queue: Queue[Node],
                                     renamed_functions: dict[BoxFunction, str], hypergraph: Hypergraph
                                     ) -> list[str, dict[int, str]]:

        function_result_variables: dict[int, str] = dict()
        input_index = 1
        result_index = 1
        content = ""

        function_output_index: dict[int, int] = dict()
        for node in hypergraph.nodes:
            if len(node.outputs) > 1:
                function_output_index[node.id] = 0

        while not nodes_queue.empty():
            node = nodes_queue.get()
            variable_name = f"res_{result_index}"
            current_box_function = canvas.get_box_function(node.id)
            line = f"{variable_name} = {renamed_functions[current_box_function]}("
            result_index += 1
            function_result_variables[node.id] = variable_name

            for input_wire in node.inputs:
                input_node = hypergraph.get_node_by_output(input_wire)
                if input_node is None:
                    line += f"input_{input_index}, "
                    input_index += 1
                else:
                    if input_node.id in function_output_index:
                        line += f"{function_result_variables[input_node.id]}[{function_output_index[input_node.id]}], "
                        function_output_index[input_node.id] += 1
                    else:
                        line += f"{function_result_variables[input_node.id]}, "
            line = line[:-2] + ")\n\t"
            content += line

        return content, function_result_variables

    @classmethod
    def create_main_function_return(cls, function_result_variables: dict[int, str], hypergraph: Hypergraph) -> str:
        return_statement = "return "
        output_nodes = set(hypergraph.get_node_by_output(output) for output in hypergraph.outputs)
        for output_node in output_nodes:
            return_statement += f'{function_result_variables.get(output_node.id)}, '
        return return_statement[:-2]

    @classmethod
    def get_children_nodes(cls, current_level_nodes: list[Node], node_input_count_check: dict[int, int]) -> set:
        children = set()

        for node in current_level_nodes:
            current_node_children = node.get_children_nodes()

            for node_child in current_node_children:
                connections_with_parent_node = 0
                for parent_node_output in node.outputs:
                    if parent_node_output in node_child.inputs:
                        connections_with_parent_node += 1

                node_input_count_check[node_child.id] = node_input_count_check.get(node_child.id,
                                                                                   0) + connections_with_parent_node

                if node_input_count_check[node_child.id] == len(node_child.inputs):
                    children.add(node_child)

        return children
