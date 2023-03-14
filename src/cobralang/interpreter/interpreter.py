from abc import ABC, abstractmethod


class Scope:
    def __init__(self):
        self.variables = {}
        self.functions = {}

    def __repr__(self):
        return f"Scope({self.variables}, {self.functions})"


class Context:
    def __init__(self):
        self.scopes = []
        self.functions = {}

    def push_scope(self):
        self.scopes.append(Scope())

    def pop_scope(self):
        self.scopes.pop()

    def push_function(self, key, value):
        self.current_scope().functions[key] = value

    def get_function(self, name):
        for scope in self.scopes[::-1]:
            if name in scope.functions:
                return scope.functions[name]
        raise KeyError(f"Function {name} not found")

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


class ReplContext(Context):
    def pop_scope(self):
        if len(self.scopes) == 1:
            return
        super().pop_scope()

    def push_scope(self):
        if len(self.scopes) == 1:
            return
        super().push_scope()


class Node(ABC):
    @abstractmethod
    def run(self, ctx: Context):
        pass
