import os
from inspect import signature
from typing import Callable


def get_predefined_functions() -> dict:
    predefined_functions = {}
    functions_path = os.path.join(os.path.dirname(__file__), "./predefined/")
    dirs_and_files = os.listdir(functions_path)
    for name in dirs_and_files:
        full_path = os.path.join(functions_path, name)
        if os.path.isfile(full_path):
            with open(full_path, "r") as file:
                function_name = name.replace(".py", "").replace("_", " ")
                predefined_functions[function_name] = file.read()
    return predefined_functions


predefined_functions = get_predefined_functions()


class BoxFunction:

    def __init__(self,
                 name=None,
                 function=None,
                 min_args=None,
                 max_args=None,
                 imports=None,
                 file_code=None,
                 is_predefined_function=False):
        if imports is None:
            imports = []
            self.imports = imports
        self.name: str = name

        if is_predefined_function:
            predefined_file_code = predefined_functions[self.name]
            self._set_data_from_file_code(predefined_file_code)
            self.code = predefined_file_code # TODO: Remove this variable after code generation is refactored
        elif file_code is not None:
            self._set_data_from_file_code(file_code)
            self.code = file_code # TODO: Remove this variable after code generation is refactored
        else:
            self.function: Callable = function
            self.min_args: int = min_args
            self.max_args: int = max_args
            self.imports: list = imports


    def _set_data_from_file_code(self, file_code: str):
        local = {}
        exec(file_code, {}, local)
        meta = local["meta"]

        self.function = local["invoke"]
        self.min_args = meta["min_args"]
        self.max_args = meta["max_args"]
        # TODO: set imports for predefined functions

    def count_inputs(self):
        # TODO: may not work, fix if needed
        sig = signature(self.function)
        params = sig.parameters
        count = len(params)
        if params["self"]:
            count -= 1
        return count

    def __call__(self, *args):
        return self.function(*args)

    # def __eq__(self, other):
    #     if isinstance(other, BoxFunction):
    #         return (self.name == other.name
    #                 and self.function == other.function
    #                 and self.min_args == other.min_args
    #                 and self.max_args == other.max_args
    #                 and self.imports == other.imports)
    #     return False

    def __eq__(self, other):
        if isinstance(other, BoxFunction):
            return self.code == other.code
        return False

    def __hash__(self):
        return hash(self.code)

    # def __hash__(self):
    #     return hash(self.function)

    def __str__(self):
        return f"BoxFunction: {self.name}\n" \
               f"Min args: {self.min_args}\n" \
               f"Max args: {self.max_args}\n" \
               f"Imports: {self.imports}\n"

    def __repr__(self):
        return self.__str__()
