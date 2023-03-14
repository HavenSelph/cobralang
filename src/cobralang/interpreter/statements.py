from .interpreter import Context, Node
from .exceptions import ReturnException
from .nodes import Block


class PrintStatement(Node):
    def __init__(self, value: Node):
        self.value = value

    def __repr__(self):
        return f"print {self.value}"

    def run(self, ctx: Context):
        print(self.value.run(ctx))
        return None


class ReturnStatement(Node):
    def __init__(self, value: Node):
        self.value = value

    def __repr__(self):
        return f"return {self.value}"

    def run(self, ctx: Context):
        raise ReturnException(self.value.run(ctx))


class IfStatement(Node):
    def __init__(self, condition: Node, body: Block, else_body: Block):
        self.condition = condition
        self.body = body
        self.else_body = else_body

    def __repr__(self):
        return f"if {self.condition} {self.body} else {self.else_body}"

    def run(self, ctx: Context):
        if self.condition.run(ctx):
            out = self.body.run(ctx)
        else:
            out = self.else_body.run(ctx)
        return out


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
