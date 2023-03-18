from ..nodes import Function, FunctionBlock
from typing import Callable
from ..datatypes import *


std_functions = {}


class BuiltInFunctionBlock(FunctionBlock):
    def __init__(self, function: Callable):
        self.function = function
        super().__init__([StringLiteral("<built-in function>")])

    def run(self, ctx):
        return self.function(ctx)


def register_function(name: str, args: list[str]=None, varargs: str | None=None, kwargs=None, varkwargs: str | None=None):
    def inner(func: Callable):
        std_functions[name] = Function(name, args, varargs, kwargs, varkwargs, BuiltInFunctionBlock(func))
        return func
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    return inner


def get_arg(ctx, name):
    return ctx[name].value


@register_function("print", varargs="args", kwargs={"sep": String(" "), "end": String("\n"), "flush": Boolean(True)})
def print_function(ctx):
    # print(*args, sep=" ", end="\n", flush=True)
    args = get_arg(ctx, "args")
    sep = get_arg(ctx, "sep")
    end = get_arg(ctx, "end")
    flush = get_arg(ctx, "flush")
    print(*args, sep=sep, end=end, flush=flush)


@register_function("exit", kwargs={"code": Integer(0)})
def exit_function(ctx):
    # exit(code=0)
    code = get_arg(ctx, "code")
    exit(code)


@register_function("dump", kwargs={"show_self": Boolean(False), "show_var": Boolean(True), "show_func": Boolean(True)})
def dump_function(ctx: Context):
    # dump(all=True)
    show_self = get_arg(ctx, "show_self")
    show_var = get_arg(ctx, "show_var")
    show_func = get_arg(ctx, "show_func")
    space_count = 0
    for scope in ctx.scopes if show_self else ctx.scopes[:-1]:
        if show_var:
            print(" " * space_count + "Variables: [\n" + "".join([f"{' ' * space_count}\t{name}={value}\n" for name, value in scope.variables.items()]) + " " * space_count + "]")
        if show_func:
            print(" " * space_count + "Functions: [\n" + "".join([f"{' ' * space_count}\t{name}={value}\n" for name, value in scope.functions.items()]) + " " * space_count + "]")
        space_count += 2


@register_function("clear")
def clear_function(ctx: Context):
    ctx.clear_scopes()


# std_functions = {
#     "time": TimeFunction(),
#     "getctx": GetContext(),
#     "getvars": GetVariables(),
#     "getvar": GetVariable(),
#     "getfuncs": GetFunctions(),
#     "getfunc": GetFunction(),
#     "setvar": SetVariable(),
#     "global": SetGlobal(),
#     "input": InputFunction(),
#     "insert": InsertFunction(),
#     "append": AppendFunction(),
#     "type": TypeFunction(),
#     "int": AsIntFunction(),
#     "float": AsFloatFunction(),
#     "str": AsStringFunction(),
#     "bool": AsBoolFunction(),
#     "list": AsListFunction(),
#     "tuple": AsTupleFunction(),
#     "len": LenFunction(),
#     "random": RandomFunction(),
# }
