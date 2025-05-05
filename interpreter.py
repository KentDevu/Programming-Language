import logging
from typing import Any, List, Optional
from nodes import *
from token_type import TokenType
from function import Function
from structs import StructDef, StructInstance
from concurrent.futures import ThreadPoolExecutor

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
        if verbose:
            logging.basicConfig(level=logging.DEBUG)

    def evaluate(self, node: Node) -> Any:
        if self.verbose:
            logging.debug(f"Evaluating {type(node).__name__}")
        
        if isinstance(node, NumberNode):
            return node.value
        elif isinstance(node, StringNode):
            return node.value
        elif isinstance(node, BoolNode):
            return node.value
        elif isinstance(node, NullNode):
            return None
        elif isinstance(node, VarNode):
            if node.name in self.variables and not self.variables[node.name].get('deleted', False):
                return self.variables[node.name]['value']
            raise Exception(f"Access to undefined or deleted variable '{node.name}' at line {node.line}")
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
                self.evaluate(node.update)
                if result is not None and isinstance(result, ReturnNode):
                    return self.evaluate(result.expr) if result.expr else None
            return None
        elif isinstance(node, WhileNode):
            while True:
                condition = self.evaluate(node.condition)
                if not isinstance(condition, bool):
                    raise Exception(f"Condition must be boolean at line {node.line}")
                if not condition:
                    break
                result = self.evaluate(node.body)
                if result is not None and isinstance(result, ReturnNode):
                    return self.evaluate(result.expr) if result.expr else None
            return None
        elif isinstance(node, BlockNode):
            result = None
            for stmt in node.statements:
                result = self.evaluate(stmt)
                if isinstance(result, ReturnNode):
                    return self.evaluate(result.expr) if result.expr else None
            return result
        elif isinstance(node, FunctionCallNode):
            fname = node.fname
            if fname in self.structs:
                struct_def = self.structs[fname]
                args = [self.evaluate(arg) for arg in node.args]
                if len(args) == 0 and len(struct_def.fields) > 0:
                    fields = {field: None for field in struct_def.fields}
                elif len(struct_def.fields) != len(args):
                    raise Exception(f"Struct '{fname}' expects {len(struct_def.fields)} fields, got {len(args)} at line {node.line}")
                else:
                    fields = {field: arg for field, arg in zip(struct_def.fields, args)}
                return StructInstance(fname, fields)
            if fname not in self.functions:
                if '.' in fname:
                    obj_name, method_name = fname.split('.')
                    if obj_name in self.variables:
                        obj = self.variables[obj_name]['value']
                        if isinstance(obj, StructInstance) and f"{obj.struct_name}.{method_name}" in self.functions:
                            fname = f"{obj.struct_name}.{method_name}"
                        else:
                            raise Exception(f"Invalid method call '{fname}' at line {node.line}")
                    else:
                        raise Exception(f"Undefined object '{obj_name}' at line {node.line}")
                else:
                    if fname in self.variables and callable(self.variables[fname]['value']):
                        func = self.variables[fname]['value']
                        args = [self.evaluate(arg) for arg in node.args]
                        return func(*args)
                    raise Exception(f"Undefined function '{fname}' at line {node.line}")
            func = self.functions[fname]
            args = [self.evaluate(arg) for arg in node.args]
            if len(func.params) != len(args):
                raise Exception(f"Function '{fname}' expects {len(func.params)} arguments, got {len(args)} at line {node.line}")
            
            saved_vars = self.variables.copy()
            for param, arg in zip(func.params, args):
                self.variables[param] = {'value': arg, 'deleted': False}
            
            result = self.evaluate(func.body)
            if isinstance(result, ReturnNode):
                result = self.evaluate(result.expr) if result.expr else None
            
            self.variables = saved_vars
            return result
        elif isinstance(node, LambdaNode):
            def lambda_func(*args):
                if len(node.params) != len(args):
                    raise Exception(f"Lambda expects {len(node.params)} arguments, got {len(args)} at line {node.line}")
                saved_vars = self.variables.copy()
                for param, arg in zip(node.params, args):
                    self.variables[param] = {'value': arg, 'deleted': False}
                result = self.evaluate(node.body)
                self.variables = saved_vars
                return result
            return lambda_func
        elif isinstance(node, ArrayNode):
            return [self.evaluate(elem) for elem in node.elements]
        elif isinstance(node, StructInitNode):
            if node.struct_name not in self.structs:
                raise Exception(f"Undefined struct '{node.struct_name}' at line {node.line}")
            struct_def = self.structs[node.struct_name]
            args = [self.evaluate(arg) for arg in node.args]
            if len(args) == 0 and len(struct_def.fields) > 0:
                fields = {field: None for field in struct_def.fields}
            elif len(struct_def.fields) != len(args):
                raise Exception(f"Struct '{node.struct_name}' expects {len(struct_def.fields)} fields, got {len(args)} at line {node.line}")
            else:
                fields = {field: arg for field, arg in zip(struct_def.fields, args)}
            return StructInstance(node.struct_name, fields)
        elif isinstance(node, FieldAccessNode):
            if node.obj_name not in self.variables:
                raise Exception(f"Undefined variable '{node.obj_name}' at line {node.line}")
            obj = self.variables[node.obj_name]['value']
            if not isinstance(obj, StructInstance):
                raise Exception(f"Variable '{node.obj_name}' is not a struct at line {node.line}")
            if node.field not in obj.fields:
                raise Exception(f"Field '{node.field}' not found in struct '{obj.struct_name}' at line {node.line}")
            return obj.fields[node.field]
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
            return input("Input: ")
        elif isinstance(node, ReturnNode):
            return self.evaluate(node.expr) if node.expr else None
        raise Exception(f"Unknown node type {type(node).__name__} at line {node.line}")