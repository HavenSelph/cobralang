from ..nodes import Function, FunctionBlock
from typing import Callable
from ..datatypes import *
from time import time
from random import randint


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


def get_arg(ctx: Context, name: str):
    return ctx[name].value


@register_function("print", varargs="args", kwargs={"sep": String(" "), "end": String("\n"), "flush": Boolean(True)})
def print_function(ctx: Context):
    # print(*args, sep=" ", end="\n", flush=True)
    args = get_arg(ctx, "args")
    sep = get_arg(ctx, "sep")
    end = get_arg(ctx, "end")
    flush = get_arg(ctx, "flush")
    print(*args, sep=sep, end=end, flush=flush)


@register_function("exit", kwargs={"code": Integer(0)})
def exit_function(ctx: Context):
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
            functions = "\n".join([f"{' ' * space_count}\t{name}({value.posargs}, {value.varargs or 'Null'}, {value.kwargs}, {value.varkwargs or 'Null'}) {{\n" + "\n".join([' ' * (space_count+4) + statement.__repr__() for statement in value.body.statements]) + '\n' + ' ' * (space_count+2) + "}" for name, value in scope.functions.items()])
            print(" " * space_count + "Functions: [\n" + functions + " " * space_count + "]")
        space_count += 2


@register_function("clear")
def clear_function(ctx: Context):
    ctx.clear_scopes()


@register_function("time", kwargs={"as_int": Boolean(False)})
def time_function(ctx: Context):
    # time(as_int=False)
    as_int = get_arg(ctx, "as_int")
    if as_int:
        return Float(time())
    return Integer(int(time()))


@register_function("getvars")
def get_variables_function(ctx: Context):
    # getvars()
    variables = {}
    for scope in ctx.scopes:
        for name, value in scope.variables.items():
            variables[name] = value
    return List(list(variables.keys()))


@register_function("getvar", args=["name"])
def get_variable_function(ctx: Context):
    # getvar(name)
    name = get_arg(ctx, "name")
    return ctx[name]


@register_function("getfuncs")
def get_functions_function(ctx: Context):
    # getfuncs()
    functions = {}
    for scope in ctx.scopes:
        for name, value in scope.functions.items():
            functions[name] = value
    return List(list(functions.keys()))


@register_function("setvar", args=["name", "value"])
def set_variable_function(ctx: Context):
    # setvar(name, value)
    name = get_arg(ctx, "name")
    value = get_arg(ctx, "value")
    ctx[name] = value


@register_function("global", args=["name", "value"])
def set_global_function(ctx: Context):
    # global(name, value)
    name = get_arg(ctx, "name")
    value = get_arg(ctx, "value")
    ctx.scopes[0].variables[name] = value


@register_function("input", args=["prompt"])
def input_function(ctx: Context):
    # input(prompt="")
    prompt = get_arg(ctx, "prompt")
    return String(input(prompt))


@register_function("insert", args=["list", "index", "value"])
def insert_function(ctx: Context):
    # insert(list, index, value)
    list_ = get_arg(ctx, "list")
    index = get_arg(ctx, "index")
    value = get_arg(ctx, "value")
    list_.insert(index, value)


@register_function("append", args=["list", "value"])
def append_function(ctx: Context):
    # append(list, value)
    list_ = get_arg(ctx, "list")
    value = get_arg(ctx, "value")
    list_.append(value)


@register_function("pop", args=["list", "index"])
def pop_function(ctx: Context):
    # pop(list, index)
    list_ = get_arg(ctx, "list")
    index = get_arg(ctx, "index")
    return list_.pop(index)


@register_function("type", args=["value"])
def type_function(ctx: Context):
    # type(value)
    value = get_arg(ctx, "value")
    return String(value.__class__.__name__)


@register_function("int", args=["value"])
def int_function(ctx: Context):
    # int(value)
    value = get_arg(ctx, "value")
    return Integer(int(value))


@register_function("float", args=["value"])
def float_function(ctx: Context):
    # float(value)
    value = get_arg(ctx, "value")
    return Float(float(value))


@register_function("str", args=["value"])
def str_function(ctx: Context):
    # str(value)
    value = get_arg(ctx, "value")
    return String(str(value))


@register_function("bool", args=["value"])
def bool_function(ctx: Context):
    # bool(value)
    value = get_arg(ctx, "value")
    return Boolean(bool(value))


@register_function("list", args=["value"])
def list_function(ctx: Context):
    # list(value)
    value = get_arg(ctx, "value")
    return List(list(value))


@register_function("tuple", args=["value"])
def tuple_function(ctx: Context):
    # tuple(value)
    value = get_arg(ctx, "value")
    return Tuple(tuple(value))


@register_function("len", args=["value"])
def len_function(ctx: Context):
    # len(value)
    value = get_arg(ctx, "value")
    return Integer(len(value))


@register_function("random", args=["min", "max"])
def random_function(ctx: Context):
    # random(min, max)
    min_ = get_arg(ctx, "min")
    max_ = get_arg(ctx, "max")
    return Integer(randint(min_, max_))
