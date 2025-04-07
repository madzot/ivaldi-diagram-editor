import ast
from typing import Optional

import astor  # Requires pip install astor


class CodeInspector(ast.NodeTransformer):
    def __init__(self, target_name: str = None, new_name: str = None):
        self.target_name = target_name
        self.new_name = new_name
        self.current_function_globals = set()
        self.current_function_params = set()
        self.main_function_body = None
        self.global_vars = set()
        self.global_statements = set()
        self.function_names = set()

    def visit_Assign(self, node):
        if hasattr(node, "parent") and isinstance(node.parent, ast.Module):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.global_vars.add(target.id)
        self.generic_visit(node)

        return node

    def visit_FunctionDef(self, node):
        self.function_names.add(node.name)
        if node.name == self.target_name:
            node.name = self.new_name

        self.current_function_params = {arg.arg for arg in node.args.args}

        for stmt in node.body:
            if isinstance(stmt, ast.Global):
                stmt.names = [
                    self.new_name if name == self.target_name else name
                    for name in stmt.names
                ]
                self.global_statements.update(stmt.names)
                self.current_function_globals.update(stmt.names)

        self.generic_visit(node)

        self.current_function_globals.clear()
        self.current_function_params.clear()

        return node

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == self.target_name:
            node.func.id = self.new_name
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        if (
                node.id == self.target_name
                and (
                node.id in self.current_function_globals
                or not self.current_function_params)
        ):
            node.id = self.new_name

        return node

    def refactor_code(self, code_str: str, target_name: str, new_name: str):
        if target_name:
            self.target_name = target_name
        if new_name:
            self.new_name = new_name
        tree = ast.parse(code_str)
        self.visit(tree)
        return astor.to_source(tree)

    def _attach_parents(self, node, parent=None):
        node.parent = parent
        for child in ast.iter_child_nodes(node):
            self._attach_parents(child, node)

    def find_globals(self, code_str):
        tree = ast.parse(code_str)
        self._attach_parents(tree)
        self.visit(tree)

        all_globals = self.global_vars.union(self.global_statements)
        self.cleanup()
        return all_globals

    def find_function_names(self, code_str):
        tree = ast.parse(code_str)
        self.visit(tree)

        functions = set(self.function_names)
        self.cleanup()
        return functions

    def cleanup(self):
        self.global_vars.clear()
        self.global_statements.clear()
        self.function_names.clear()

    @classmethod
    def get_main_function(cls, code_str: str, main_method_name: str) -> Optional[str]:
        """
        Extracts the source code for a function matching `main_method_name` from the given code string.
        """
        tree = ast.parse(code_str)
        main_method = None
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == main_method_name:
                main_method = node
                break

        if main_method is None:
            return None

        return astor.to_source(main_method)

    @classmethod
    def get_help_methods(cls, code_str: str, main_method_name: str) -> Optional[list[str]]:
        """
        Extracts all method definitions from the given code string, excluding the main method.
        """
        tree = ast.parse(code_str)
        methods = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name != main_method_name:
                methods.append(node)

        if not methods:
            return None

        return [astor.to_source(method) for method in methods]

    @classmethod
    def get_imports(cls, code_str) -> Optional[list[str]]:
        """
        Parse the provided Python code string and extract import statements.
        """
        tree = ast.parse(code_str)
        imports = []

        for node in tree.body:
            if isinstance(node, ast.Import):
                imports.append(node)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node)

        if not imports:
            return None

        return [astor.to_source(ast_import) for ast_import in imports]
