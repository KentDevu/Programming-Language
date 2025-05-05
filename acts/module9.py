from typing import Callable, Any, Dict, List

# Pure lambda parser (dummy - returns a lambda)
def parse_lambda(expr: str) -> Callable:
    # For simplicity: "lambda x: x + 1" -> eval as lambda
    return eval(expr)

# Environment is immutable
def extend_env(env: Dict[str, Any], key: str, value: Any) -> Dict[str, Any]:
    new_env = env.copy()
    new_env[key] = value
    return new_env

# Functional map using higher-order function
def functional_map(fn: Callable, lst: List[Any]) -> List[Any]:
    return list(map(fn, lst))

# Closure with retained environment
def make_closure(param: str, body: Callable, env: Dict[str, Any]) -> Callable:
    def closure(arg):
        local_env = extend_env(env, param, arg)
        return body(local_env)
    return closure

# Example usage
if __name__ == "__main__":
    # Create a lambda expression
    lambda_expr = "lambda x: x * 2"
    fn = parse_lambda(lambda_expr)

    # Functional map
    result = functional_map(fn, [1, 2, 3, 4])
    print("Mapped result:", result)  # [2, 4, 6, 8]

    # Closure with captured env
    base_env = {"n": 10}
    def body(env): return env["n"] + 1
    closure = make_closure("n", body, base_env)
    print("Closure result:", closure(5))  # 6
