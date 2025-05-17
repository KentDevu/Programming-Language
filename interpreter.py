import logging
from typing import Any, List, Optional
from nodes import *
from token_type import TokenType
from function import Function
from structs import StructDef, StructInstance
from concurrent.futures import ThreadPoolExecutor
import sys

# Increase recursion limit for small recursive functions
sys.setrecursionlimit(10000)

# Custom exception to signal input is needed
class InputRequired(Exception):
    def __init__(self, line: int):
        self.line = line
        super().__init__("Input required")

class ParallelExecutor:
    def __init__(self, interpreter: 'Interpreter', block: BlockNode):
        self.interpreter = interpreter
        self.block = block

    def execute(self):
        self.interpreter.evaluate(self.block)

class Interpreter:
    def __init__(self, verbose: bool = False):
        self.variables: dict = {}
        self.functions: dict = {}
        self.structs: dict = {}
        self.printed_values: List[Any] = []
        self.verbose = verbose
        self.input_value = None
        if verbose:
            logging.basicConfig(level=logging.DEBUG)

    def set_input(self, value: str):
        self.input_value = value

    def evaluate(self, node: Node) -> Any:
        if self.verbose:
            logging.debug(f"Evaluating {type(node).__name__} at line {node.line}")
        
        if isinstance(node, NumberNode):
            return float(node.value)
        elif isinstance(node, StringNode):
            return node.value
        elif isinstance(node, BoolNode):
            return node.value
        elif isinstance(node, NullNode):
            return None
        elif isinstance(node, VarNode):
            if node.name not in self.variables or self.variables[node.name].get('deleted', False):
                raise Exception(f"Access to undefined or deleted variable '{node.name}' at line {node.line}")
            return self.variables[node.name]['value']
        elif isinstance(node, BinOpNode):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.op == TokenType.PLUS:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left + right
                elif isinstance(left, str) and isinstance(right, str):
                    return left + right
                raise Exception(f"Type mismatch in '+' operation at line {node.line}")
            elif node.op == TokenType.MINUS:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left - right
                raise Exception(f"Type mismatch in '-' operation at line {node.line}")
            elif node.op == TokenType.MULTIPLY:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left * right
                raise Exception(f"Type mismatch in '*' operation at line {node.line}")
            elif node.op == TokenType.DIVIDE:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    if right == 0:
                        raise Exception(f"Division by zero at line {node.line}")
                    return left / right
                raise Exception(f"Type mismatch in '/' operation at line {node.line}")
            elif node.op == TokenType.EXPONENTIATION:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left ** right
                raise Exception(f"Type mismatch in '^' operation at line {node.line}")
            elif node.op == TokenType.MODULUS:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    if right == 0:
                        raise Exception(f"Modulus by zero at line {node.line}")
                    return left % right
                raise Exception(f"Type mismatch in '%' operation at line {node.line}")
        elif isinstance(node, UnaryOpNode):
            operand = self.evaluate(node.operand)
            if node.op == TokenType.PLUS:
                if isinstance(operand, (int, float)):
                    return +operand
                raise Exception(f"Type mismatch in unary '+' operation at line {node.line}")
            elif node.op == TokenType.MINUS:
                if isinstance(operand, (int, float)):
                    return -operand
                raise Exception(f"Type mismatch in unary '-' operation at line {node.line}")
            elif node.op == TokenType.NOT:
                if isinstance(operand, bool):
                    return not operand
                raise Exception(f"Type mismatch in 'NOT' operation at line {node.line}")
        elif isinstance(node, LogicalNode):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.op == TokenType.AND:
                if isinstance(left, bool) and isinstance(right, bool):
                    return left and right
                raise Exception(f"Type mismatch in 'AND' operation at line {node.line}")
            elif node.op == TokenType.OR:
                if isinstance(left, bool) and isinstance(right, bool):
                    return left or right
                raise Exception(f"Type mismatch in 'OR' operation at line {node.line}")
        elif isinstance(node, CompareNode):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.op == TokenType.EQUAL:
                return left == right
            elif node.op == TokenType.NOT_EQUAL:
                return left != right
            elif node.op == TokenType.LESS:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left < right
                raise Exception(f"Type mismatch in '<' operation at line {node.line}")
            elif node.op == TokenType.GREATER:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left > right
                raise Exception(f"Type mismatch in '>' operation at line {node.line}")
            elif node.op == TokenType.LESS_EQUAL:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left <= right
                raise Exception(f"Type mismatch in '<=' operation at line {node.line}")
            elif node.op == TokenType.GREATER_EQUAL:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left >= right
                raise Exception(f"Type mismatch in '>=' operation at line {node.line}")
        elif isinstance(node, AssignNode):
            value = self.evaluate(node.value)
            self.variables[node.name] = {'value': value, 'deleted': False}
            return value
        elif isinstance(node, IfNode):
            condition = self.evaluate(node.condition)
            if not isinstance(condition, bool):
                raise Exception(f"Condition must be boolean at line {node.line}")
            if condition:
                return self.evaluate(node.then_block)
            elif node.else_block:
                return self.evaluate(node.else_block)
            return None
        elif isinstance(node, ForNode):
            self.evaluate(node.init)
            while self.evaluate(node.condition):
                result = self.evaluate(node.body)
                if isinstance(result, ReturnNode):
                    return self.evaluate(result.expr) if result.expr else None
                self.evaluate(node.update)
            return None
        elif isinstance(node, WhileNode):
            while True:
                condition = self.evaluate(node.condition)
                if not isinstance(condition, bool):
                    raise Exception(f"Condition must be boolean at line {node.line}")
                if not condition:
                    break
                result = self.evaluate(node.body)
                if isinstance(result, ReturnNode):
                    return self.evaluate(result.expr) if result.expr else None
            return None
        elif isinstance(node, BlockNode):
            for stmt in node.statements:
                result = self.evaluate(stmt)
                if isinstance(result, ReturnNode):
                    return self.evaluate(result.expr) if result.expr else None
                if result is not None:
                    return result
            return None
        elif isinstance(node, FunctionCallNode):
            fname = node.fname
            args = [self.evaluate(arg) for arg in node.args]
            if self.verbose:
                logging.debug(f"Calling function: {fname}, args: {args} at line {node.line}")
            if fname in self.structs:
                struct_def = self.structs[fname]
                if len(args) == 0 and len(struct_def.fields) > 0:
                    fields = {field: None for field in struct_def.fields}
                elif len(struct_def.fields) != len(args):
                    raise Exception(f"Struct '{fname}' expects {len(struct_def.fields)} fields, got {len(args)} at line {node.line}")
                else:
                    fields = {field: float(arg) if isinstance(arg, (int, float)) else arg for field, arg in zip(struct_def.fields, args)}
                return StructInstance(fname, fields)
            if '.' in fname:
                obj_name, method_name = fname.split('.')
                if obj_name not in self.variables:
                    raise Exception(f"Undefined object '{obj_name}' at line {node.line}")
                obj = self.variables[obj_name]['value']
                if not isinstance(obj, StructInstance):
                    raise Exception(f"Variable '{obj_name}' is not a struct at line {node.line}")
                method_key = f"{obj.struct_name}.{method_name}"
                if method_key not in self.functions:
                    raise Exception(f"Method '{method_name}' not found in struct '{obj.struct_name}' at line {node.line}")
                func = self.functions[method_key]
                if len(func.params) != len(args):
                    raise Exception(f"Method '{method_name}' expects {len(func.params)} arguments, got {len(args)} at line {node.line}")
                saved_vars = self.variables.copy()
                for param, arg in zip(func.params, args):
                    self.variables[param] = {'value': arg, 'deleted': False}
                self.variables[obj_name] = {'value': obj, 'deleted': False}
                result = self.evaluate(func.body)
                self.variables = saved_vars
                if isinstance(result, ReturnNode):
                    return self.evaluate(result.expr) if result.expr else None
                return result if result is not None else None
            if fname not in self.functions:
                if fname in self.variables and callable(self.variables[fname]['value']):
                    func = self.variables[fname]['value']
                    return func(*args)
                raise Exception(f"Undefined function '{fname}' at line {node.line}")
            func = self.functions[fname]
            if len(func.params) != len(args):
                raise Exception(f"Function '{fname}' expects {len(func.params)} arguments, got {len(args)} at line {node.line}")
            saved_vars = self.variables.copy()
            for param, arg in zip(func.params, args):
                self.variables[param] = {'value': arg, 'deleted': False}
            result = self.evaluate(func.body)
            self.variables = saved_vars
            if isinstance(result, ReturnNode):
                return self.evaluate(result.expr) if result.expr else None
            return result if result is not None else None
        elif isinstance(node, FunctionDefNode):
            self.functions[node.fname] = Function(node.params, node.body)
            return None
        elif isinstance(node, StructDefNode):
            self.structs[node.struct_name] = StructDef(node.fields)
            return None
        elif isinstance(node, LambdaNode):
            def lambda_func(*args):
                if len(node.params) != len(args):
                    raise Exception(f"Lambda expects {len(node.params)} arguments, got {len(args)} at line {node.line}")
                saved_vars = self.variables.copy()
                for param, arg in zip(node.params, args):
                    self.variables[param] = {'value': arg, 'deleted': False}
                result = self.evaluate(node.body)
                self.variables = saved_vars
                if isinstance(result, ReturnNode):
                    return self.evaluate(result.expr) if result.expr else None
                return result
            return lambda_func
        elif isinstance(node, ArrayNode):
            return [self.evaluate(elem) for elem in node.elements]
        elif isinstance(node, StructInitNode):
            if node.struct_name not in self.structs:
                raise Exception(f"Undefined struct '{node.struct_name}' at line {node.line}")
            struct_def = self.structs[node.struct_name]
            args = [self.evaluate(arg) for arg in node.args]
            if self.verbose:
                logging.debug(f"Initializing struct {node.struct_name} with args: {args} at line {node.line}")
            if len(args) == 0 and len(struct_def.fields) > 0:
                fields = {field: None for field in struct_def.fields}
            elif len(struct_def.fields) != len(args):
                raise Exception(f"Struct '{node.struct_name}' expects {len(struct_def.fields)} fields, got {len(args)} at line {node.line}")
            else:
                fields = {field: float(arg) if isinstance(arg, (int, float)) else arg for field, arg in zip(struct_def.fields, args)}
            return StructInstance(node.struct_name, fields)
        elif isinstance(node, FieldAccessNode):
            if self.verbose:
                logging.debug(f"Accessing field: {node.obj_name}.{node.field} at line {node.line}")
            if node.obj_name not in self.variables:
                raise Exception(f"Undefined variable '{node.obj_name}' at line {node.line}")
            obj = self.variables[node.obj_name]['value']
            if not isinstance(obj, StructInstance):
                raise Exception(f"Variable '{node.obj_name}' is not a struct at line {node.line}")
            if node.field not in obj.fields:
                raise Exception(f"Field '{node.field}' not found in struct '{obj.struct_name}' at line {node.line}")
            value = obj.fields[node.field]
            if self.verbose:
                logging.debug(f"Field value: {value} at line {node.line}")
            return float(value) if isinstance(value, (int, float)) else value
        elif isinstance(node, PrintNode):
            value = self.evaluate(node.expr)
            self.printed_values.append(str(value))
            return value
        elif isinstance(node, DeleteNode):
            if node.var_name in self.variables:
                self.variables[node.var_name]['deleted'] = True
            return None
        elif isinstance(node, ParallelNode):
            executor = ParallelExecutor(self, node.block)
            with ThreadPoolExecutor() as pool:
                pool.submit(executor.execute)
            return None
        elif isinstance(node, InputNode):
            if self.input_value is None:
                raise InputRequired(node.line)
            value = self.input_value
            self.input_value = None
            try:
                return float(value)
            except ValueError:
                return value
        elif isinstance(node, ReturnNode):
            return self.evaluate(node.expr) if node.expr else None
        raise Exception(f"Unknown node type {type(node).__name__} at line {node.line}")