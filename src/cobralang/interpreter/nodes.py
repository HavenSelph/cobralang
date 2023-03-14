from .interpreter import Node, Context
from .exceptions import ReturnException
from .datatypes import NullLiteral


class VariableReference(Node):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name

    def run(self, ctx: Context):
        return ctx[self.name]


class VariableDeclaration(Node):
    def __init__(self, name: str, value: Node):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"let {self.name} = {self.value}"

    def run(self, ctx: Context):
        ctx.current_scope().variables[self.name] = self.value.run(ctx)


class Assignment(Node):
    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"{self.left} = {self.right}"

    def run(self, ctx: Context):
        if not isinstance(self.left, VariableReference):
            raise TypeError("Can only assign to a variable")
        ctx[self.left.name] = self.right.run(ctx)


class Block(Node):
    def __init__(self, statements: list[Node]):
        self.statements = statements

    def __repr__(self):
        return f"{{ {self.statements} }}"

    def run(self, ctx: Context):
        ctx.push_scope()
        out = NullLiteral()
        try:
            for statement in self.statements:
                out = statement.run(ctx)
        except ReturnException as e:
            out = e.value
        ctx.pop_scope()
        return out
