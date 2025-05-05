from tokens import Token
from token_type import TokenType
import logging

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[0] if self.text else None

    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 0
        self.pos += 1
        self.column += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        if self.current_char == '\n':
            self.advance()

    def get_number(self):
        result = ''
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if result.count('.') > 1:
                raise Exception(f"Invalid number format at line {self.line}, column {self.column}")
            result += self.current_char
            self.advance()
        try:
            return float(result)
        except ValueError:
            raise Exception(f"Invalid number format at line {self.line}, column {self.column}")

    def get_string(self):
        result = ''
        quote_type = self.current_char  # Capture ' or "
        self.advance()  # Skip opening quote
        while self.current_char is not None and self.current_char != quote_type:
            result += self.current_char
            self.advance()
        if self.current_char != quote_type:
            raise Exception(f"Unterminated string at line {self.line}, column {self.column}")
        self.advance()  # Skip closing quote
        return result

    def get_id(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result

    def get_next_token(self):
        while self.current_char is not None:
            self.skip_whitespace()

            if self.current_char is None:
                break

            if self.current_char == '/' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '/':
                self.advance()
                self.advance()
                self.skip_comment()
                continue

            if self.current_char.isdigit() or self.current_char == '.':
                value = self.get_number()
                token = Token(TokenType.NUMBER, value, self.line, self.column)
                logging.debug(f"Token: {token}")
                return token

            if self.current_char in ("'", '"'):
                value = self.get_string()
                token = Token(TokenType.STRING, value, self.line, self.column)
                logging.debug(f"Token: {token}")
                return token

            if self.current_char.isalpha() or self.current_char == '_':
                value = self.get_id()
                if value == 'if':
                    token = Token(TokenType.IF, value, self.line, self.column)
                elif value == 'else':
                    token = Token(TokenType.ELSE, value, self.line, self.column)
                elif value == 'for':
                    token = Token(TokenType.FOR, value, self.line, self.column)
                elif value == 'while':
                    token = Token(TokenType.WHILE, value, self.line, self.column)
                elif value == 'def':
                    token = Token(TokenType.DEF, value, self.line, self.column)
                elif value == 'return':
                    token = Token(TokenType.RETURN, value, self.line, self.column)
                elif value == 'struct':
                    token = Token(TokenType.STRUCT, value, self.line, self.column)
                elif value == 'class':
                    token = Token(TokenType.CLASS, value, self.line, self.column)
                elif value == 'print':
                    token = Token(TokenType.PRINT, value, self.line, self.column)
                elif value == 'true':
                    token = Token(TokenType.TRUE, value, self.line, self.column)
                elif value == 'false':
                    token = Token(TokenType.FALSE, value, self.line, self.column)
                elif value == 'and':
                    token = Token(TokenType.AND, value, self.line, self.column)
                elif value == 'or':
                    token = Token(TokenType.OR, value, self.line, self.column)
                elif value == 'not':
                    token = Token(TokenType.NOT, value, self.line, self.column)
                elif value == 'null':
                    token = Token(TokenType.NULL, None, self.line, self.column)
                elif value == 'delete':
                    token = Token(TokenType.DELETE, value, self.line, self.column)
                elif value == 'parallel':
                    token = Token(TokenType.PARALLEL, value, self.line, self.column)
                elif value == 'input':
                    token = Token(TokenType.INPUT, value, self.line, self.column)
                else:
                    token = Token(TokenType.ID, value, self.line, self.column)
                logging.debug(f"Token: {token}")
                return token

            if self.current_char == '=' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '=':
                self.advance()
                self.advance()
                token = Token(TokenType.EQUAL, '==', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == '!' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '=':
                self.advance()
                self.advance()
                token = Token(TokenType.NOT_EQUAL, '!=', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == '<' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '=':
                self.advance()
                self.advance()
                token = Token(TokenType.LESS_EQUAL, '<=', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == '>' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '=':
                self.advance()
                self.advance()
                token = Token(TokenType.GREATER_EQUAL, '>=', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == '-':
                self.advance()
                if self.current_char == '>':
                    self.advance()
                    token = Token(TokenType.ARROW, '->', self.line, self.column)
                    logging.debug(f"Token: {token}")
                    return token
                token = Token(TokenType.MINUS, '-', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == '=':
                self.advance()
                token = Token(TokenType.ASSIGN, '=', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == '+':
                self.advance()
                token = Token(TokenType.PLUS, '+', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == '*':
                self.advance()
                token = Token(TokenType.MULTIPLY, '*', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == '/':
                self.advance()
                token = Token(TokenType.DIVIDE, '/', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == '^':
                self.advance()
                token = Token(TokenType.EXPONENTIATION, '^', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == '%':
                self.advance()
                token = Token(TokenType.MODULUS, '%', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == '<':
                self.advance()
                token = Token(TokenType.LESS, '<', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == '>':
                self.advance()
                token = Token(TokenType.GREATER, '>', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == '(':
                self.advance()
                token = Token(TokenType.LPAREN, '(', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == ')':
                self.advance()
                token = Token(TokenType.RPAREN, ')', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == '{':
                self.advance()
                token = Token(TokenType.LBRACE, '{', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == '}':
                self.advance()
                token = Token(TokenType.RBRACE, '}', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == '.':
                self.advance()
                token = Token(TokenType.DOT, '.', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == ',':
                self.advance()
                token = Token(TokenType.COMMA, ',', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token
            if self.current_char == ';':
                self.advance()
                token = Token(TokenType.SEMICOLON, ';', self.line, self.column)
                logging.debug(f"Token: {token}")
                return token

            raise Exception(f"Invalid character '{self.current_char}' at line {self.line}, column {self.column}")

        token = Token(TokenType.EOF, None, self.line, self.column)
        logging.debug(f"Token: {token}")
        return token