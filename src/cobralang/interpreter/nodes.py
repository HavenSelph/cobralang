from .interpreter import Node, Context
from .exceptions import ReturnException, StopException
from .datatypes import NullLiteral, Value


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


class Program(Block):
    def __init__(self, statements: list[Node]):
        super().__init__(statements)

    def __repr__(self):
        return f"Program({self.statements})"

    def run(self, ctx: Context):
        out = NullLiteral()
        try:
            for statement in self.statements:
                out = statement.run(ctx)
        except ReturnException as e:
            out = e.value
        except StopException as e:
            if e.code is not None:
                print("Program exited with code ", e.code)
            exit(0)
        return out


class Function:
    def __init__(self, name: str, args: list, body: Node):
        self.name = name
        self.args = args
        self.body = body

    def __repr__(self):
        return f"Function({self.name} ({self.args}) {{ {self.body} }})"

    def run(self, ctx: Context, args: list[Value]):
        ctx.push_scope()
        for name, arg in zip(self.args, args):
            ctx.current_scope().variables[name] = arg
        try:
            result = self.body.run(ctx)
        except ReturnException as e:
            result = e.value
        ctx.pop_scope()
        return result


class FunctionDefinition(Node):
    def __init__(self, function: Function):
        self.function = function

    def __repr__(self):
        return f"FunctionDeclaration({self.function})"

    def run(self, ctx: Context):
        ctx.push_function(self.function.name, self.function)


class FunctionCall(Node):
    def __init__(self, name: str, args: list[Node]):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"{self.name}({', '.join(map(repr, self.args))})"

    def run(self, ctx: Context):
        args = [arg.run(ctx) for arg in self.args]
        if len(self.args) != len(ctx.get_function(self.name).args):
            raise TypeError(f"Function '{self.name}' expects {len(ctx.get_function(self.name).args)} argument(s) ({', '.join(ctx.get_function(self.name).args)}), {len(self.args)} argument(s) ({', '.join(map(repr, self.args))}) were passed")
        return ctx.get_function(self.name).run(ctx, args)
