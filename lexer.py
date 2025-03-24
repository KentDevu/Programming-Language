from typing import Any
from token_type import TokenType
from tokens import Token

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
            
        return Token(TokenType.NUMBER, float(result), self.line, self.column - len(result))

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