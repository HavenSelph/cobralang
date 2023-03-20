from .interpreter import Context, Node
from .exceptions import ReturnException
from .nodes import Block, StatementBlock, VariableDeclaration


class ReturnStatement(Node):
    def __init__(self, value: Node):
        self.value = value

    def __repr__(self):
        return f"return {self.value}"

    def run(self, ctx: Context):
        raise ReturnException(self.value.run(ctx))


class IfStatement(Node):
    def __init__(self, body: list[tuple[Node, Block]]):
        self.body = body

    def __repr__(self):
        return f"IfStatement: {self.body}"

    def run(self, ctx: Context):
        for condition, body in self.body:
            if condition.run(ctx):
                body.run(ctx)
                return


class WhileStatement(Node):
    def __init__(self, condition: Node, body: Block):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"while {self.condition} {self.body}"

    def run(self, ctx: Context):
        out = None
        while self.condition.run(ctx):
            out = self.body.run(ctx)
        return out
