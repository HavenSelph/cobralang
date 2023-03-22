# This code is licensed under the MIT License (see LICENSE file for details)
from __future__ import annotations
from .interpreter import Node, Context
from .exceptions import ReturnException, StopException
from .datatypes import Value, Null, Dict, Tuple


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
        if isinstance(self.name, Node):
            return self.name.run(ctx)[self.index.run(ctx)]
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


class StatementBlock(Block):
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
    def __init__(self, name: str, posargs: list[str], varargs: str | None, kwargs: dict[str,Node], varkwargs: str | None, body: StatementBlock):
        self.name = name
        self.posargs = posargs
        self.varargs = varargs
        self.kwargs = kwargs
        self.varkwargs = varkwargs
        self.body = body

    def __repr__(self):
        return f"Function({self.name}, {self.posargs}, {self.varargs}, {self.kwargs}, {self.varkwargs}, {self.body})"

    def run(self, ctx: Context, args: list[Value], _kwargs: dict[str,Value]):
        if len(args) < len(self.posargs):
            raise Exception(f"Function {self.name} expected {len(self.posargs)} arguments, got {len(args)}")
        ctx.push_scope()
        posargs, varargs = args, []
        if len(args) > len(self.posargs):
            if self.varargs is None:
                raise Exception(f"Function {self.name} expected {len(self.posargs)} arguments, got {len(args)}")
            posargs = args[:len(self.posargs)]
            varargs = args[len(self.posargs):]
        kwargs = self.kwargs.copy()
        undefined_kwargs = set(_kwargs.keys()) - set(self.kwargs.keys())
        if undefined_kwargs and self.varkwargs is None:
            raise Exception(f"Function {self.name} got unexpected keyword arguments {undefined_kwargs}")
        defined_kwargs = set(_kwargs.keys()) - undefined_kwargs
        if defined_kwargs:
            kwargs.update({k: _kwargs[k] for k in defined_kwargs})
        if undefined_kwargs:
            kwargs.update({self.varkwargs: Dict({k: _kwargs[k] for k in undefined_kwargs})})
        if varargs:
            # noinspection PyTypeChecker
            kwargs[self.varargs] = Tuple(varargs)
        for name, arg in zip(self.posargs, posargs):
            ctx.current_scope().variables[name] = arg
        for name, arg in kwargs.items():
            ctx.current_scope().variables[name] = arg
        try:
            out = self.body.run(ctx)
            if not isinstance(out, Null):
                return out
        except ReturnException as e:
            out = e.value
            return out
        finally:
            ctx.pop_scope()


class FunctionDefinition(Node):
    def __init__(self, function: Function):
        self.function = function

    def __repr__(self):
        return f"FunctionDeclaration({self.function})"

    def run(self, ctx: Context):
        self.function.kwargs = {k: v.run(ctx) for k, v in self.function.kwargs.items()}
        ctx.push_function(self.function.name, self.function)


class FunctionCall(Node):
    def __init__(self, name: str, args: list[Node], kwargs: dict[str:Node]):
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return f"FunctionCall({self.name}, {self.args}, {self.kwargs})"

    def run(self, ctx: Context):
        function = ctx.get_function(self.name)
        args = [arg.run(ctx) for arg in self.args]
        kwargs = {k: v.run(ctx) for k, v in self.kwargs.items()}
        return function.run(ctx, args, kwargs)


class FromImportFn(Node):
    def __init__(self, name: str, filename: str, program: Program, names: list[str]):
        self.name = name
        self.filename = filename
        self.program = program
        self.functions = names

    def __repr__(self):
        return f"FromImportFn({self.name}, {self.functions})"

    def run(self, ctx: Context):
        try:
            ctx.push_scope()
            self.program.run(ctx)
            for name in self.functions:
                ctx.scopes[-2].functions[name] = ctx.get_function(name)
        except KeyError:
            raise Exception(f"Function(s) not found in module {self.name}")
        finally:
            ctx.pop_scope()


class FromImportVar(Node):
    def __init__(self, name: str, filename: str, program: Program, names: list[str]):
        self.name = name
        self.filename = filename
        self.program = program
        self.variables = names

    def __repr__(self):
        return f"FromImportVar({self.name}, {self.variables})"

    def run(self, ctx: Context):
        try:
            ctx.push_scope()
            self.program.run(ctx)
            for name in self.variables:
                ctx.scopes[-2].variables[name] = ctx[name]
        except KeyError:
            raise Exception(f"Variable(s) not found in module {self.name} - {self.filename}")
        finally:
            ctx.pop_scope()
