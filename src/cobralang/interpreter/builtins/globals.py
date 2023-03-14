from ..interpreter import Context, Node
from ..nodes import Function, Block
from ..exceptions import StopException
from ..datatypes import *


class EmptyBlock(Block):
    def __init__(self):
        super().__init__([])

    def __repr__(self):
        return "<builtin>"

    def run(self, ctx: Context):
        return None


class InputFunction(Function):
    def __init__(self):
        super().__init__("input", ["prompt"], EmptyBlock())

    def run(self, ctx: Context, args):
        return String(input(args[0]))


class PrintFunction(Function):
    def __init__(self):
        super().__init__("print", ["output"], EmptyBlock())

    def run(self, ctx: Context, args):
        print(*args)
        return None


class DumpContext(Function):
    def __init__(self):
        super().__init__("ctx", [], EmptyBlock())

    def run(self, ctx: Context, args):
        space_count = 0
        for scope in ctx.scopes:
            print(" "*space_count+"Variables: [\n"+"".join([f"{' '*space_count}\t{name}={value}\n" for name, value in scope.variables.items()])+" "*space_count+"]")
            print(" "*space_count+"Functions: [\n"+"".join([f"{' '*space_count}\t{name}={value}\n" for name, value in scope.functions.items()])+" "*space_count+"]")
            space_count += 2
        return None


class ExitFunction(Function):
    def __init__(self):
        super().__init__("exit", ["code"], EmptyBlock())

    def run(self, ctx: Context, args):
        raise StopException(args[0])


class TypeFunction(Function):
    def __init__(self):
        super().__init__("type", ["value"], EmptyBlock())

    def run(self, ctx: Context, args):
        return String(args[0].__class__.__name__)


class AsIntFunction(Function):
    def __init__(self):
        super().__init__("int", ["value"], EmptyBlock())

    def run(self, ctx: Context, args):
        return Integer(int(args[0].value))


class AsFloatFunction(Function):
    def __init__(self):
        super().__init__("float", ["value"], EmptyBlock())

    def run(self, ctx: Context, args):
        return Float(float(args[0].value))


class AsStringFunction(Function):
    def __init__(self):
        super().__init__("string", ["value"], EmptyBlock())

    def run(self, ctx: Context, args):
        return String(str(args[0].value))


class AsBoolFunction(Function):
    def __init__(self):
        super().__init__("bool", ["value"], EmptyBlock())

    def run(self, ctx: Context, args):
        return Boolean(bool(args[0].value))


std_functions = {
    "print": PrintFunction(),
    "ctx": DumpContext(),
    "exit": ExitFunction(),
    "input": InputFunction(),
    "type": TypeFunction(),
    "int": AsIntFunction(),
    "float": AsFloatFunction(),
    "str": AsStringFunction(),
    "bool": AsBoolFunction()
}
