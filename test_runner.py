import subprocess
import sys
import io
import contextlib

def run_test(filename, verbose=False, input_value="Alice"):
    cmd = [sys.executable, "main.py", filename]
    if verbose:
        cmd.append("--verbose")
    
    # Capture stdout and stderr
    result = {"stdout": "", "stderr": "", "returncode": 0}
    with io.StringIO() as buf, contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            # Simulate input for input() test
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=input_value + "\n", timeout=5)
            result["stdout"] = stdout
            result["stderr"] = stderr
            result["returncode"] = process.returncode
        except subprocess.TimeoutExpired:
            process.kill()
            result["stderr"] = "Test timed out"
            result["returncode"] = 1
        finally:
            result["stdout"] += buf.getvalue()
    
    return result

def verify_output(test_name, result, expected_stdout, expected_stderr_contains=None):
    print(f"\nRunning {test_name}...")
    passed = True
    
    # Special handling for parallel execution test
    if test_name == "Test 15: Parallel Execution":
        actual_stdout = result["stdout"].strip().splitlines()
        expected_lines = expected_stdout.strip().splitlines()
        # Accept either order: ["1", "2"] or ["2", "1"]
        valid_outputs = [
            expected_lines,
            expected_lines[::-1]
        ]
        if actual_stdout not in valid_outputs:
            print(f"FAIL: {test_name}")
            print("Expected stdout (or reversed):")
            print(expected_stdout)
            print("Got stdout:")
            print(result["stdout"])
            passed = False
    else:
        # Check stdout for other tests
        actual_stdout = result["stdout"].strip().splitlines()
        expected_lines = expected_stdout.strip().splitlines()
        if actual_stdout != expected_lines:
            print(f"FAIL: {test_name}")
            print("Expected stdout:")
            print(expected_stdout)
            print("Got stdout:")
            print(result["stdout"])
            passed = False
    
    # Check stderr (if applicable)
    if expected_stderr_contains:
        if not any(expected_stderr_contains in line for line in result["stderr"].splitlines()):
            print(f"FAIL: {test_name}")
            print(f"Expected stderr to contain: {expected_stderr_contains}")
            print("Got stderr:")
            print(result["stderr"])
            passed = False
    
    # Check return code
    expected_returncode = 0 if not expected_stderr_contains else 1
    if result["returncode"] != expected_returncode:
        print(f"FAIL: {test_name}")
        print(f"Expected returncode: {expected_returncode}, Got: {result["returncode"]}")
        passed = False
    
    if passed:
        print(f"PASS: {test_name}")
    
    return passed

def main():
    tests = [
        {
            "name": "Test 1: Comments and Basic Tokens",
            "expected_stdout": "10",
            "expected_stderr_contains": None
        },
        {
            "name": "Test 2: Valid If Statement",
            "expected_stdout": "x is greater than 5",
            "expected_stderr_contains": None
        },
        {
            "name": "Test 4: Arithmetic Expression",
            "expected_stdout": "14",
            "expected_stderr_contains": None
        },
        {
            "name": "Test 5: While Loop",
            "expected_stdout": "0\n1\n2",
            "expected_stderr_contains": None
        },
        {
            "name": "Test 6: Function Call",
            "expected_stdout": "25",
            "expected_stderr_contains": None
        },
        {
            "name": "Test 7: Input/Output",
            "expected_stdout": "Hello, Alice",
            "expected_stderr_contains": None
        },
        {
            "name": "Test 8: Arrays",
            "expected_stdout": "[1, 2, 3]",
            "expected_stderr_contains": None
        },
        {
            "name": "Test 9: Null",
            "expected_stdout": "None",
            "expected_stderr_contains": None
        },
        {
            "name": "Test 10: Delete",
            "expected_stdout": "",
            "expected_stderr_contains": "Access to deleted variable 'z'"
        },
        {
            "name": "Test 11: Division by Zero",
            "expected_stdout": "",
            "expected_stderr_contains": "Division by zero"
        },
        {
            "name": "Test 12: Type Mismatch",
            "expected_stdout": "",
            "expected_stderr_contains": "Type mismatch in '+' operation"
        },
        {
            "name": "Test 13: Class and Method",
            "expected_stdout": "Hello",
            "expected_stderr_contains": None
        },
        {
            "name": "Test 14: Lambda",
            "expected_stdout": "5",
            "expected_stderr_contains": None
        },
        {
            "name": "Test 15: Parallel Execution",
            "expected_stdout": "1\n2",
            "expected_stderr_contains": None
        },
        {
            "name": "Test 16: Struct",
            "expected_stdout": "3",
            "expected_stderr_contains": None
        }
    ]

    print("Running Toy Language Interpreter Tests...")
    passed_count = 0
    total_tests = len(tests)

    # Run without verbose
    for test in tests:
        result = run_test("test.toy", verbose=False, input_value="Alice")
        passed = verify_output(
            test["name"],
            result,
            test["expected_stdout"],
            test["expected_stderr_contains"]
        )
        if passed:
            passed_count += 1

    # Run with verbose to verify logging
    verbose_test = {
        "name": "Verbose Mode",
        "expected_stdout": "10\nx is greater than 5\n14\n0\n1\n2\n25\nHello, Alice\n[1, 2, 3]\nNone\nHello\n5\n1\n2\n3",
        "expected_stderr_contains": None
    }
    result = run_test("test.toy", verbose=True, input_value="Alice")
    passed = verify_output(
        verbose_test["name"],
        result,
        verbose_test["expected_stdout"],
        verbose_test["expected_stderr_contains"]
    )
    if passed:
        passed_count += 1
    total_tests += 1

    print(f"\nTest Summary: {passed_count}/{total_tests} tests passed")
    sys.exit(0 if passed_count == total_tests else 1)

if __name__ == "__main__":
    main()