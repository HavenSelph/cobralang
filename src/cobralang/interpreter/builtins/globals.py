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


class GetContext(Function):
    def __init__(self):
        super().__init__("getctx", [], EmptyBlock())

    def run(self, ctx: Context, args):
        return GetVariables().run(ctx, []), GetFunctions().run(ctx, [])


class GetVariables(Function):
    def __init__(self):
        super().__init__("getctx", [], EmptyBlock())

    def run(self, ctx: Context, args):
        variables = {}
        for scope in ctx.scopes:
            variables.update(scope.variables)
        # TODO: make return dict
        return Tuple(tuple([key for key in variables.keys()]))


class GetFunctions(Function):
    def __init__(self):
        super().__init__("getfuncs", [], EmptyBlock())

    def run(self, ctx: Context, args):
        functions = {}
        for scope in ctx.scopes:
            functions.update(scope.functions)
        # TODO: make return dict
        return Tuple(tuple([key for key in functions.keys()]))


class GetFunction(Function):
    def __init__(self):
        super().__init__("get", ["name"], EmptyBlock())

    def run(self, ctx: Context, args):
        return ctx.get_function(args[0].value)


class GetVariable(Function):
    def __init__(self):
        super().__init__("getvar", ["name"], EmptyBlock())

    def run(self, ctx: Context, args):
        return ctx[args[0].value]


class SetVariable(Function):
    def __init__(self):
        super().__init__("setvar", ["name", "value"], EmptyBlock())

    def run(self, ctx: Context, args):
        ctx.current_scope().variables[args[0].value] = args[1]
        return None


class SetGlobal(Function):
    def __init__(self):
        super().__init__("setglobal", ["name", "value"], EmptyBlock())

    def run(self, ctx: Context, args):
        ctx.scopes[0].variables[args[0].value] = args[1]
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


class AsListFunction(Function):
    def __init__(self):
        super().__init__("list", ["value"], EmptyBlock())

    def run(self, ctx: Context, args):
        return List(list(args[0].value))


class AsTupleFunction(Function):
    def __init__(self):
        super().__init__("tuple", ["value"], EmptyBlock())

    def run(self, ctx: Context, args):
        return Tuple(tuple(args[0].value))


class InsertFunction(Function):
    def __init__(self):
        super().__init__("insert", ["list", "index", "value"], EmptyBlock())

    def run(self, ctx: Context, args):
        args[0].value.insert(args[1].value, args[2])
        return None


class AppendFunction(Function):
    def __init__(self):
        super().__init__("append", ["list", "value"], EmptyBlock())

    def run(self, ctx: Context, args):
        args[0].value.append(args[1])
        return None


class LenFunction(Function):
    def __init__(self):
        super().__init__("len", ["value"], EmptyBlock())

    def run(self, ctx: Context, args):
        return Integer(len(args[0].value))


std_functions = {
    "print": PrintFunction(),
    "exit": ExitFunction(),
    "dump": DumpContext(),
    "getctx": GetContext(),
    "getvars": GetVariables(),
    "getvar": GetVariable(),
    "getfuncs": GetFunctions(),
    "getfunc": GetFunction(),
    "setvar": SetVariable(),
    "global": SetGlobal(),
    "input": InputFunction(),
    "insert": InsertFunction(),
    "append": AppendFunction(),
    "type": TypeFunction(),
    "int": AsIntFunction(),
    "float": AsFloatFunction(),
    "str": AsStringFunction(),
    "bool": AsBoolFunction(),
    "list": AsListFunction(),
    "tuple": AsTupleFunction(),
    "len": LenFunction(),
}
