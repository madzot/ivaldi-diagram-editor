import ast
import astor  # Requires `pip install astor`


class Renamer(ast.NodeTransformer):
    def __init__(self, target_name: str = None, new_name: str = None):
        self.target_name = target_name
        self.new_name = new_name
        self.current_function_globals = set()
        self.current_function_params = set()
        self.global_vars = set()
        self.global_statements = set()
        self.function_names = set()

    def visit_Assign(self, node):
        # Check if the assignment is at the module (top) level
        if hasattr(node, "parent") and isinstance(node.parent, ast.Module):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.global_vars.add(target.id)
        self.generic_visit(node)

        return node

    def visit_FunctionDef(self, node):
        # Rename the function name if it matches the target name
        self.function_names.add(node.name)
        if node.name == self.target_name:
            node.name = self.new_name

        # Track the parameter names in the current function to avoid renaming them
        self.current_function_params = {arg.arg for arg in node.args.args}

        # Check for `global` declarations in the function
        for stmt in node.body:
            if isinstance(stmt, ast.Global):
                # Rename in `global` if the target variable is present
                stmt.names = [
                    self.new_name if name == self.target_name else name
                    for name in stmt.names
                ]
                self.global_statements.update(stmt.names)
                self.current_function_globals.update(stmt.names)

        self.generic_visit(node)

        # Clear tracked names after processing the function
        self.current_function_globals.clear()
        self.current_function_params.clear()

        return node

    def visit_Call(self, node):
        # Rename function calls if the function name matches the target name
        if isinstance(node.func, ast.Name) and node.func.id == self.target_name:
            node.func.id = self.new_name
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        # Rename the variable if it's global or top-level, but avoid renaming parameters
        if (
                node.id == self.target_name
                and (
                node.id in self.current_function_globals
                or not self.current_function_params
        )
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

    def find_globals(self, code_str):
        # Parse the code and add scopes using `ast` and `scopes` modules
        tree = ast.parse(code_str)
        self._attach_parents(tree)
        # Process the AST to find global variables
        self.visit(tree)

        # Combine all identified globals
        all_globals = self.global_vars.union(self.global_statements)
        self.cleanup()
        return all_globals

    def find_function_names(self, code_str):
        # Parse the code and add scopes using `ast` and `scopes` modules
        tree = ast.parse(code_str)
        self.visit(tree)

        # Combine all identified globals
        functions = set(self.function_names)
        self.cleanup()
        return functions

    def cleanup(self):
        self.global_vars.clear()
        self.global_statements.clear()
        self.function_names.clear()

    def _attach_parents(self, node, parent=None):
        """
        Helper function to add a 'parent' attribute to each AST node.
        This is necessary to check if an assignment is directly under the module.
        """
        node.parent = parent
        for child in ast.iter_child_nodes(node):
            self._attach_parents(child, node)


# # Example usage
# code = """
# learners = []
# friends = {}
#
# def add_students():
#     global hren
#     learners.append("New Student")
#
#
# meta = {
#     "hren": "hui"
# }
# """
#
# """
# students = []
# friends = {}
#
# def add_students():
#     global hren
#     students.append("New Student")
#
# """
#
# """
# learners = []
# friends = {}
#
# def add_students():
#     global hren
#     learners.append("New Student")
#
# learners = []
# friends = {}
#
# def add_students():
#     global hren
#     learners.append("New Student")
# """
#
# refactorer = Renamer()
# refactored_code = refactorer.find_globals(code)
# print(refactored_code)