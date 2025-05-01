from typing import List


class CodeLine:

    def __init__(self, assigned_variables: List[str] = None,
                 expression: str = None,
                 called_function_names: List[str] = None,
                 used_variables: List[str] = None,
                 used_constants: List[str] = None):
        self.assigned_variables = assigned_variables or []
        self.expression = expression
        self.called_function_names = called_function_names or []
        self.used_variables = used_variables or []
        self.used_constants = used_constants or []

    def __str__(self):
        assigned_str = ", ".join(self.assigned_variables) if self.assigned_variables else ""
        used_str = ", ".join(self.used_variables)
        constants_str = ", ".join(self.used_constants)
        funcs_str = ", ".join(self.called_function_names)
        return (f"{assigned_str} = {self.expression}  "
                f"# uses: {used_str}; consts: {constants_str}; calls: {funcs_str}")

    def __repr__(self):
        return (f"CodeLine(assigned_variables={self.assigned_variables!r}, "
                f"expression={self.expression!r}, "
                f"called_function_names={self.called_function_names!r}, "
                f"used_variables={self.used_variables!r}, "
                f"used_constants={self.used_constants!r})")

    def __eq__(self, other):
        return (isinstance(other, CodeLine)
                and self.assigned_variables == other.assigned_variables
                and self.expression == other.expression
                and self.called_function_names == other.called_function_names
                and self.used_variables == other.used_variables
                and self.used_constants == other.used_constants)

    def __hash__(self):
        return hash((
            tuple(self.assigned_variables),
            self.expression,
            tuple(self.called_function_names),
            tuple(self.used_variables),
            tuple(self.used_constants)
        ))
