import ast

from MVP.refactored.backend.box_functions.function_structure.code_line import CodeLine
from MVP.refactored.backend.box_functions.function_structure.function_structure import FunctionStructure


class FunctionParser(ast.NodeVisitor):

    def __init__(self):
        self.arguments: list[str] = []
        self.body_lines: list[CodeLine] = []
        self.return_line: CodeLine|None = None

    @staticmethod
    def parse_function_code(function_code: str) -> FunctionStructure:
        """
        Parse the function code and extract its structure.

        Args:
            function_code (str): The Python code of the function to parse.

        Returns:
            FunctionStructure: An object representing the structure of the function.
        """
        tree = ast.parse(function_code)
        return FunctionParser.parse_function_tree(tree)

    @staticmethod
    def parse_function_tree(function_tree):
        parser = FunctionParser()
        parser.visit(function_tree)

        return FunctionStructure(arguments=parser.arguments, body_lines=parser.body_lines, return_line=parser.return_line)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.arguments = []
        for arg in node.args.args:
            self.arguments.append(arg.arg)
        self.generic_visit(node)

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
        used_variables, called_function_names, used_constants = self._analyze_expression(node.value)

        code_line = CodeLine(
            assigned_variables=assigned_variables,
            expression=expression,
            called_function_names=called_function_names,
            used_variables=used_variables,
            used_constants=used_constants,
        )

        self.body_lines.append(code_line)

    def visit_Return(self, node: ast.Return):
        expression = ast.unparse(node.value)
        used_variables, called_function_names, used_constants = self._analyze_expression(node.value)

        self.return_line = CodeLine(
            expression=expression,
            called_function_names=called_function_names,
            used_variables=used_variables,
            used_constants=used_constants,
        )

    def _analyze_expression(self, node: ast.AST) -> tuple[list[str], list[str], list[str]]:
        functions_to_ignore = {"print"}
        used_variables = []
        called_function_names = []
        used_constants = []

        for n in ast.walk(node):
            if isinstance(n, ast.Name):
                if self._is_function_name(n, node) and n.id not in functions_to_ignore:
                    called_function_names.append(n.id)
                else:
                    used_variables.append(n.id)
            elif isinstance(n, ast.Constant):
                used_constants.append(repr(n.value))  # `repr` to preserve e.g., string quotes

        return used_variables, called_function_names, used_constants

    def _is_function_name(self, name_node: ast.Name, context_node: ast.AST) -> bool:
        for parent in ast.walk(context_node):
            if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name):
                if parent.func is name_node:
                    return True
        return False
