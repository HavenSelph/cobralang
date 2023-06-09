# This code is licensed under the MIT License (see LICENSE file for details)
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
        self.register_builtins()

    def clear_context(self, keep_functions=True, no_warning=False):
        if not no_warning and len(self.scopes) > 2:
            print("Warning: Clearing context within higher scopes can cause side effects, use with caution.")
        for scope in self.scopes:
            scope.variables = {}
            if not keep_functions:
                self.scopes[0].functions = {}
        self.register_builtins()

    def register_builtins(self):
        from .builtins import std_functions
        for name, function in std_functions.items():
            self.scopes[0].functions[name] = function

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


class Node(ABC):
    @abstractmethod
    def run(self, ctx: Context):
        pass
