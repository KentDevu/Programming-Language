from typing import List
from lexer import Lexer
from nodes import *
from token_type import TokenType
from function import Function
from structs import StructDef
import logging

class Parser:
    def __init__(self, lexer: Lexer, verbose: bool = False):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.functions: dict = {}
        self.structs: dict = {}
        self.variables: dict = {}
        self.verbose = verbose
        if self.verbose:
            logging.basicConfig(level=logging.DEBUG)
            self.log_token_stream()

    def log_token_stream(self):
        tokens = []
        temp_pos = self.lexer.pos
        temp_line = self.lexer.line
        temp_column = self.lexer.column
        temp_char = self.lexer.current_char
        temp_token = self.current_token

        while temp_token.type != TokenType.EOF:
            tokens.append(temp_token)
            temp_token = self.lexer.get_next_token()

        logging.debug(f"Token Stream: {tokens}")

        self.lexer.pos = temp_pos
        self.lexer.line = temp_line
        self.lexer.column = temp_column
        self.lexer.current_char = temp_char
        self.current_token = temp_token

    def log_ast(self, node: Node):
        if self.verbose:
            logging.debug(f"AST Node: {type(node).__name__}")

    def eat(self, token_type: TokenType):
        if self.current_token.type == token_type:
            if self.verbose:
                logging.debug(f"Consuming token: {self.current_token}")
            self.current_token = self.lexer.get_next_token()
        else:
            logging.error(f"Token mismatch: Expected {token_type}, got {self.current_token.type} (value: {self.current_token.value}, token: {self.current_token})")
            raise Exception(f"Expected {token_type}, got {self.current_token.type} (value: {self.current_token.value}) at line {self.current_token.line}, column {self.current_token.column}")

    def parse(self) -> List[Node]:
        statements = []
        while self.current_token.type != TokenType.EOF:
            stmt = self.statement()
            statements.append(stmt)
            self.log_ast(stmt)
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
        return statements

    def statement(self) -> Node:
        if self.current_token.type == TokenType.DEF:
            return self.function_def()
        elif self.current_token.type == TokenType.STRUCT:
            return self.struct_def()
        elif self.current_token.type == TokenType.CLASS:
            return self.class_def()
        elif self.current_token.type == TokenType.IF:
            return self.if_stmt()
        elif self.current_token.type == TokenType.FOR:
            return self.for_stmt()
        elif self.current_token.type == TokenType.WHILE:
            return self.while_stmt()
        elif self.current_token.type == TokenType.PRINT:
            return self.print_stmt()
        elif self.current_token.type == TokenType.DELETE:
            return self.delete_stmt()
        elif self.current_token.type == TokenType.PARALLEL:
            return self.parallel_stmt()
        elif self.current_token.type == TokenType.RETURN:
            return self.return_stmt()
        elif self.current_token.type == TokenType.ID and self.current_token.value == 'let':
            return self.let_stmt()
        elif self.current_token.type == TokenType.ID:
            return self.assign_or_call()
        elif self.current_token.type == TokenType.INPUT:
            return self.input_stmt()
        else:
            return self.expr()

    def assign_or_call(self) -> Node:
        line = self.current_token.line
        var_name = self.current_token.value
        if self.verbose:
            logging.debug(f"Processing ID: {var_name} at line {line}")
        self.eat(TokenType.ID)
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            value = self.expr()
            return AssignNode(var_name, value, line)
        elif self.current_token.type == TokenType.DOT:
            self.eat(TokenType.DOT)
            if self.current_token.type != TokenType.ID:
                raise Exception(f"Expected ID after DOT, got {self.current_token.type} at line {self.current_token.line}, column {self.current_token.column}")
            field = self.current_token.value
            field_line = self.current_token.line
            field_column = self.current_token.column
            self.eat(TokenType.ID)
            if self.current_token.type == TokenType.LPAREN:
                if self.verbose:
                    logging.debug(f"Creating FunctionCallNode for {var_name}.{field} at line {line}")
                return self.function_call(f"{var_name}.{field}", line)
            if self.verbose:
                logging.debug(f"Creating FieldAccessNode for {var_name}.{field} at line {line}")
            return FieldAccessNode(var_name, field, line)
        elif self.current_token.type == TokenType.LPAREN:
            return self.function_call(var_name, line)
        return VarNode(var_name, line)

    def function_def(self) -> Node:
        line = self.current_token.line
        self.eat(TokenType.DEF)
        fname = self.current_token.value
        self.eat(TokenType.ID)
        self.eat(TokenType.LPAREN)
        params = []
        if self.current_token.type != TokenType.RPAREN:
            params.append(self.current_token.value)
            self.eat(TokenType.ID)
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                params.append(self.current_token.value)
                self.eat(TokenType.ID)
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        body = self.block()
        self.eat(TokenType.RBRACE)
        self.functions[fname] = Function(params, body)
        return FunctionDefNode(fname, params, body, line)

    def struct_def(self) -> Node:
        line = self.current_token.line
        self.eat(TokenType.STRUCT)
        struct_name = self.current_token.value
        self.eat(TokenType.ID)
        self.eat(TokenType.LBRACE)
        fields = []
        if self.current_token.type != TokenType.RBRACE:
            fields.append(self.current_token.value)
            self.eat(TokenType.ID)
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                fields.append(self.current_token.value)
                self.eat(TokenType.ID)
        self.eat(TokenType.RBRACE)
        self.structs[struct_name] = StructDef(fields)
        return BlockNode([], line)

    def class_def(self) -> Node:
        line = self.current_token.line
        self.eat(TokenType.CLASS)
        class_name = self.current_token.value
        self.eat(TokenType.ID)
        self.eat(TokenType.LBRACE)
        fields = []
        methods = []
        while self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.DEF:
                method = self.function_def()
                methods.append(method)
                fname = method.fname
                self.functions[f"{class_name}.{fname}"] = self.functions[fname]
                del self.functions[fname]
            else:
                fields.append(self.current_token.value)
                self.eat(TokenType.ID)
                if self.current_token.type in [TokenType.SEMICOLON, TokenType.COMMA]:
                    self.eat(self.current_token.type)
        self.eat(TokenType.RBRACE)
        self.structs[class_name] = StructDef(fields)
        return BlockNode([], line)

    def if_stmt(self) -> Node:
        line = self.current_token.line
        self.eat(TokenType.IF)
        if self.current_token.type != TokenType.LPAREN:
            raise Exception(f"Expected TokenType.LPAREN, got {self.current_token.type} at line {self.current_token.line}, column {self.current_token.column}")
        self.eat(TokenType.LPAREN)
        condition = self.expr()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        then_block = self.block()
        self.eat(TokenType.RBRACE)
        else_block = None
        if self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            self.eat(TokenType.LBRACE)
            else_block = self.block()
            self.eat(TokenType.RBRACE)
        return IfNode(condition, then_block, else_block, line)

    def for_stmt(self) -> Node:
        line = self.current_token.line
        self.eat(TokenType.FOR)
        self.eat(TokenType.LPAREN)
        init = self.let_stmt() if self.current_token.value == 'let' else self.statement()
        self.eat(TokenType.SEMICOLON)
        condition = self.expr()
        self.eat(TokenType.SEMICOLON)
        update = self.statement()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        body = self.block()
        self.eat(TokenType.RBRACE)
        return ForNode(init, condition, update, body, line)

    def while_stmt(self) -> Node:
        line = self.current_token.line
        self.eat(TokenType.WHILE)
        self.eat(TokenType.LPAREN)
        condition = self.expr()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        body = self.block()
        self.eat(TokenType.RBRACE)
        return WhileNode(condition, body, line)

    def print_stmt(self) -> Node:
        line = self.current_token.line
        self.eat(TokenType.PRINT)
        self.eat(TokenType.LPAREN)
        expr = self.expr()
        self.eat(TokenType.RPAREN)
        return PrintNode(expr, line)

    def delete_stmt(self) -> Node:
        line = self.current_token.line
        self.eat(TokenType.DELETE)
        self.eat(TokenType.LPAREN)
        var_name = self.current_token.value
        self.eat(TokenType.ID)
        self.eat(TokenType.RPAREN)
        return DeleteNode(var_name, line)

    def parallel_stmt(self) -> Node:
        line = self.current_token.line
        self.eat(TokenType.PARALLEL)
        self.eat(TokenType.LBRACE)
        block = self.block()
        self.eat(TokenType.RBRACE)
        return ParallelNode(block, line)

    def return_stmt(self) -> Node:
        line = self.current_token.line
        self.eat(TokenType.RETURN)
        expr = self.expr() if self.current_token.type not in [TokenType.SEMICOLON, TokenType.RBRACE] else None
        return ReturnNode(expr, line)

    def let_stmt(self) -> Node:
        line = self.current_token.line
        self.eat(TokenType.ID)
        var_name = self.current_token.value
        self.eat(TokenType.ID)
        self.eat(TokenType.ASSIGN)
        if self.current_token.type == TokenType.INPUT:
            return AssignNode(var_name, self.input_stmt(), line)
        value = self.expr()
        return AssignNode(var_name, value, line)

    def input_stmt(self) -> Node:
        line = self.current_token.line
        self.eat(TokenType.INPUT)
        self.eat(TokenType.LPAREN)
        self.eat(TokenType.RPAREN)
        return InputNode(line)

    def block(self) -> Node:
        line = self.current_token.line
        statements = []
        while self.current_token.type not in [TokenType.RBRACE, TokenType.EOF]:
            stmt = self.statement()
            statements.append(stmt)
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
        return BlockNode(statements, line)

    def expr(self) -> Node:
        return self.logical_or()

    def logical_or(self) -> Node:
        node = self.logical_and()
        while self.current_token.type == TokenType.OR:
            line = self.current_token.line
            op = self.current_token.type
            self.eat(TokenType.OR)
            right = self.logical_and()
            if self.verbose:
                logging.debug(f"Creating LogicalNode with OR at line {line}")
            node = LogicalNode(op, node, right, line)
        return node

    def logical_and(self) -> Node:
        node = self.logical_not()
        while self.current_token.type == TokenType.AND:
            line = self.current_token.line
            op = self.current_token.type
            self.eat(TokenType.AND)
            right = self.logical_not()
            if self.verbose:
                logging.debug(f"Creating LogicalNode with AND at line {line}")
            node = LogicalNode(op, node, right, line)
        return node

    def logical_not(self) -> Node:
        line = self.current_token.line
        if self.current_token.type == TokenType.NOT:
            op = self.current_token.type
            self.eat(TokenType.NOT)
            operand = self.logical_not()
            if self.verbose:
                logging.debug(f"Creating UnaryOpNode with NOT at line {line}")
            return UnaryOpNode(op, operand, line)
        return self.equality()

    def equality(self) -> Node:
        node = self.comparison()
        while self.current_token.type in [TokenType.EQUAL, TokenType.NOT_EQUAL]:
            line = self.current_token.line
            op = self.current_token.type
            self.eat(op)
            right = self.comparison()
            if self.verbose:
                logging.debug(f"Creating CompareNode with {op} at line {line}")
            node = CompareNode(op, node, right, line)
        return node

    def comparison(self) -> Node:
        node = self.term()
        while self.current_token.type in [TokenType.LESS, TokenType.GREATER, TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL]:
            line = self.current_token.line
            op = self.current_token.type
            self.eat(op)
            right = self.term()
            if self.verbose:
                logging.debug(f"Creating CompareNode with {op} at line {line}")
            node = CompareNode(op, node, right, line)
        return node

    def term(self) -> Node:
        node = self.factor()
        while self.current_token.type in [TokenType.PLUS, TokenType.MINUS]:
            line = self.current_token.line
            op = self.current_token.type
            self.eat(op)
            right = self.factor()
            if self.verbose:
                logging.debug(f"Creating BinOpNode with {op} at line {line}")
            node = BinOpNode(op, node, right, line)
        return node

    def factor(self) -> Node:
        node = self.exponent()
        while self.current_token.type in [TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULUS]:
            line = self.current_token.line
            op = self.current_token.type
            self.eat(op)
            right = self.exponent()
            if self.verbose:
                logging.debug(f"Creating BinOpNode with {op} at line {line}")
            node = BinOpNode(op, node, right, line)
        return node

    def exponent(self) -> Node:
        node = self.unary()
        while self.current_token.type == TokenType.EXPONENTIATION:
            line = self.current_token.line
            op = self.current_token.type
            self.eat(TokenType.EXPONENTIATION)
            right = self.unary()
            if self.verbose:
                logging.debug(f"Creating BinOpNode with {op} at line {line}")
            node = BinOpNode(op, node, right, line)
        return node

    def unary(self) -> Node:
        line = self.current_token.line
        if self.current_token.type in [TokenType.PLUS, TokenType.MINUS]:
            op = self.current_token.type
            self.eat(op)
            operand = self.unary()
            if self.verbose:
                logging.debug(f"Creating UnaryOpNode with {op} at line {line}")
            return UnaryOpNode(op, operand, line)
        return self.primary()

    def primary(self) -> Node:
        token = self.current_token
        if self.verbose:
            logging.debug(f"Parsing primary token: {token}")
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            try:
                value = float(token.value)
                if self.verbose:
                    logging.debug(f"Created NumberNode: value={value}")
                return NumberNode(value, token.line)
            except ValueError:
                raise Exception(f"Invalid number format '{token.value}' at line {token.line}, column {token.column}")
        elif token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return StringNode(token.value, token.line)
        elif token.type == TokenType.TRUE:
            self.eat(TokenType.TRUE)
            return BoolNode(True, token.line)
        elif token.type == TokenType.FALSE:
            self.eat(TokenType.FALSE)
            return BoolNode(False, token.line)
        elif token.type == TokenType.NULL:
            self.eat(TokenType.NULL)
            return NullNode(token.line)
        elif token.type == TokenType.ID:
            var_name = token.value
            reserved_keywords = ['and', 'or', 'not', 'if', 'else', 'for', 'while', 'def', 'return', 'struct', 'class', 'print', 'true', 'false', 'null', 'delete', 'parallel', 'input']
            if var_name in reserved_keywords:
                raise Exception(f"Unexpected reserved keyword '{var_name}' used as identifier at line {token.line}, column {token.column}")
            self.eat(TokenType.ID)
            if self.current_token.type == TokenType.LPAREN:
                if self.verbose:
                    logging.debug(f"Creating FunctionCallNode for {var_name}")
                return self.function_call(var_name, token.line)
            elif self.current_token.type == TokenType.DOT:
                self.eat(TokenType.DOT)
                if self.current_token.type != TokenType.ID:
                    raise Exception(f"Expected ID after DOT, got {self.current_token.type} at line {self.current_token.line}, column {self.current_token.column}")
                field = self.current_token.value
                field_line = self.current_token.line
                field_column = self.current_token.column
                self.eat(TokenType.ID)
                if self.current_token.type == TokenType.LPAREN:
                    fname = f"{var_name}.{field}"
                    if self.verbose:
                        logging.debug(f"Creating FunctionCallNode for {fname} at line {token.line}")
                    return self.function_call(fname, token.line)
                if self.verbose:
                    logging.debug(f"Creating FieldAccessNode for {var_name}.{field} at line {token.line}")
                return FieldAccessNode(var_name, field, token.line)
            elif self.current_token.type == TokenType.LBRACE:
                return self.array_or_struct(var_name, token.line)
            if self.verbose:
                logging.debug(f"Creating VarNode for {var_name}")
            return VarNode(var_name, token.line)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            if self.current_token.type == TokenType.ID and self.current_token.value not in self.functions:
                return self.lambda_expr(token.line)
            expr = self.expr()
            self.eat(TokenType.RPAREN)
            return expr
        elif token.type == TokenType.LBRACE:
            return self.array_or_struct(None, token.line)
        elif token.type == TokenType.INPUT:
            return self.input_stmt()
        raise Exception(f"Unexpected token {token.type} at line {token.line}, column {token.column}")

    def function_call(self, fname: str, line: int) -> Node:
        if self.verbose:
            logging.debug(f"Processing function call: {fname} at line {line}")
        self.eat(TokenType.LPAREN)
        args = []
        if self.current_token.type != TokenType.RPAREN:
            args.append(self.expr())
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                args.append(self.expr())
        self.eat(TokenType.RPAREN)
        if fname in self.structs:
            if self.verbose:
                logging.debug(f"Creating StructInitNode for {fname} at line {line}")
            return StructInitNode(fname, args, line)
        if self.verbose:
            logging.debug(f"Created FunctionCallNode: fname={fname}, args={len(args)} at line {line}")
        return FunctionCallNode(fname, args, line)

    def lambda_expr(self, line: int) -> Node:
        params = []
        if self.current_token.type != TokenType.RPAREN:
            params.append(self.current_token.value)
            self.eat(TokenType.ID)
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                params.append(self.current_token.value)
                self.eat(TokenType.ID)
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.ARROW)
        body = self.expr()
        return LambdaNode(params, body, line)

    def array_or_struct(self, struct_name: str, line: int) -> Node:
        self.eat(TokenType.LBRACE)
        elements = []
        if self.current_token.type != TokenType.RBRACE:
            elements.append(self.expr())
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                elements.append(self.expr())
        self.eat(TokenType.RBRACE)
        if struct_name and struct_name in self.structs:
            return StructInitNode(struct_name, elements, line)
        return ArrayNode(elements, line)