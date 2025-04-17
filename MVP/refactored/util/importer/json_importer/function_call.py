from typing import List


class FunctionCall:

    def __init__(self, function_name: str = None, arguments: List[str] = None, assigned_variables: List[str] = None):
        self.function_name = function_name
        self.arguments = arguments or []
        self.assigned_variables = assigned_variables or []

    def __str__(self):
        return f"{', '.join(self.assigned_variables)} = {self.function_name}({', '.join(self.arguments)})"

    def __repr__(self):
        return (f"FunctionCall(function_name={self.function_name!r}, "
                f"arguments={self.arguments!r}, assigned_variables={self.assigned_variables!r})")

    def __eq__(self, other):
        return (self.function_name == other.function_name
                and self.arguments == other.arguments
                and self.assigned_variables == other.assigned_variables)

    def __hash__(self):
        return hash((self.function_name, tuple(self.arguments), tuple(self.assigned_variables)))
