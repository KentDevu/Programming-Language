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
import sys
import argparse
import logging
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import io
from contextlib import redirect_stdout, redirect_stderr

app = FastAPI(title="Toy Language Interpreter")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeInput(BaseModel):
    code: str

def run_interpreter(code: str, verbose: bool = False) -> str:
    output = io.StringIO()
    error_output = io.StringIO()
    
    try:
        lexer = Lexer(code)
        parser = Parser(lexer, verbose)
        interpreter = Interpreter(parser, verbose)
        
        with redirect_stdout(output), redirect_stderr(error_output):
            interpreter.interpret()
        
        result = output.getvalue()
        errors = error_output.getvalue()
        if errors:
            return errors
        return result if result else "No output"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        output.close()
        error_output.close()

@app.post("/run")
async def run_code(input: CodeInput):
    try:
        result = run_interpreter(input.code, verbose=False)
        return {"output": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})

def print_supported_operations():
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

def repl(verbose: bool):
    print_supported_operations()
    print("Enter your expression:")
    while True:
        try:
            code = input("> ")
            if code.lower() == 'quit':
                break
            if code.strip():
                result = run_interpreter(code + ";", verbose)
                print(result)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Toy Language Interpreter")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose logging")
    parser.add_argument('--server', action='store_true', help="Run as FastAPI server")
    args = parser.parse_args()

    if args.server:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        repl(args.verbose)