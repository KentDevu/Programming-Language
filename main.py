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
    print("7. Struct definitions: STRUCT ObjFac { x, y }")
    print("8. Struct usage: ObjFac obj = ObjFac(3, 4); obj.x")
    print("9. Print statements: PRINT(expr)")
    print("10. Enter 'quit' to exit")
    print("Test Cases to Try")
    print("-----------------")
    print("1. Function Parameters & Return Values:")
    print("   - DEF add(a, b) RETURN a + b; add(3, 4)  # Expected: 7.0")
    print("   - DEF square(x) RETURN x * x; square(5)  # Expected: 25.0")
    print("   - DEF greet(name) RETURN 'Hello, ' + name; greet('Alice')  # Expected: 'Hello, Alice'")
    print()
    print("2. Logical Operators:")
    print("   - TRUE AND FALSE  # Expected: False")
    print("   - TRUE OR FALSE   # Expected: True")
    print("   - NOT TRUE        # Expected: False")
    print("   - (3 > 2) AND (5 < 10)  # Expected: True")
    print("   - (3 > 5) OR (5 < 10)   # Expected: True")
    print()
    print("3. User-Defined Data Types (Structs):")
    print("   - STRUCT Point { x, y }; Point p = Point(3, 4); p.x  # Expected: 3.0")
    print("   - STRUCT Person { name, age }; Person p = Person('Alice', 30); p.age  # Expected: 30.0")
    print("   - STRUCT Rectangle { width, height }; Rectangle r = Rectangle(5, 10); r.width * r.height  # Expected: 50.0")
    print()
    print("4. Enhanced Control Structures:")
    print("   - FOR (i = 0; i < 3; i = i + 1) { PRINT(i) }  # Expected: Printed: 0.0, 1.0, 2.0")
    print("   - IF (5 > 3) { PRINT('Yes') } ELSE { PRINT('No') }  # Expected: Printed: 'Yes'")
    print("   - IF (3 > 5) { PRINT('Yes') } ELSE { PRINT('No') }  # Expected: Printed: 'No'")
    print()
    print("5. Error Handling:")
    print("   - PRINT(undefinedVar)  # Expected: Error: Undefined variable 'undefinedVar'")
    print("   - add(1)  # Expected: Error: Function 'add' expects 2 arguments, got 1")
    print("   - IF (5 > 3 { PRINT('error') }  # Expected: Error: Invalid syntax (missing parenthesis)")
    print()
    print("Notes: Use ';' to separate statements. Enter 'quit' to exit.")
    print("Enter your expression:")

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