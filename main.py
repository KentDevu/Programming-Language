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
from interpreter import Interpreter, InputRequired
from nodes import AssignNode
import uuid

app = Flask(__name__)

# Store interpreter states by session ID
interpreter_states = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    data = request.get_json()
    code = data.get('code', '')
    session_id = data.get('session_id', str(uuid.uuid4()))  # Unique ID for each run

    if not code:
        return jsonify({'error': 'No code provided', 'session_id': session_id}), 400

    try:
        # Initialize or retrieve interpreter
        if session_id in interpreter_states:
            interpreter = interpreter_states[session_id]['interpreter']
            parser = interpreter_states[session_id]['parser']
            statements = interpreter_states[session_id]['statements']
            current_stmt = interpreter_states[session_id].get('current_stmt', 0)
        else:
            interpreter = Interpreter(verbose=False)
            lexer = Lexer(code)
            parser = Parser(lexer, verbose=False)
            # Synchronize parser and interpreter dictionaries
            interpreter.functions = parser.functions.copy()
            interpreter.structs = parser.structs.copy()
            statements = parser.parse()
            # Update interpreter dictionaries after parsing
            interpreter.functions.update(parser.functions)
            interpreter.structs.update(parser.structs)
            interpreter.variables = parser.variables.copy()
            current_stmt = 0

        output = []
        # Execute statements, handling input requests
        while current_stmt < len(statements):
            try:
                result = interpreter.evaluate(statements[current_stmt])
                if interpreter.printed_values:
                    output.extend(interpreter.printed_values)
                    interpreter.printed_values.clear()
                elif result is not None and not isinstance(statements[current_stmt], AssignNode):
                    output.append(result)
                current_stmt += 1
            except InputRequired as e:
                # Store state and request input
                interpreter_states[session_id] = {
                    'interpreter': interpreter,
                    'parser': parser,
                    'statements': statements,
                    'current_stmt': current_stmt
                }
                return jsonify({
                    'status': 'input_required',
                    'line': e.line,
                    'session_id': session_id,
                    'output': '\n'.join(str(item) for item in output)
                })

        # Execution complete, clean up
        if session_id in interpreter_states:
            del interpreter_states[session_id]

        return jsonify({
            'status': 'complete',
            'output': '\n'.join(str(item) for item in output),
            'session_id': session_id
        })

    except Exception as e:
        if session_id in interpreter_states:
            del interpreter_states[session_id]
        return jsonify({'error': str(e), 'session_id': session_id}), 400

@app.route('/submit_input', methods=['POST'])
def submit_input():
    data = request.get_json()
    session_id = data.get('session_id')
    user_input = data.get('input', '')

    if session_id not in interpreter_states:
        return jsonify({'error': 'Invalid session ID'}), 400

    try:
        # Retrieve interpreter and set input
        interpreter = interpreter_states[session_id]['interpreter']
        interpreter.set_input(user_input)

        # Resume execution
        statements = interpreter_states[session_id]['statements']
        current_stmt = interpreter_states[session_id]['current_stmt']
        parser = interpreter_states[session_id]['parser']
        # Update interpreter dictionaries
        interpreter.functions.update(parser.functions)
        interpreter.structs.update(parser.structs)

        output = []
        while current_stmt < len(statements):
            try:
                result = interpreter.evaluate(statements[current_stmt])
                if interpreter.printed_values:
                    output.extend(interpreter.printed_values)
                    interpreter.printed_values.clear()
                elif result is not None and not isinstance(statements[current_stmt], AssignNode):
                    output.append(result)
                current_stmt += 1
            except InputRequired as e:
                interpreter_states[session_id]['current_stmt'] = current_stmt
                return jsonify({
                    'status': 'input_required',
                    'line': e.line,
                    'session_id': session_id,
                    'output': '\n'.join(str(item) for item in output)
                })

        # Execution complete, clean up
        if session_id in interpreter_states:
            del interpreter_states[session_id]

        return jsonify({
            'status': 'complete',
            'output': '\n'.join(str(item) for item in output),
            'session_id': session_id
        })

    except Exception as e:
        if session_id in interpreter_states:
            del interpreter_states[session_id]
        return jsonify({'error': str(e), 'session_id': session_id}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)