from abc import ABC, abstractmethod

class Expression(ABC):
    @abstractmethod
    def evaluate(self):
        """Evaluate the expression."""
        pass

class Number(Expression):
    def __init__(self, value):
        self.value = value
    
    def evaluate(self):
        return self.value

class Add(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def evaluate(self):
        return self.left.evaluate() + self.right.evaluate()

class Subtract(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def evaluate(self):
        return self.left.evaluate() - self.right.evaluate()

class Multiply(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def evaluate(self):
        return self.left.evaluate() * self.right.evaluate()

class Divide(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def evaluate(self):
        right_val = self.right.evaluate()
        if right_val == 0:
            raise ValueError("Division by zero")
        return self.left.evaluate() / right_val

# Program to demonstrate polymorphism
if __name__ == "__main__":
    # Create a list of different expressions
    expressions = [
        Number(10),                          # 10
        Add(Number(5), Number(3)),           # 5 + 3 = 8
        Subtract(Number(7), Number(2)),      # 7 - 2 = 5
        Multiply(Number(4), Number(3)),      # 4 * 3 = 12
        Divide(Number(8), Number(2)),        # 8 / 2 = 4
        Multiply(Add(Number(2), Number(3)), Number(2))  # (2 + 3) * 2 = 10
    ]
    
    # Evaluate each expression using a loop
    for i, expr in enumerate(expressions, 1):
        try:
            result = expr.evaluate()
            print(f"Expression {i}: {result}")
        except ValueError as e:
            print(f"Expression {i}: Error - {e}")