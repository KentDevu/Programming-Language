from typing import Dict, List, Any
import math
from nodes import *
from token_type import TokenType
from function import Function
from structs import StructDef, StructInstance

class Interpreter:
    def __init__(self):
        self.functions: Dict[str, Function] = {}
        self.structs: Dict[str, StructDef] = {}
        self.variables: Dict[str, Any] = {}
        self.printed_values: List[Any] = []

    def evaluate(self, node: Node) -> Any:
        if isinstance(node, NumberNode):
            return node.value
        elif isinstance(node, StringNode):
            return node.value
        elif isinstance(node, BoolNode):
            return node.value
        elif isinstance(node, VarNode):
            if node.name not in self.variables:
                raise Exception(f"Undefined variable '{node.name}'")
            return self.variables[node.name]
        elif isinstance(node, FieldAccessNode):
            if node.struct_var not in self.variables:
                raise Exception(f"Undefined variable '{node.struct_var}'")
            struct_instance = self.variables[node.struct_var]
            if not isinstance(struct_instance, StructInstance):
                raise Exception(f"Variable '{node.struct_var}' is not a struct")
            if node.field not in struct_instance.fields:
                raise Exception(f"Field '{node.field}' does not exist in struct '{struct_instance.struct_name}'")
            return struct_instance.fields[node.field]
        elif isinstance(node, StructInitNode):
            if node.struct_name not in self.structs:
                raise Exception(f"Undefined struct '{node.struct_name}'")
            struct_def = self.structs[node.struct_name]
            if len(node.args) != len(struct_def.fields):
                raise Exception(f"Struct '{node.struct_name}' expects {len(struct_def.fields)} fields, got {len(node.args)}")
            field_values = {}
            for field, arg in zip(struct_def.fields, node.args):
                field_values[field] = self.evaluate(arg)
            return StructInstance(node.struct_name, field_values)
        elif isinstance(node, BinOpNode):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.op == TokenType.PLUS:
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            elif node.op == TokenType.MINUS:
                return left - right
            elif node.op == TokenType.MULTIPLY:
                return left * right
            elif node.op == TokenType.DIVIDE:
                if right == 0:
                    raise Exception("Division by zero")
                return left / right
            elif node.op == TokenType.MODULUS:
                return left % right
            elif node.op == TokenType.EXPONENTIATION:
                return math.pow(left, right)
        elif isinstance(node, UnaryOpNode):
            value = self.evaluate(node.node)
            if node.op == TokenType.PLUS:
                return value
            elif node.op == TokenType.MINUS:
                return -value
        elif isinstance(node, CompareNode):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.op == TokenType.EQUAL:
                return left == right
            elif node.op == TokenType.NOT_EQUAL:
                return left != right
            elif node.op == TokenType.LESS:
                return left < right
            elif node.op == TokenType.GREATER:
                return left > right
            elif node.op == TokenType.LESS_EQUAL:
                return left <= right
            elif node.op == TokenType.GREATER_EQUAL:
                return left >= right
        elif isinstance(node, LogicalNode):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.op == TokenType.AND:
                return left and right
            elif node.op == TokenType.OR:
                return left or right
        elif isinstance(node, NotNode):
            value = self.evaluate(node.node)
            return not value
        elif isinstance(node, IfNode):
            condition = self.evaluate(node.condition)
            if condition:
                return self.evaluate(node.then_block)
            elif node.else_block is not None:
                return self.evaluate(node.else_block)
            return None
        elif isinstance(node, ForNode):
            self.evaluate(node.init)
            result = None
            while self.evaluate(node.condition):
                result = self.evaluate(node.body)
                self.evaluate(node.update)
            return result
        elif isinstance(node, AssignNode):
            value = self.evaluate(node.value)
            self.variables[node.var_name] = value
            return value
        elif isinstance(node, PrintNode):
            value = self.evaluate(node.expr)
            self.printed_values.append(value)
            return value
        elif isinstance(node, FunctionCallNode):
            if node.name not in self.functions:
                raise Exception(f"Undefined function '{node.name}'")
            func = self.functions[node.name]
            if len(node.args) != len(func.params):
                raise Exception(f"Function '{node.name}' expects {len(func.params)} arguments, got {len(node.args)}")
            old_vars = self.variables.copy()
            for param, arg in zip(func.params, node.args):
                self.variables[param] = self.evaluate(arg)
            result = self.evaluate(func.body)
            self.variables = old_vars
            return result
        elif isinstance(node, BlockNode):
            result = None
            for stmt in node.statements:
                result = self.evaluate(stmt)
            return result
        raise Exception(f"Unknown node type: {type(node)}")