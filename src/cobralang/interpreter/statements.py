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


class ForStatement(Node):
    def __init__(self, variables: list[Node], iterable: Node, body: StatementBlock):
        self.variables = variables
        self.iterable = iterable
        self.body = body

    def __repr__(self):
        return f"for {self.variables} in {self.iterable} {self.body}"

    def run(self, ctx: Context):
        i = 0
        iterable = self.iterable.run(ctx)
        iter_len = len(iterable)
        if iter_len % len(self.variables) != 0:
            raise Exception("Iterable length must be divisible by the number of variables")
        ctx.push_scope()
        try:
            while i < iter_len:
                for k in range(len(self.variables)):
                    ctx.current_scope().variables[self.variables[k].name] = iterable.value[i + k]
                i += len(self.variables)
                self.body.run(ctx)
        finally:
            ctx.pop_scope()
