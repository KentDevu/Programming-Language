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
from flask import Flask, request, jsonify, render_template
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from nodes import AssignNode

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # Serve the HTML page

@app.route('/run', methods=['POST'])
def run_code():
    data = request.get_json()
    code = data.get('code', '')

    if not code:
        return jsonify({'error': 'No code provided'}), 400

    try:
        interpreter = Interpreter(verbose=False)
        lexer = Lexer(code)
        parser = Parser(lexer, verbose=False)

        # Initialize functions, structs, and variables from the interpreter
        parser.functions = interpreter.functions.copy()
        parser.structs = interpreter.structs.copy()
        parser.variables = interpreter.variables.copy()

        # Parse the statements
        statements = parser.parse()

        # Update interpreter with new functions, structs, and variables
        interpreter.functions.update(parser.functions)
        interpreter.structs.update(parser.structs)
        interpreter.variables.update(parser.variables)

        # Execute the statements
        output = []
        for stmt in statements:
            result = interpreter.evaluate(stmt)
            if interpreter.printed_values:
                output.extend(interpreter.printed_values)
                interpreter.printed_values.clear()
            elif result is not None and not isinstance(stmt, AssignNode):
                output.append(result)

        return jsonify({'output': '\n'.join(str(item) for item in output)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
