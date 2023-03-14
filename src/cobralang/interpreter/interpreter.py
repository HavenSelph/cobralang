from abc import ABC, abstractmethod


class Scope:
    def __init__(self):
        self.variables = {}
        self.functions = {}

    def __repr__(self):
        return f"Scope({self.variables}, {self.functions})"


class Context:
    def __init__(self):
        self.scopes = [Scope()]

    def push_scope(self):
        self.scopes.append(Scope())

    def pop_scope(self):
        self.scopes.pop()

    def current_scope(self):
        return self.scopes[-1]

    def __getitem__(self, item):
        for scope in self.scopes[::-1]:
            if item in scope.variables:
                return scope.variables[item]
        raise KeyError(f"Variable {item} not found")

    def __setitem__(self, key, value):
        for scope in self.scopes[::-1]:
            if key in scope.variables:
                scope.variables[key] = value
                return
        raise KeyError(f"Variable {key} not found")

    # def push_function(self, key, value):
    #     self.currentScope().functions[key] = value
    #
    # def get_function(self, name):
    #     for scope in self.scopes[::-1]:
    #         if name in scope.functions:
    #             return scope.functions[name]
    #     raise KeyError(f"Function {name} not found")

    def __repr__(self):
        return f"Context({self.scopes})"


class Node(ABC):
    @abstractmethod
    def run(self, ctx: Context):
        pass


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
        out = None
        for statement in self.statements:
            out = statement.run(ctx)
        ctx.pop_scope()
        return out


class PrintStatement(Node):
    def __init__(self, value: Node):
        self.value = value

    def __repr__(self):
        return f"print {self.value}"

    def run(self, ctx: Context):
        print(self.value.run(ctx))
        return None