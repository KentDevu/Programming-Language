def factorial(n, depth=0):
    indent = "  " * depth  # visual indent for recursion level

    if not isinstance(n, int) or n < 0:
        raise ValueError(f"[Error] Invalid input: n must be a non-negative integer, got {n}")

    print(f"{indent}[Debug] Function factorial called with argument n={n}")

    if n == 0:
        print(f"{indent}[Debug] Base case reached, returning 1.")
        return 1
    else:
        print(f"{indent}[Debug] Recursively calling factorial({n - 1})")
        result = n * factorial(n - 1, depth + 1)
        print(f"{indent}[Debug] Computed factorial({n}) = {result}")
        return result

# Entry point
try:
    result = factorial(5)
    print(f"\nResult: {result}")
except Exception as e:
    print(str(e))
