import os
from inspect import signature
from typing import Optional, Callable, List

import autopep8

from MVP.refactored.backend.code_generation.code_inspector import CodeInspector


def get_predefined_functions() -> dict:
    predefined_functions_dict = {}
    functions_path = os.path.join(os.path.dirname(__file__), "./predefined/")
    dirs_and_files = os.listdir(functions_path)
    for name in dirs_and_files:
        full_path = os.path.join(functions_path, name)
        if os.path.isfile(full_path):
            with open(full_path, "r") as file:
                function_name = name.replace(".py", "").replace("_", " ")
                predefined_functions_dict[function_name] = file.read()
    return predefined_functions_dict


predefined_functions = get_predefined_functions()
INVOKE_METHOD = "invoke"

class BoxFunction:

    def __init__(self,
                 name: Optional[str] = None,
                 function: Optional[Callable] = None,
                 min_args: Optional[int] = None,
                 max_args: Optional[int] = None,
                 imports: Optional[List[str]] = None,
                 file_code: Optional[str] = None,
                 is_predefined_function: bool = False):

        self.name: str = name
        self.imports: List[str] = imports or []
        self.global_statements: List[str] = []
        self.helper_functions: List[Callable] = []
        self.main_function: Optional[Callable] = None
        self.is_predefined_function = is_predefined_function
        self.min_args: Optional[int] = min_args
        self.max_args: Optional[int] = max_args

        if is_predefined_function:
            predefined_file_code = predefined_functions[self.name]
            self._set_data_from_file_code(predefined_file_code)
            # self.code = predefined_file_code  # TODO: Remove this variable after code generation is refactored
        elif file_code is not None:
            self._set_data_from_file_code(file_code)
            # self.code = file_code  # TODO: Remove this variable after code generation is refactored
        else:
            self.main_function: Callable = function
            self.min_args: int = min_args
            self.max_args: int = max_args
            self.imports: list = imports

    def _set_data_from_file_code(self, file_code: str):
        """
        Sets data for the object using file code.

        This method processes the provided file code to determine the main function,
        helper functions, and imported modules within the file. Depending on whether
        the object has a predefined function, it selects the corresponding main and
        helper functions from the file code using appropriate methods.
        """
        if self.is_predefined_function:
            self.main_function = CodeInspector.get_main_function(file_code, INVOKE_METHOD)
            self.helper_functions = CodeInspector.get_help_methods(file_code, INVOKE_METHOD)
        else:
            self.main_function = CodeInspector.get_main_function(file_code, self.name)  # TODO self.name?
            self.helper_functions = CodeInspector.get_help_methods(file_code, self.name)  # TODO self.name?
        self.imports = CodeInspector.get_imports(file_code)
        self.global_statements = list(CodeInspector.get_global_statements(file_code))
        # TODO min_args/max_args

    def count_inputs(self):
        # TODO: may not work, fix if needed
        if self.main_function is None:
            raise ValueError("Main function is not set; cannot count inputs.")
        sig = signature(self.main_function)
        params = sig.parameters
        count = len(params)
        if "self" in params:
            count -= 1
        return count

    def __call__(self, *args):
        return self.main_function(*args)

    def __eq__(self, other):
        """
        Compares the current BoxFunction instance with another object for equality.
        """
        if isinstance(other, BoxFunction):
            return (self.name == other.name
                    and self.main_function == other.main_function
                    and self.helper_functions == other.helper_functions
                    and self.imports == other.imports
                    and self.min_args == other.min_args
                    and self.max_args == other.max_args)
        return False

    def __hash__(self):
        """
        Generates a hash value for an instance based on its attributes to allow its use
        as a key in hash-based collections like sets and dictionaries.
        """
        helper_hash = tuple(func for func in self.helper_functions)
        imports_hash = tuple(self.imports)
        main_function_hash = hash(self.main_function) if self.main_function else 0

        return hash((
            self.name,
            main_function_hash,
            helper_hash,
            imports_hash,
            self.min_args,
            self.max_args
        ))

    def __str__(self) -> str:
        """
        Generates a string representation of a Python file by organizing and assembling
        its components, including imports, global statements, helper functions, and
        the main function. This output is formatted using autopep8 for adherence to
        PEP 8 style guidelines.
        """
        # TODO could be implemented better
        file_content = ""
        for imp in self.imports:
            file_content += f"{imp}\n"
        for global_statement in self.global_statements:
            file_content += f"{global_statement}\n"
        for func in self.helper_functions:
            file_content += f"\n{func}\n"
        if self.main_function:
            file_content += f"\n{self.main_function}\n"
        return autopep8.fix_code(file_content)

    def __repr__(self):
        return self.__str__()
