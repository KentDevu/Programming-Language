from typing import List, Dict, Any, Optional
from token_type import TokenType
from nodes import *
from lexer import Lexer
from function import Function
from structs import StructDef

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.functions: Dict[str, Function] = {}
        self.structs: Dict[str, StructDef] = {}
        self.variables: Dict[str, Any] = {}

    def error(self, message: str = "Invalid syntax"):
        raise Exception(f'{message} at line {self.current_token.line}, column {self.current_token.column}')

    def eat(self, token_type: TokenType):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}, got {self.current_token.type}")

    def atom(self) -> Node:
        token = self.current_token
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return NumberNode(token.value)
        elif token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return StringNode(token.value)
        elif token.type == TokenType.TRUE:
            self.eat(TokenType.TRUE)
            return BoolNode(True)
        elif token.type == TokenType.FALSE:
            self.eat(TokenType.FALSE)
            return BoolNode(False)
        elif token.type == TokenType.ID:
            name = token.value
            self.eat(TokenType.ID)
            if self.current_token.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                args = []
                if self.current_token.type != TokenType.RPAREN:
                    args.append(self.expression())
                    while self.current_token.type == TokenType.COMMA:
                        self.eat(TokenType.COMMA)
                        args.append(self.expression())
                self.eat(TokenType.RPAREN)
                if name in self.structs:
                    return StructInitNode(name, args)
                return FunctionCallNode(name, args)
            elif self.current_token.type == TokenType.DOT:
                self.eat(TokenType.DOT)
                field = self.current_token.value
                self.eat(TokenType.ID)
                return FieldAccessNode(name, field)
            return VarNode(name)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            result = self.expression()
            self.eat(TokenType.RPAREN)
            return result
        self.error(f"Unexpected token {token.type}")

    def exponentiation(self) -> Node:
        node = self.atom()
        while self.current_token.type == TokenType.EXPONENTIATION:
            self.eat(TokenType.EXPONENTIATION)
            node = BinOpNode(node, TokenType.EXPONENTIATION, self.factor())
        return node

    def factor(self) -> Node:
        token = self.current_token
        if token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return UnaryOpNode(TokenType.PLUS, self.factor())
        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return UnaryOpNode(TokenType.MINUS, self.factor())
        return self.exponentiation()

    def term(self) -> Node:
        node = self.factor()
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULUS):
            token = self.current_token
            if token.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
                node = BinOpNode(node, TokenType.MULTIPLY, self.factor())
            elif token.type == TokenType.DIVIDE:
                self.eat(TokenType.DIVIDE)
                node = BinOpNode(node, TokenType.DIVIDE, self.factor())
            elif token.type == TokenType.MODULUS:
                self.eat(TokenType.MODULUS)
                node = BinOpNode(node, TokenType.MODULUS, self.factor())
        return node

    def expression(self) -> Node:
        node = self.term()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
                node = BinOpNode(node, TokenType.PLUS, self.term())
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
                node = BinOpNode(node, TokenType.MINUS, self.term())
        return node

    def comparison(self) -> Node:
        node = self.expression()
        while self.current_token.type in (TokenType.EQUAL, TokenType.NOT_EQUAL, 
                                        TokenType.LESS, TokenType.GREATER,
                                        TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            token = self.current_token
            if token.type == TokenType.EQUAL:
                self.eat(TokenType.EQUAL)
                node = CompareNode(node, TokenType.EQUAL, self.expression())
            elif token.type == TokenType.NOT_EQUAL:
                self.eat(TokenType.NOT_EQUAL)
                node = CompareNode(node, TokenType.NOT_EQUAL, self.expression())
            elif token.type == TokenType.LESS:
                self.eat(TokenType.LESS)
                node = CompareNode(node, TokenType.LESS, self.expression())
            elif token.type == TokenType.GREATER:
                self.eat(TokenType.GREATER)
                node = CompareNode(node, TokenType.GREATER, self.expression())
            elif token.type == TokenType.LESS_EQUAL:
                self.eat(TokenType.LESS_EQUAL)
                node = CompareNode(node, TokenType.LESS_EQUAL, self.expression())
            elif token.type == TokenType.GREATER_EQUAL:
                self.eat(TokenType.GREATER_EQUAL)
                node = CompareNode(node, TokenType.GREATER_EQUAL, self.expression())
        return node

    def logical_expr(self) -> Node:
        if self.current_token.type == TokenType.NOT:
            self.eat(TokenType.NOT)
            return NotNode(self.logical_expr())
        node = self.comparison()
        while self.current_token.type in (TokenType.AND, TokenType.OR):
            token = self.current_token
            if token.type == TokenType.AND:
                self.eat(TokenType.AND)
                node = LogicalNode(node, TokenType.AND, self.comparison())
            elif token.type == TokenType.OR:
                self.eat(TokenType.OR)
                node = LogicalNode(node, TokenType.OR, self.comparison())
        return node

    def assign_stmt(self) -> Node:
        var_name = self.current_token.value
        self.eat(TokenType.ID)
        self.eat(TokenType.ASSIGN)
        value = self.logical_expr()
        return AssignNode(var_name, value)

    def print_stmt(self) -> Node:
        self.eat(TokenType.PRINT)
        self.eat(TokenType.LPAREN)
        expr = self.logical_expr()
        self.eat(TokenType.RPAREN)
        return PrintNode(expr)

    def block(self) -> Node:
        statements = []
        while self.current_token.type != TokenType.RBRACE and self.current_token.type != TokenType.EOF:
            stmt = self.statement()
            if stmt is not None:
                statements.append(stmt)
        return BlockNode(statements)

    def if_stmt(self) -> Node:
        self.eat(TokenType.IF)
        self.eat(TokenType.LPAREN)
        condition = self.logical_expr()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        then_block = self.block()
        self.eat(TokenType.RBRACE)
        self.eat(TokenType.ELSE)
        self.eat(TokenType.LBRACE)
        else_block = self.block()
        self.eat(TokenType.RBRACE)
        return IfNode(condition, then_block, else_block)

    def for_loop(self) -> Node:
        self.eat(TokenType.FOR)
        self.eat(TokenType.LPAREN)
        init = self.assign_stmt()
        self.eat(TokenType.SEMICOLON)
        condition = self.logical_expr()
        self.eat(TokenType.SEMICOLON)
        update = self.assign_stmt()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LBRACE)
        body = self.block()
        self.eat(TokenType.RBRACE)
        return ForNode(init, condition, update, body)

    def function_def(self) -> None:
        self.eat(TokenType.DEF)
        func_name = self.current_token.value
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
        if self.current_token.type == TokenType.LBRACE:
            self.eat(TokenType.LBRACE)
            self.eat(TokenType.RETURN)
            body = self.logical_expr()
            self.eat(TokenType.SEMICOLON)
            self.eat(TokenType.RBRACE)
        else:
            self.eat(TokenType.RETURN)
            body = self.logical_expr()
        self.functions[func_name] = Function(params, body)

    def struct_def(self) -> None:
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
        if self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
        self.structs[struct_name] = StructDef(fields)

    def statement(self) -> Optional[Node]:
        if self.current_token.type == TokenType.DEF:
            self.function_def()
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
            return None
        elif self.current_token.type == TokenType.STRUCT:
            self.struct_def()
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
            return None
        elif self.current_token.type == TokenType.IF:
            stmt = self.if_stmt()
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
            return stmt
        elif self.current_token.type == TokenType.FOR:
            stmt = self.for_loop()
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
            return stmt
        elif self.current_token.type == TokenType.PRINT:
            stmt = self.print_stmt()
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
            return stmt
        elif self.current_token.type == TokenType.ID:
            first_id = self.current_token.value
            self.eat(TokenType.ID)
            if self.current_token.type == TokenType.ID:
                var_name = self.current_token.value
                self.eat(TokenType.ID)
                if self.current_token.type == TokenType.ASSIGN:
                    self.eat(TokenType.ASSIGN)
                    value = self.logical_expr()
                    if self.current_token.type == TokenType.SEMICOLON:
                        self.eat(TokenType.SEMICOLON)
                    return AssignNode(var_name, value)
                else:
                    self.error(f"Expected '=' after '{first_id} {var_name}'")
            elif self.current_token.type == TokenType.ASSIGN:
                self.eat(TokenType.ASSIGN)
                value = self.logical_expr()
                if self.current_token.type == TokenType.SEMICOLON:
                    self.eat(TokenType.SEMICOLON)
                return AssignNode(first_id, value)
            elif self.current_token.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                args = []
                if self.current_token.type != TokenType.RPAREN:
                    args.append(self.expression())
                    while self.current_token.type == TokenType.COMMA:
                        self.eat(TokenType.COMMA)
                        args.append(self.expression())
                self.eat(TokenType.RPAREN)
                node = FunctionCallNode(first_id, args)
                if self.current_token.type == TokenType.SEMICOLON:
                    self.eat(TokenType.SEMICOLON)
                return node
            elif self.current_token.type == TokenType.DOT:
                self.eat(TokenType.DOT)
                field = self.current_token.value
                self.eat(TokenType.ID)
                node = FieldAccessNode(first_id, field)
                if self.current_token.type == TokenType.SEMICOLON:
                    self.eat(TokenType.SEMICOLON)
                return node
            else:
                node = VarNode(first_id)
                if self.current_token.type == TokenType.SEMICOLON:
                    self.eat(TokenType.SEMICOLON)
                return node
        
        node = self.logical_expr()
        if self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
        return node

    def parse(self) -> List[Node]:
        statements = []
        while self.current_token.type != TokenType.EOF:
            stmt = self.statement()
            if stmt is not None:
                statements.append(stmt)
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
                if self.current_token.type == TokenType.EOF:  # Handle trailing semicolon
                    break
        return statements