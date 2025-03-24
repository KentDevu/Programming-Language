"""
<program> ::= <statement_list>

<statement_list> ::= <statement> (";" <statement_list> | ε)

<statement> ::= <assign_stmt>
              | <print_stmt>
              | <if_stmt>
              | <for_stmt>
              | <function_def>
              | <struct_def>
              | <expr>

<assign_stmt> ::= <id> "=" <logical_expr>

<print_stmt> ::= "PRINT" "(" <logical_expr> ")"

<if_stmt> ::= "IF" "(" <logical_expr> ")" "{" <statement_list> "}" ("ELSE" "{" <statement_list> "}" | ε)

<for_stmt> ::= "FOR" "(" <assign_stmt> ";" <logical_expr> ";" <assign_stmt> ")" "{" <statement_list> "}"

<function_def> ::= "DEF" <id> "(" <param_list> ")" "RETURN" <logical_expr>
                 | "DEF" <id> "(" <param_list> ")" "{" "RETURN" <logical_expr> (";" | ε) "}"

<param_list> ::= <id> "," <param_list> | <id> | ε

<struct_def> ::= "STRUCT" <id> "{" <field_list> "}" (";" | ε)

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

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from nodes import AssignNode

def interactive_test():
    print("Expression Parser Test Interface")
    print("===============================")
    print("Supported operations:")
    print("1. Arithmetic: +, -, *, /, ^, %")
    print("2. Logical: AND, OR, NOT")
    print("3. Comparison: ==, !=, <, >, <=, >=")
    print("4. IF-ELSE statements: IF (cond) { stmts } [ELSE { stmts }]")
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