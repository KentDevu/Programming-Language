from typing import Any, List, Optional
from token_type import TokenType

class Node:
    def __init__(self, line: int):
        self.line = line

class NumberNode(Node):
    def __init__(self, value: float, line: int):
        super().__init__(line)
        self.value = value

class StringNode(Node):
    def __init__(self, value: str, line: int):
        super().__init__(line)
        self.value = value

class BoolNode(Node):
    def __init__(self, value: bool, line: int):
        super().__init__(line)
        self.value = value

class NullNode(Node):
    def __init__(self, line: int):
        super().__init__(line)

class VarNode(Node):
    def __init__(self, name: str, line: int):
        super().__init__(line)
        self.name = name

class BinOpNode(Node):
    def __init__(self, op: TokenType, left: Node, right: Node, line: int):
        super().__init__(line)
        self.op = op
        self.left = left
        self.right = right

class UnaryOpNode(Node):
    def __init__(self, op: TokenType, operand: Node, line: int):
        super().__init__(line)
        self.op = op
        self.operand = operand

class LogicalNode(Node):
    def __init__(self, op: TokenType, left: Node, right: Node, line: int):
        super().__init__(line)
        self.op = op
        self.left = left
        self.right = right

class CompareNode(Node):
    def __init__(self, op: TokenType, left: Node, right: Node, line: int):
        super().__init__(line)
        self.op = op
        self.left = left
        self.right = right

class AssignNode(Node):
    def __init__(self, name: str, value: Node, line: int):
        super().__init__(line)
        self.name = name
        self.value = value

class IfNode(Node):
    def __init__(self, condition: Node, then_block: Node, else_block: Optional[Node], line: int):
        super().__init__(line)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

class ForNode(Node):
    def __init__(self, init: Node, condition: Node, update: Node, body: Node, line: int):
        super().__init__(line)
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

class WhileNode(Node):
    def __init__(self, condition: Node, body: Node, line: int):
        super().__init__(line)
        self.condition = condition
        self.body = body

class BlockNode(Node):
    def __init__(self, statements: List[Node], line: int):
        super().__init__(line)
        self.statements = statements

class FunctionCallNode(Node):
    def __init__(self, fname: str, args: List[Node], line: int):
        super().__init__(line)
        self.fname = fname
        self.args = args

class LambdaNode(Node):
    def __init__(self, params: List[str], body: Node, line: int):
        super().__init__(line)
        self.params = params
        self.body = body

class ArrayNode(Node):
    def __init__(self, elements: List[Node], line: int):
        super().__init__(line)
        self.elements = elements

class StructInitNode(Node):
    def __init__(self, struct_name: str, args: List[Node], line: int):
        super().__init__(line)
        self.struct_name = struct_name
        self.args = args

class FieldAccessNode(Node):
    def __init__(self, obj_name: str, field: str, line: int):
        super().__init__(line)
        self.obj_name = obj_name
        self.field = field

class PrintNode(Node):
    def __init__(self, expr: Node, line: int):
        super().__init__(line)
        self.expr = expr

class DeleteNode(Node):
    def __init__(self, var_name: str, line: int):
        super().__init__(line)
        self.var_name = var_name

class ParallelNode(Node):
    def __init__(self, block: Node, line: int):
        super().__init__(line)
        self.block = block

class InputNode(Node):
    def __init__(self, line: int):
        super().__init__(line)

class ReturnNode(Node):
    def __init__(self, expr: Optional[Node], line: int):
        super().__init__(line)
        self.expr = expr