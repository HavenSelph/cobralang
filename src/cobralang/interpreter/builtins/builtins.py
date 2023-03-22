# This code is licensed under the MIT License (see LICENSE file for details)
from ..nodes import Function, StatementBlock
from typing import Callable
from ..datatypes import *
import inspect
from time import time
from random import randint
from pathlib import Path
from src import __version__, __author__, __repo__, __license__


std_functions = {}


class BuiltInStatementBlock(StatementBlock):
    def __init__(self, function: Callable):
        self.function = function
        if function.__doc__ is not None:
            self.doc = "\n".join([ln.strip() for ln in function.__doc__.strip().splitlines()])
            super().__init__([StringLiteral(self.doc), StringLiteral("<built-in>")])
        else:
            self.doc = "No documentation available for this function."
            # noinspection PyTypeChecker
            super().__init__(["<built-in>"])

    def run(self, ctx):
        out = self.function(ctx)
        return out


def register_function(name: str, args: list[str]=None, varargs: str | None=None, kwargs=None, varkwargs: str | None=None):
    def inner(func: Callable):
        std_functions[name] = Function(name, args, varargs, kwargs, varkwargs, BuiltInStatementBlock(func))
        return func
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    return inner


def register_auto(func: Callable):
    name = func.__name__.replace("_function", "")
    args = inspect.signature(func)
    pos_args = []
    var_args = None
    kwargs = {}
    var_kwargs = None
    for arg in args.parameters.values():
        if arg.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            if arg.default == inspect.Parameter.empty:
                if arg.name == "ctx":
                    continue
                pos_args.append(arg.name)
            else:
                kwargs[arg.name] = auto_cast(arg.default)
        elif arg.kind == inspect.Parameter.VAR_POSITIONAL:
            var_args = arg.name
        elif arg.kind == inspect.Parameter.KEYWORD_ONLY:
            kwargs[arg.name] = auto_cast(arg.default)
        elif arg.kind == inspect.Parameter.VAR_KEYWORD:
            var_kwargs = arg.name

    def wrapper(ctx):
        _args = []
        _kwargs = {}
        if len(tuple(args.parameters))>0 and tuple(args.parameters.keys())[0] == "ctx":
            _args.append(ctx)
        for _arg in pos_args:
            _args.append(get_arg(ctx, _arg))
        if var_args is not None:
            try:
                _args.extend(get_arg(ctx, var_args))
            except KeyError:
                pass
        for _arg in kwargs:
            _kwargs[_arg] = get_arg(ctx, _arg)
        if var_kwargs is not None:
            try:
                _kwargs.update(get_arg(ctx, var_kwargs))
            except KeyError:
                pass
        out = auto_cast(func(*_args, **_kwargs))
        return out
    wrapper.__doc__ = func.__doc__
    register_function(name, pos_args, var_args, kwargs, var_kwargs)(wrapper)
    return func


def type_of(item):
    match item:
        case list():
            return "list(" + ", ".join([type_of(v) for v in item]) + ")"
        case tuple():
            return "tuple(" + ", ".join([type_of(v) for v in item]) + ")"
        case dict():
            return "dict(" + ", ".join([type_of(k) + ": " + type_of(v) for k, v in item.items()]) + ")"
        case List():
            return "List(" + ", ".join([type_of(v) for v in item]) + ")"
        case Tuple():
            return "Tuple(" + ", ".join([type_of(v) for v in item]) + ")"
        case Dict():
            return "Dict(" + ", ".join([type_of(k) + ": " + type_of(v) for k, v in item.value.items()]) + ")"
        case _:
            return item.__class__.__name__.__repr__() + "(" + str(item) + ")"


def get_arg(ctx: Context, name: str, value_of=True):
    return auto_cast_param(ctx[name]) if value_of else ctx[name]


def auto_cast(value):
    match value:
        case int():
            return Integer(value)
        case float():
            return Float(value)
        case str():
            return String(value)
        case bool():
            return Boolean(value)
        case list():
            return List([auto_cast(x) for x in value])
        case dict():
            return Dict({auto_cast(k): auto_cast(v) for k, v in value.items()})
        case tuple():
            return Tuple(tuple(auto_cast(x) for x in value))
        case x if x is None:
            return Null()
        case x if isinstance(x, Node):
            return value
        case _:
            raise Exception(f"Unsupported value for auto_cast: {value}")


def auto_cast_param(value):
    match value:
        case Integer():
            return int(value.value)
        case Float():
            return float(value.value)
        case String():
            return str(value.value)
        case Boolean():
            return bool(value.value)
        case List():
            return [auto_cast_param(x.value) for x in value]
        case Tuple():
            return tuple(auto_cast_param(x.value) for x in value)
        case Dict():
            return {auto_cast_param(k.value): auto_cast_param(v.value) for k, v in value.value.items()}
        case Null():
            return None
        case _:
            raise Exception(f"Unsupported value for auto_cast_param: {type_of(value)}")


@register_auto
def print_function(*args, sep=" ", end="\n", flush=True):
    """
    Print any amount of arguments to the console.

    args: The arguments to print.
    sep: The separator between the arguments.
    end: The string to print at the end.
    flush: Whether to flush the output.
    """
    print(*args, sep=sep, end=end, flush=flush)


@register_auto
def exit_function(code=0):
    """
    Exit the program.

    code: The exit code.
    """
    # exit(code=0)
    exit(code)


@register_auto
def dump_function(ctx: Context, only_current=False, show_vars=True, show_funcs=True, show_doc=True, show_builtins=True):
    """
    Dump the current context, nicely formatted, to the console.

    only_current: Whether to only dump the current scope.
    show_vars: Whether to show the variables.
    show_funcs: Whether to show the functions.
    show_doc: Whether to show the docstrings.
    show_builtins: Whether to show the built-in functions.
    """
    space_count = 0
    for scope in ctx.scopes[:-1] if not only_current else (ctx.scopes[-2],):
        if show_vars:
            print(" " * space_count + "Variables: [\n" + "".join([f"{' ' * space_count}\t{name}={value}\n" for name, value in scope.variables.items()]) + " " * space_count + "]")
        if show_funcs:
            funcs = []
            for name, value in scope.functions.items():
                if isinstance(value.body, BuiltInStatementBlock) and not show_builtins:
                    continue
                func = f"{name}({', '.join(value.posargs) or '_'}, {value.varargs or '_'}, {','.join([f'{k}={v!r}' for k, v in value.kwargs.items()]) or '_'}, {value.varkwargs or '_'})"
                funcs.append("\n\u001b[34m" + " " * (space_count + 2) + f"{'<built-in>' if isinstance(value.body, BuiltInStatementBlock) else ''} {func} \u001b[0m")
                if not show_doc:
                    continue
                if isinstance(value.body.statements[0], StringLiteral):
                    # noinspection PyUnresolvedReferences
                    docstring = value.body.statements[0].value.splitlines()
                    while docstring[0] == "":
                        docstring.pop(0)
                    while docstring[-1] == "":
                        docstring.pop(-1)
                    for line in docstring:
                        funcs.append(" " * (space_count + 2) + line)
                else:
                    funcs.append(" " * (space_count + 2) + "No documentation available.")
            print(" " * space_count + "Functions: [\n" + '\n'.join(funcs) + "\n" + " " * space_count + "]")
        space_count += 1


@register_auto
def funcs_function(ctx: Context, only_current=False, show_doc=True):
    """
    Show all functions in the current context.

    only_current: Whether to only dump the current scope.
    show_doc: Whether to show the documentation.
    """
    dump_function(ctx, only_current, False, True, show_doc, True)


@register_auto
def my_funcs(ctx: Context, only_current=False, show_doc=True):
    """
    Get all non-built-in functions in the current context.

    only_current: Whether to only dump the current scope.
    show_doc: Whether to show the documentation.
    """
    dump_function(ctx, only_current, False, True, show_doc, False)


@register_auto
def clear_function(ctx: Context, keep_functions=False, no_warning=False):
    """
    Clear the current context.

    keep_functions: Whether to keep the functions.
    no_warning: Whether to show a warning.
    """
    ctx.clear_context(keep_functions, no_warning)


@register_auto
def time_function(as_int=False):
    """
    Get the current time.

    as_int: Whether to return the time as an integer.
    """
    if as_int:
        return time()
    return int(time())


@register_auto
def get_variables_function(ctx: Context):
    """
    Get all variables in the current context.
    """
    variables = {}
    for scope in ctx.scopes:
        for name, value in scope.variables.items():
            variables[name] = value
    return tuple(variables.keys())


@register_auto
def get_variable_function(ctx: Context, name):
    """
    Get a variable from the current context.

    name: The name of the variable.
    """
    return ctx[name]


@register_auto
def get_functions_function(ctx: Context):
    """
    Get all functions in the current context.
    """
    functions = {}
    for scope in ctx.scopes:
        for name, value in scope.functions.items():
            functions[name] = value
    return tuple(functions.keys())


@register_auto
def set_variable_function(ctx: Context, name, value):
    """
    Set a variable in the current context.

    name: The name of the variable.
    value: The value of the variable.
    """
    ctx[name] = value


@register_auto
def set_global_function(ctx: Context, name, value):
    """
    Set a global variable.

    name: The name of the variable.
    value: The value of the variable.
    """
    ctx.scopes[0].variables[name] = value


@register_auto
def input_function(prompt=""):
    """
    Get input from the user.

    prompt: The prompt to show the user.
    """
    return input(prompt)


@register_auto
def insert_function(iterable, index, value):
    """
    Insert a value into a list.

    iterable: The list to insert into.
    index: The index to insert at.
    value: The value to insert.
    """
    iterable.insert(index, value)


@register_auto
def append_function(iterable, value):
    """
    Append a value to a list.

    iterable: The list to append to.
    value: The value to append.
    """
    iterable.append(value)


@register_auto
def pop_function(iterable, index):
    """
    Pop a value from a list.

    iterable: The list to pop from.
    index: The index to pop from.
    """
    return iterable.pop(index)


@register_auto
def type_function(ctx, value, recursive=False):
    """
    Get the type of a value.

    value: The value to get the type of.
    """
    # type(value)
    value = get_arg(ctx, "value", value_of=False)
    return value.__class__.__name__ if not recursive else type_of(value)


@register_auto
def int_function(value):
    """
    Convert a value to an integer.

    value: The value to convert.
    """
    return Integer(int(value))


@register_auto
def float_function(value):
    """
    Convert a value to a float.

    value: The value to convert.
    """
    return Float(float(value))


@register_auto
def str_function(value):
    """
    Convert a value to a string.

    value: The value to convert.
    """
    return String(str(value))


@register_auto
def bool_function(value):
    """
    Convert a value to a boolean.

    value: The value to convert.
    """
    return Boolean(bool(value))


def list_function(value):
    """
    Convert a value to a list.

    value: The value to convert.
    """
    return List(list(value))


@register_auto
def tuple_function(value):
    """
    Convert a value to a tuple.

    value: The value to convert.
    """
    return Tuple(tuple(value))


@register_auto
def len_function(value):
    """
    Get the length of a value.

    value: The value to get the length of.
    """
    # len(value)
    return Integer(len(value))


@register_auto
def random_function(minimum=0, maximum=1):
    """
    Get a random integer between two values.

    min: The minimum value.
    max: The maximum value.
    """
    return Integer(randint(minimum, maximum))


@register_auto
def choice_function(iterable):
    """
    Get a random element from an iterable.

    iterable: The iterable to get a random element from.
    """
    # choice(iterable)
    return iterable[randint(0, len(iterable) - 1)]


@register_auto
def license_function():
    """
    Get the license.
    """
    path = Path(__file__).parent.parent.parent.parent.parent.joinpath("LICENSE.md")
    with open(path, "r") as f:
        text = f.read()
    print(text.replace("[Learn what this license permits you to do](https://choosealicense.com/licenses/mit/)", "https://choosealicense.com/licenses/mit/").replace("> ", ""))


@register_auto
def info_function():
    """
    Get information about the language.
    """

    print(f"CobraLang (v{__version__}) Licensed under {__license__} license, type license() for more info.\nMade by {__author__}, find the source code at: {__repo__}\nType 'exit()' to exit, 'clear()' to clear the context, help() for help.")
