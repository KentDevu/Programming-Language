from typing import Any
from token_type import TokenType

class Token:
    def __init__(self, type: TokenType, value: Any, line: int, column: int, is_deleted: bool = False):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
        self.is_deleted = is_deleted

    def __str__(self):
        return f'Token({self.type}, {self.value}, pos={self.line}:{self.column}, deleted={self.is_deleted})'