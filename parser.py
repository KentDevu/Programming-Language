"""
<program> ::= <statement_list>

<statement_list> ::= <statement> ";" <statement_list> | ε

<statement> ::= <assign_stmt>
              | <print_stmt>
              | <if_stmt>
              | <for_stmt>
              | <function_def>
              | <struct_def>
              | <expr>

<assign_stmt> ::= <id> "=" <logical_expr>

<print_stmt> ::= "PRINT" "(" <logical_expr> ")"

<if_stmt> ::= "IF" "(" <logical_expr> ")" "{" <statement_list> "}" "ELSE" "{" <statement_list> "}"

<for_stmt> ::= "FOR" "(" <assign_stmt> ";" <logical_expr> ";" <assign_stmt> ")" "{" <statement_list> "}"

<function_def> ::= "DEF" <id> "(" <param_list> ")" "RETURN" <logical_expr>
                 | "DEF" <id> "(" <param_list> ")" "{" "RETURN" <logical_expr> ";" "}"

<param_list> ::= <id> "," <param_list> | <id> | ε

<struct_def> ::= "STRUCT" <id> "{" <field_list> "}" ";"

<field_list> ::= <id> "," <field_list> | <id> | ε

<logical_expr> ::= "NOT" <logical_expr>
                 | <compare_expr> "AND" <compare_expr>
                 | <compare_expr> "OR" <compare_expr>
                 | <compare_expr>

<compare_expr> ::= <expr> "==" <expr>
                 | <expr> "!=" <expr>
                 | <expr> "<" <expr>
                 | <expr> ">" <expr>
                 | <expr> "<=" <expr>
                 | <expr> ">=" <expr>
                 | <expr>

<expr> ::= <term> "+" <term>
         | <term> "-" <term>
         | <term>

<term> ::= <factor> "*" <factor>
         | <factor> "/" <factor>
         | <factor> "%" <factor>
         | <factor> "^" <factor>
         | <factor>

<factor> ::= "+" <factor>
           | "-" <factor>
           | <atom>

<atom> ::= <number>
         | <string>
         | "TRUE"
         | "FALSE"
         | <id>
         | <id> "(" <arg_list> ")"  // Function call or struct init
         | <id> "." <id>           // Field access
         | "(" <logical_expr> ")"

<arg_list> ::= <expr> "," <arg_list> | <expr> | ε

<number> ::= digit+ | digit+ "." digit* | "." digit+

<string> ::= "'" char* "'"

<id> ::= letter (letter | digit | "_")*

<digit> ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

<letter> ::= "a" | "b" | ... | "z" | "A" | "B" | ... | "Z"

<char> ::= any_character_except_quote
"""
from enum import Enum
from typing import Any, List, Optional, Dict, Tuple
import math

# Token types for our language
class TokenType(Enum):
    IF = 'IF'
    ELSE = 'ELSE'
    FOR = 'FOR'
    DEF = 'DEF'
    RETURN = 'RETURN'
    STRUCT = 'STRUCT'
    PRINT = 'PRINT'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    EQUAL = 'EQUAL'
    NOT_EQUAL = 'NOT_EQUAL'
    LESS = 'LESS'
    GREATER = 'GREATER'
    LESS_EQUAL = 'LESS_EQUAL'
    GREATER_EQUAL = 'GREATER_EQUAL'
    ASSIGN = 'ASSIGN'  # =
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    EXPONENTIATION = 'EXPONENTIATION'
    MODULUS = 'MODULUS'
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    ID = 'ID'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACE = 'LBRACE'
    RBRACE = 'RBRACE'
    DOT = 'DOT'
    COMMA = 'COMMA'
    SEMICOLON = 'SEMICOLON'
    EOF = 'EOF'

class Token:
    def __init__(self, type: TokenType, value: Any, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        return f'Token({self.type}, {self.value}, pos={self.line}:{self.column})'

# AST Node Types
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
    def __init__(self, condition: Node, then_block: Node, else_block: Node):
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

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None
        self.line = 1
        self.column = 1
        
        self.keywords = {
            'IF': TokenType.IF,
            'ELSE': TokenType.ELSE,
            'FOR': TokenType.FOR,
            'DEF': TokenType.DEF,
            'RETURN': TokenType.RETURN,
            'STRUCT': TokenType.STRUCT,
            'PRINT': TokenType.PRINT,
            'TRUE': TokenType.TRUE,
            'FALSE': TokenType.FALSE,
            'AND': TokenType.AND,
            'OR': TokenType.OR,
            'NOT': TokenType.NOT,
            'function': TokenType.DEF,
            'return': TokenType.RETURN,
            'struct': TokenType.STRUCT,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'for': TokenType.FOR,
            'print': TokenType.PRINT,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT
        }

    def error(self, message: str = "Invalid character"):
        raise Exception(f'{message} at line {self.line}, column {self.column}')

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 0
        self.pos += 1
        self.column += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char and self.current_char != '\n':
            self.advance()
        self.advance()

    def number(self) -> Token:
        result = ''
        decimal_point_count = 0
        
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                decimal_point_count += 1
                if decimal_point_count > 1:
                    self.error("Too many decimal points in number")
            result += self.current_char
            self.advance()
            
        if result.startswith('.'):
            result = '0' + result
        if result.endswith('.'):
            result += '0'
            
        return Token(
            TokenType.NUMBER,
            float(result),
            self.line,
            self.column - len(result)
        )

    def string(self) -> Token:
        self.advance()  # Skip opening quote
        result = ''
        while self.current_char and self.current_char != "'":
            result += self.current_char
            self.advance()
        if not self.current_char:
            self.error("Unterminated string")
        self.advance()  # Skip closing quote
        return Token(TokenType.STRING, result, self.line, self.column - len(result) - 2)

    def _id(self) -> Token:
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
            
        token_type = self.keywords.get(result)
        if token_type:
            return Token(token_type, result, self.line, self.column - len(result))
        return Token(TokenType.ID, result, self.line, self.column - len(result))

    def get_next_token(self) -> Token:
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '#':
                self.skip_comment()
                continue

            if self.current_char == '.':
                self.advance()
                return Token(TokenType.DOT, '.', self.line, self.column - 1)

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == "'":
                return self.string()

            if self.current_char.isalpha():
                return self._id()

            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+', self.line, self.column - 1)

            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-', self.line, self.column - 1)

            if self.current_char == '*':
                self.advance()
                return Token(TokenType.MULTIPLY, '*', self.line, self.column - 1)

            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIVIDE, '/', self.line, self.column - 1)

            if self.current_char == '^':
                self.advance()
                return Token(TokenType.EXPONENTIATION, '^', self.line, self.column - 1)

            if self.current_char == '%':
                self.advance()
                return Token(TokenType.MODULUS, '%', self.line, self.column - 1)

            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(', self.line, self.column - 1)

            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')', self.line, self.column - 1)

            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LBRACE, '{', self.line, self.column - 1)

            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RBRACE, '}', self.line, self.column - 1)

            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',', self.line, self.column - 1)

            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';', self.line, self.column - 1)

            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.EQUAL, '==', self.line, self.column - 2)
                return Token(TokenType.ASSIGN, '=', self.line, self.column - 1)

            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.NOT_EQUAL, '!=', self.line, self.column - 2)
                self.error("Expected '!=' after '!'")

            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.LESS_EQUAL, '<=', self.line, self.column - 2)
                return Token(TokenType.LESS, '<', self.line, self.column - 1)

            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.GREATER_EQUAL, '>=', self.line, self.column - 2)
                return Token(TokenType.GREATER, '>', self.line, self.column - 1)

            self.error(f"Invalid character '{self.current_char}'")

        return Token(TokenType.EOF, None, self.line, self.column)

class Function:
    def __init__(self, params: List[str], body: Node):
        self.params = params
        self.body = body

class StructDef:
    def __init__(self, fields: List[str]):
        self.fields = fields

class StructInstance:
    def __init__(self, struct_name: str, field_values: Dict[str, Any]):
        self.struct_name = struct_name
        self.fields = field_values

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
            else:
                return self.evaluate(node.else_block)
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

def interactive_test():
    print("Expression Parser Test Interface")
    print("===============================")
    print("Supported operations:")
    print("1. Arithmetic: +, -, *, /, ^, %")
    print("2. Logical: AND, OR, NOT")
    print("3. Comparison: ==, !=, <, >, <=, >=")
    print("4. IF-ELSE statements: IF (cond) { stmts } ELSE { stmts }")
    print("5. FOR loops: FOR (i = 0; i < 5; i = i + 1) { stmts }")
    print("6. Function definitions: DEF fname(x, y) RETURN expr")
    print("7. Struct definitions: STRUCT Point { x, y }")
    print("8. Struct usage: Point p = Point(3, 4); p.x")
    print("9. Print statements: PRINT(expr)")
    print("10. Enter 'quit' to exit")
    print("\nExample expressions:")
    print("- 3 + 4 * 2")
    print("- 'Hello' + ', World'")
    print("- TRUE AND FALSE")
    print("- IF (5 > 3) { PRINT('Yes') } ELSE { PRINT('No') }")
    print("- FOR (i = 0; i < 3; i = i + 1) { PRINT(i) }")
    print("- DEF add(x, y) RETURN x + y")
    print("- add(3, 4)")
    print("- STRUCT Point { x, y }")
    print("- Point p = Point(3, 4); p.x")
    print("\nEnter your expression (use ';' to separate statements, 'quit' to exit):")

    interpreter = Interpreter()

    while True:
        try:
            line = input("> ")
            if line.lower() == 'quit':
                print("Goodbye!")
                break

            cleaned_line = line.lstrip('>').strip()
            if not cleaned_line:
                continue

            lexer = Lexer(cleaned_line)
            parser = Parser(lexer)
            
            parser.functions = interpreter.functions.copy()
            parser.structs = interpreter.structs.copy()
            parser.variables = interpreter.variables.copy()
            
            statements = parser.parse()
            
            interpreter.functions.update(parser.functions)
            interpreter.structs.update(parser.structs)
            interpreter.variables.update(parser.variables)
            
            for stmt in statements:
                result = interpreter.evaluate(stmt)
                if interpreter.printed_values:
                    for val in interpreter.printed_values:
                        print(f"Printed: {val}")
                    interpreter.printed_values.clear()
                elif result is not None and not isinstance(stmt, AssignNode):
                    print(f"Result: {result}")

        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    interactive_test()