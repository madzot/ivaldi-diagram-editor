import ast
from typing import List

from MVP.refactored.backend.box_functions.function_structure.code_line import CodeLine
from MVP.refactored.backend.box_functions.function_structure.function_structure import FunctionStructure


class FunctionParser(ast.NodeVisitor):

    def __init__(self):
        self.body_lines: List[CodeLine] = []
        self.return_line: CodeLine|None = None

    @staticmethod
    def parse_function_structure(function_code: str) -> FunctionStructure:
        """
        Parse the function code and extract its structure.

        Args:
            function_code (str): The Python code of the function to parse.

        Returns:
            FunctionStructure: An object representing the structure of the function.
        """
        tree = ast.parse(function_code)
        parser = FunctionParser()
        parser.visit(tree)

        return FunctionStructure(body_lines=parser.body_lines, return_line=parser.return_line)

    def visit_Assign(self, node: ast.Assign):
        assigned_variables = []
        for target in node.targets:
            if isinstance(target, ast.Name):
                assigned_variables.append(target.id)
            elif isinstance(target, (ast.Tuple, ast.List)):
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        assigned_variables.append(elt.id)

        expression = ast.unparse(node.value)

        used_variables = []
        for n in ast.walk(node.value):
            if isinstance(n, ast.Name) and not self._is_function_name(n, node.value):
                used_variables.append(n.id)

        code_line = CodeLine(assigned_variables=assigned_variables, expression=expression, used_variables=used_variables)
        self.body_lines.append(code_line)

    def visit_Return(self, node: ast.Return):
        expression = ast.unparse(node.value)

        used_vars = []
        for n in ast.walk(node.value):
            if isinstance(n, ast.Name) and not self._is_function_name(n, node.value):
                used_vars.append(n.id)

        self.return_line = CodeLine(expression=expression, used_variables=used_vars)

    def _is_function_name(self, name_node: ast.Name, context_node: ast.AST) -> bool:
        for parent in ast.walk(context_node):
            if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name):
                if parent.func is name_node:
                    return True
        return False
