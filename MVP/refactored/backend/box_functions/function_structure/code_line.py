from typing import List


class CodeLine:

    def __init__(self, assigned_variables: List[str] = None, expression: str = None, used_variables: List[str] = None):
        self.assigned_variables = assigned_variables or []
        self.expression = expression
        self.used_variables = used_variables or []

    def __str__(self):
        assigned_str = ", ".join(self.assigned_variables) if self.assigned_variables else ""
        used_str = ", ".join(self.used_variables)
        return f"{assigned_str} = {self.expression}  # uses {used_str}"

    def __repr__(self):
        return (f"CodeLine(assigned_variables={self.assigned_variables!r}, "
                f"expression={self.expression!r}, used_variables={self.used_variables!r})")

    def __eq__(self, other):
        return (isinstance(other, CodeLine)
                and self.assigned_variables == other.assigned_variables
                and self.expression == other.expression
                and self.used_variables == other.used_variables)

    def __hash__(self):
        return hash((tuple(self.assigned_variables), self.expression, tuple(self.used_variables)))
