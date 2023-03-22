# This code is licensed under the MIT License (see LICENSE file for details)
from .interpreter import Context, Node


class BinaryOp(Node):
    def __init__(self, left: Node, right: Node, op_name="", run_func=None):
        self.left = left
        self.right = right
        self.op_name = op_name
        self.run_func = run_func

    def __repr__(self):
        return f"{self.left} {self.op_name} {self.right}"

    def run(self, ctx: Context):
        return self.run_func(self.left.run(ctx), self.right.run(ctx))


class And(BinaryOp):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right, "and", lambda a, b: a and b)


class Or(BinaryOp):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right, "or", lambda a, b: a or b)


class GreaterThan(BinaryOp):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right, ">", lambda a, b: a > b)


class GreaterThanOrEqual(BinaryOp):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right, ">=", lambda a, b: a >= b)


class LessThan(BinaryOp):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right, "<", lambda a, b: a < b)


class LessThanOrEqual(BinaryOp):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right, "<=", lambda a, b: a <= b)


class Equals(BinaryOp):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right, "==", lambda a, b: a == b)


class NotEquals(BinaryOp):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right, "!=", lambda a, b: a != b)


class Add(BinaryOp):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right, "+", lambda a, b: a + b)


class Subtract(BinaryOp):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right, "-", lambda a, b: a - b)


class Multiply(BinaryOp):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right, "*", lambda a, b: a * b)


class Power(BinaryOp):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right, "**", lambda a, b: a ** b)


class Divide(BinaryOp):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right, "/", lambda a, b: a / b)


class FloorDivide(BinaryOp):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right, "//", lambda a, b: a // b)


class Modulo(BinaryOp):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right, "%", lambda a, b: a % b)


class In(BinaryOp):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right, "in", lambda a, b: a in b)
