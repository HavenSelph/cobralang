from __future__ import annotations
from .interpreter import Node, Context
from .exceptions import ReturnException, StopException
from .datatypes import Value, Null


class VariableReference(Node):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name

    def run(self, ctx: Context):
        return ctx[self.name]


class Subscript(Node):
    def __init__(self, name: VariableReference | Value | Subscript, index: Node):
        self.name = name
        self.index = index

    def __repr__(self):
        return f"{self.name}[{self.index}]"

    def run(self, ctx: Context):
        if isinstance(self.name, Value):
            return self.name.value[self.index.run(ctx)]
        elif isinstance(self.name, Subscript):
            return self.name.run(ctx)[self.index.run(ctx)]
        elif isinstance(self.name, VariableReference):
            return ctx[self.name.name][self.index.run(ctx)]

    def get_target(self, ctx: Context):
        if isinstance(self.name, Value):
            return self.name.value
        elif isinstance(self.name, Subscript):
            return self.name.run(ctx)
        elif isinstance(self.name, VariableReference):
            return ctx[self.name.name]


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

    def run(self, ctx: Context):  # allow x[0][0] = 1
        if isinstance(self.left, VariableReference):
            ctx[self.left.name] = self.right.run(ctx)
        elif isinstance(self.left, Subscript):
            target = self.left.get_target(ctx)
            target[self.left.index.run(ctx)] = self.right.run(ctx)
        else:
            raise Exception(f"Invalid assignment target: {self}")


# class SubscriptAssignment(Node):
#     def __init__(self, left: str, index: Node, right: Node):
#         self.left = left
#         self.index = index
#         self.right = right
#
#     def __repr__(self):
#         return f"{self.left}[{self.index}] = {self.right}"
#
#     def run(self, ctx: Context):
#         ctx[self.left][self.index.run(ctx)] = self.right.run(ctx)


class Block(Node):
    def __init__(self, statements: list[Node]):
        self.statements = statements

    def __repr__(self):
        return f"{{ {self.statements} }}"

    def run(self, ctx: Context):
        ctx.push_scope()
        out = Null()
        try:
            for statement in self.statements:
                out = statement.run(ctx)
            return out
        finally:
            ctx.pop_scope()


class FunctionBlock(Block):
    def run(self, ctx: Context):
        out = Null()
        for statement in self.statements:
            out = statement.run(ctx)
        return out


class Program(Block):
    def __init__(self, statements: list[Node]):
        super().__init__(statements)

    def __repr__(self):
        return f"Program({self.statements})"

    def run(self, ctx: Context):
        out = None
        try:
            for statement in self.statements:
                out = statement.run(ctx)
        except ReturnException as e:
            out = e.value
        except StopException as e:
            if e.code is not None:
                print("Program exited with code ", e.code)
            exit(0)
        if out is not None:
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
        result = Null()
        try:
            for name, arg in zip(self.args, args):
                ctx.current_scope().variables[name] = arg
            result = self.body.run(ctx)
        except ReturnException as e:
            result = e.value
        finally:
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
