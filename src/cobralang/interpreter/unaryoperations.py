from .nodes import Node


class UnaryOp:
    def __init__(self, operand: Node, operator: str, operation):
        self.operand = operand
        self.operator = operator
        self.operation = operation

    def __repr__(self):
        return f"({self.operator} {self.operand})"

    def run(self, ctx):
        return self.operation(self.operand.run(ctx))


class Not(UnaryOp):
    def __init__(self, operand: Node):
        super().__init__(operand, "not", lambda x: not x)


class Minus(UnaryOp):
    def __init__(self, operand: Node):
        super().__init__(operand, "-", lambda x: -x)


class Plus(UnaryOp):
    def __init__(self, operand: Node):
        super().__init__(operand, "+", lambda x: +x)
