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
import argparse
import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from nodes import AssignNode

def interactive_test(verbose: bool = False):
    print("Toy Language Interpreter")
    print("=======================")
    print("Supported operations:")
    print("1. Arithmetic: +, -, *, /, ^, %")
    print("2. Logical: AND, OR, NOT")
    print("3. Comparison: ==, !=, <, >, <=, >=")
    print("4. Control: IF, FOR, WHILE")
    print("5. Functions: DEF fname(x, y) { RETURN expr; }")
    print("6. Structs: STRUCT Obj { x, y }; Obj o = Obj(3, 4); o.x")
    print("7. Classes: CLASS Person { name; DEF greet() { PRINT('Hello'); } }")
    print("8. Lambdas: (x, y) -> x + y")
    print("9. Arrays: {1, 2, 3}")
    print("10. Parallel: PARALLEL { PRINT(1); }")
    print("11. Input/Output: PRINT(expr), INPUT()")
    print("12. Memory: NULL, DELETE(x)")
    print("13. Enter 'quit' to exit")
    print("Enter your expression:")

    interpreter = Interpreter(verbose=verbose)
    input_buffer = []
    brace_count = 0

    while True:
        try:
            line = input("> ")
            if line.lower() == 'quit':
                print("Goodbye!")
                break

            cleaned_line = line.lstrip('>').strip()
            if not cleaned_line:
                continue

            input_buffer.append(cleaned_line)
            brace_count += cleaned_line.count('{') - cleaned_line.count('}')
            
            if brace_count == 0 and (cleaned_line.endswith(';') or not any(c in cleaned_line for c in '{}') or '}' in cleaned_line):
                code = '\n'.join(input_buffer)
                if verbose:
                    print(f"DEBUG: Processing code:\n{code}")
                input_buffer = []
                
                lexer = Lexer(code)
                parser = Parser(lexer, verbose=verbose)
                
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
                            print(val)
                        interpreter.printed_values.clear()
                    elif result is not None and not isinstance(stmt, AssignNode):
                        print(result)

        except Exception as e:
            print(f"Error: {str(e)}")
            input_buffer = []
            brace_count = 0

def run_file(filename: str, verbose: bool = False, debug: bool = False):
    try:
        with open(filename, 'r') as f:
            code = f.read()
        
        interpreter = Interpreter(verbose=verbose)
        lexer = Lexer(code)
        parser = Parser(lexer, verbose=verbose)
        
        parser.functions = interpreter.functions.copy()
        parser.structs = interpreter.structs.copy()
        parser.variables = interpreter.variables.copy()
        
        statements = parser.parse()
        
        interpreter.functions.update(parser.functions)
        interpreter.structs.update(parser.structs)
        interpreter.variables.update(parser.variables)
        
        for stmt in statements:
            interpreter.evaluate(stmt)
            if interpreter.printed_values:
                for val in interpreter.printed_values:
                    print(val)
                interpreter.printed_values.clear()

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Toy Language Interpreter",
        epilog="If no filename is provided, enters interactive mode. Use --help for more information."
    )
    parser.add_argument('filename', nargs='?', help="Script file to run")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose logging")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    
    args = parser.parse_args()

    if args.filename:
        run_file(args.filename, verbose=args.verbose, debug=args.debug)
    else:
        interactive_test(verbose=args.verbose)

if __name__ == "__main__":
    main()