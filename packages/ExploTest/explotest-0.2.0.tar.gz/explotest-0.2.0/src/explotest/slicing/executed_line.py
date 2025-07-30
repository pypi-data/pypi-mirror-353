import ast
import io
from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutedLine:
    """Struct for each executed line in a program."""
    lineno: int
    end_lineno: int
    code: ast.AST
    file: io.TextIOWrapper

    def code_to_str(self):
        # return ""
        return ast.unparse(self.code)

    def __str__(self):
        return f"{self.file.name}:{self.lineno}-{self.end_lineno}, {self.code_to_str()}"
