class Calculator:
    def __init__(self):
        self.precision = 2
        self.history = []

    def _validate_input(self, a, b):
        if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
            raise ValueError("Inputs must be numbers.")

    def add(self, a, b):
        """Enhanced addition with logging and precision"""
        self._validate_input(a, b)
        result = a + b
        self.history.append(f"ADD: {a} + {b} = {result}")
        return round(result, self.precision)
    def add(self, a, b):
        """Enhanced addition with logging and precision"""
        result = a + b
        self.history.append(f"ADD: {a} + {b} = {result}")
        return round(result, self.precision)
    
    def subtract(self, a, b):
        self._validate_input(a, b)
        return a - b

    def multiply(self, a, b):
        self._validate_input(a, b)
        return a * b

    def multiply_with_precision(self, a, b, precision=None):
        self._validate_input(a, b)
        if precision is None:
            precision = self.precision
        result = a * b
        self.history.append(f"MULTIPLY_PRECISION: {a} * {b} = {result}")
        return round(result, precision)

    def divide(self, a, b):
        self._validate_input(a, b)
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        result = a / b
        self.history.append(f"DIVIDE: {a} / {b} = {result}")
        return round(result, self.precision)
    def multiply(self, a, b):
        return a * b
