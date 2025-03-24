from typing import List
from token_type import TokenType

class Node:
    pass

class NumberNode(Node):
    def __init__(self, value: float):
        self.value = value

class StringNode(Node):
    def __init__(self, value: str):
        self.value = value

class BoolNode(Node):
    def __init__(self, value: bool):
        self.value = value

class VarNode(Node):
    def __init__(self, name: str):
        self.name = name

class FieldAccessNode(Node):
    def __init__(self, struct_var: str, field: str):
        self.struct_var = struct_var
        self.field = field

class StructInitNode(Node):
    def __init__(self, struct_name: str, args: List[Node]):
        self.struct_name = struct_name
        self.args = args

class BinOpNode(Node):
    def __init__(self, left: Node, op: TokenType, right: Node):
        self.left = left
        self.op = op
        self.right = right

class UnaryOpNode(Node):
    def __init__(self, op: TokenType, node: Node):
        self.op = op
        self.node = node

class LogicalNode(Node):
    def __init__(self, left: Node, op: TokenType, right: Node):
        self.left = left
        self.op = op
        self.right = right

class NotNode(Node):
    def __init__(self, node: Node):
        self.node = node

class CompareNode(Node):
    def __init__(self, left: Node, op: TokenType, right: Node):
        self.left = left
        self.op = op
        self.right = right

class IfNode(Node):
    def __init__(self, condition: Node, then_block: Node, else_block: Node = None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

class ForNode(Node):
    def __init__(self, init: Node, condition: Node, update: Node, body: Node):
        self.init = init
        self.condition = condition
        self.update = update
        self.body = body

class AssignNode(Node):
    def __init__(self, var_name: str, value: Node):
        self.var_name = var_name
        self.value = value

class PrintNode(Node):
    def __init__(self, expr: Node):
        self.expr = expr

class FunctionCallNode(Node):
    def __init__(self, name: str, args: List[Node]):
        self.name = name
        self.args = args

class BlockNode(Node):
    def __init__(self, statements: List[Node]):
        self.statements = statements