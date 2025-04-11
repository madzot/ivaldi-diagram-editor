import re
from queue import Queue

import autopep8

from MVP.refactored.backend.box_functions.box_function import BoxFunction
from MVP.refactored.backend.code_generation.renamer import Renamer
from MVP.refactored.backend.hypergraph.hypergraph import Hypergraph
from MVP.refactored.backend.hypergraph.hypergraph_manager import HypergraphManager
from MVP.refactored.backend.hypergraph.node import Node
from MVP.refactored.frontend.components.custom_canvas import CustomCanvas
from MVP.refactored.backend.hypergraph.hyper_edge import HyperEdge
from MVP.refactored.frontend.components.custom_canvas import CustomCanvas


class CodeGenerator:
    @classmethod
    def generate_code(cls, canvas: CustomCanvas, canvasses: dict[str, CustomCanvas], main_diagram) -> str:
        code_parts: dict[BoxFunction, list[int]] = cls.get_all_code_parts(canvas, canvasses, main_diagram)
        file_content = cls.get_imports([f.code for f in code_parts.keys()]) + "\n\n"

        box_functions: dict[BoxFunction, set[str]] = {}

        for box_function in code_parts.keys():
            renamer = Renamer()
            variables = set()
            variables.update(renamer.find_globals(box_function.code))
            variables.update(renamer.find_function_names(box_function.code))
            box_functions[box_function] = variables

        function_list, renamed_functions = cls.rename(box_functions)
        function_list = cls.remove_meta(function_list)
        function_list = cls.remove_imports(function_list)

        file_content += "\n".join(function_list)

        file_content += "\n" + cls.construct_main_function(HypergraphManager.get_graphs_by_canvas_id(canvas.id)[0], renamed_functions)

        with open("diagram.py", "w") as file:
            file.write(autopep8.fix_code(file_content))

        return autopep8.fix_code(file_content)

    @classmethod
    def get_all_code_parts(cls, canvas: CustomCanvas, canvasses: dict[str, CustomCanvas], main_diagram) -> dict[
                            BoxFunction, list[int]]:
        code_parts: dict[BoxFunction, list[int]] = dict()
        hypergraphs = HypergraphManager.get_graphs_by_canvas_id(canvas.id)
        for hypergraph in hypergraphs:
            hyper_edges = hypergraph.get_all_hyper_edges()
            for hyper_edge in hyper_edges:
                if hyper_edge.get_box_function() is not None:
                    if hyper_edge.get_box_function() in code_parts:
                        code_parts[hyper_edge.get_box_function()].append(hyper_edge.id)
                    else:
                        code_parts[hyper_edge.get_box_function()] = [hyper_edge.id]
        # for box in canvas.boxes:
        #     if str(box.id) in canvasses:
        #         code_parts.update(cls.get_all_code_parts(canvasses.get(str(box.id)), canvasses, main_diagram))
        #     else:
        #         box_function = BoxFunction(name=box.label_text, file_code=main_diagram.label_content[box.label_text])
        #         if box_function in code_parts:
        #             code_parts[box_function].append(box.id)
        #         else:
        #             code_parts[box_function] = [box.id]
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
    def rename(cls, names: dict[BoxFunction, set[str]]) -> tuple[list[str], dict[BoxFunction, str]]:
        renamed_code_parts: list[str] = list()
        renamed_functions: dict[BoxFunction, str] = dict()
        for i, (box_function, names) in enumerate(names.items()):
            renamer = Renamer()
            code_part = box_function.code
            for name in names:
                if name == "meta":
                    continue
                new_name = f'{name}_{i}'
                if name == "invoke":
                    renamed_functions[box_function] = new_name
                code_part = renamer.refactor_code(code_part, name, new_name)
            renamed_code_parts.append(code_part)
        return renamed_code_parts, renamed_functions

    @classmethod
    def remove_imports(cls, code_parts: list[str]) -> list[str]:
        regex = r"(^import .+)|(^from .+)"
        regex2 = r"^\n+"
        code_parts_without_imports = []

        for part in code_parts:
            cleaned_part = re.sub(regex, "", part, flags=re.MULTILINE)
            cleaned_part = re.sub(regex2, "", cleaned_part)
            code_parts_without_imports.append(cleaned_part)
        return code_parts_without_imports

    @classmethod
    def remove_meta(cls, code_parts: list[str]) -> list[str]:
        regex = r"^meta\s=\s{[\s\S]+?}"
        regex2 = r"^\n+"
        code_parts_without_meta = []

        for part in code_parts:
            cleaned_part = re.sub(regex, "", part, flags=re.MULTILINE)
            cleaned_part = re.sub(regex2, "", cleaned_part)
            code_parts_without_meta.append(cleaned_part)
        return code_parts_without_meta

    @classmethod
    def construct_main_function(cls, hypergraph: Hypergraph, renamed_functions: dict[BoxFunction, str]) -> str:
        main_function = ""

        function_definition = "def main("
        node_and_hyper_edge_to_variable_name: dict[int, str] = dict()
        hypergraph_source_nodes = hypergraph.get_hypergraph_source()
        for node in hypergraph_source_nodes:
            print(node.__hash__())
        index = 0
        for node in hypergraph_source_nodes: # TODO it can be wrong order
            if node.node_group_hash() not in node_and_hyper_edge_to_variable_name:
                node_and_hyper_edge_to_variable_name[node.node_group_hash()] = f"input_{index}"
                function_definition += f"{node_and_hyper_edge_to_variable_name[node.node_group_hash()]} = None, "
                index += 1
        function_definition = function_definition[:-2] + "):"

        nodes_with_inputs: list[Node] = list()
        nodes_with_inputs.extend(hypergraph_source_nodes)
        hyper_edge_input_count_check: dict[HyperEdge, int] = dict()
        hyper_edge_queue: Queue[HyperEdge] = Queue()
        to_check = hypergraph.get_all_hyper_edges()
        while len(to_check) > 0:
            to_check_new = list()
            for hyper_edge in to_check:
                hyper_edge_input_count_check[hyper_edge] = 0
                for node in hyper_edge.get_source_nodes():
                    if node in nodes_with_inputs:
                        hyper_edge_input_count_check[hyper_edge] += 1
                if hyper_edge_input_count_check[hyper_edge] == len(hyper_edge.get_source_nodes()):
                    hyper_edge_queue.put(hyper_edge)
                    for target_node in hyper_edge.get_target_nodes():
                        if target_node not in nodes_with_inputs:
                            nodes_with_inputs.append(target_node)
                else:
                    to_check_new.append(hyper_edge)
            to_check = to_check_new

        main_function_content = ""
        index = 0
        while not hyper_edge_queue.empty():
            hyper_edge = hyper_edge_queue.get()
            variable = f"res_{index}"
            variable_definition = f"{variable} = {renamed_functions[hyper_edge.get_box_function()]}("
            for source_node in hyper_edge.get_source_nodes():
                variable_definition += f"{node_and_hyper_edge_to_variable_name[source_node.node_group_hash()]}, "
            variable_definition = variable_definition[:-2] + ")"
            main_function_content += f"\n\t{variable_definition}"
            if len(hyper_edge.get_target_nodes()) > 1:
                target_node_index = 0
                for target_node in hyper_edge.get_target_nodes():
                    if target_node.node_group_hash() not in node_and_hyper_edge_to_variable_name:
                        node_and_hyper_edge_to_variable_name[target_node.node_group_hash()] = f"{variable}[{target_node_index}]"
                        target_node_index += 1
            else:
                node_and_hyper_edge_to_variable_name[hyper_edge.get_target_nodes()[0].node_group_hash()] = variable
            index += 1

        main_function_return = "\n\treturn "
        added: set[int] = set()
        for output in hypergraph.get_hypergraph_target(): # TODO it can be wrong order
            if output.node_group_hash() in node_and_hyper_edge_to_variable_name and output.node_group_hash() not in added:
                main_function_return += f"{node_and_hyper_edge_to_variable_name[output.node_group_hash()]}, "
                added.add(output.node_group_hash())
        main_function_return = main_function_return[:-2 if len(added) > 0 else -1]


        main_function += function_definition
        main_function += main_function_content
        main_function += main_function_return
        return main_function

    @classmethod
    def create_definition_of_main_function(cls, input_hyper_edges: set[HyperEdge]) -> str:

        definition = "def main("
        variables_count = sum(map(lambda hyper_edge: len(hyper_edge.get_source_nodes()), input_hyper_edges))
        has_args = False

        for i in range(variables_count):
            definition += f"input_{i + 1} = None, "
            has_args = True
        definition = (definition[:-2] if has_args else definition) + "):\n\t"

        return definition

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
                        
                node_input_count_check[node_child.id] = node_input_count_check.get(node_child.id, 0) + connections_with_parent_node

                if node_input_count_check[node_child.id] == len(node_child.inputs):
                    children.add(node_child)

        return children
