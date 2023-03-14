from .interpreter import Node, Context


class PrintStatement(Node):
    def __init__(self, value: Node):
        self.value = value

    def __repr__(self):
        return f"print {self.value}"

    def run(self, ctx: Context):
        print(self.value.run(ctx))
        return None
