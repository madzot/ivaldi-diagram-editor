from typing import List

from MVP.refactored.backend.box_functions.function_structure.code_line import CodeLine


class FunctionStructure:

    def __init__(self, body_lines: List[CodeLine], return_line: CodeLine):
        self.body_lines = body_lines
        self.return_line = return_line

    def __str__(self):
        body_str = "\n".join(str(line) for line in self.body_lines)
        return f"{body_str}\nreturn {self.return_line.expression}"

    def __repr__(self):
        return (f"FunctionStructure(body_lines={self.body_lines!r}, "
                f"return_line={self.return_line!r})")

    def __eq__(self, other):
        return (self.body_lines == other.body_lines
                and self.return_line == other.return_line)

    def __hash__(self):
        return hash((tuple(self.body_lines), self.return_line))
