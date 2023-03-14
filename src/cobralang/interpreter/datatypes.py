from .interpreter import Context, Node


class StringLiteral(Node):
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return f'{self.value!r}'

    def run(self, ctx: Context):
        return String(self.value)


class IntegerLiteral(Node):
    def __init__(self, value: int):
        self.value = value

    def __repr__(self):
        return f'{self.value}'

    def run(self, ctx: Context):
        return Integer(self.value)


class FloatLiteral(Node):
    def __init__(self, value: float):
        self.value = value

    def __repr__(self):
        return f'{self.value}'

    def run(self, ctx: Context):
        return Float(self.value)


class BooleanLiteral(Node):
    def __init__(self, value: bool):
        self.value = value

    def __repr__(self):
        return str(self.value)

    def run(self, ctx: Context):
        return Boolean(self.value)


class NullLiteral(Node):
    def __init__(self):
        pass

    def __repr__(self):
        return 'null'

    def run(self, ctx: Context):
        return None


class Value:
    pass


class Integer(Value):
    def __init__(self, value: int):
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __add__(self, other):
        return Integer(self.value + other.value)

    def __sub__(self, other):
        return Integer(self.value - other.value)

    def __mul__(self, other):
        return Integer(self.value * other.value)

    def __truediv__(self, other):
        return Integer(self.value / other.value)

    def __lt__(self, other):
        return Boolean(self.value < other.value)

    def __gt__(self, other):
        return Boolean(self.value > other.value)

    def __eq__(self, other):
        return Boolean(self.value == other.value)

    def __mod__(self, other):
        return Integer(self.value % other.value)


class Float(Value):
    def __init__(self, value: float):
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __add__(self, other):
        return Float(self.value + other.value)

    def __sub__(self, other):
        return Float(self.value - other.value)

    def __mul__(self, other):
        return Float(self.value * other.value)

    def __truediv__(self, other):
        return Float(self.value / other.value)

    def __lt__(self, other):
        return Boolean(self.value < other.value)

    def __gt__(self, other):
        return Boolean(self.value > other.value)

    def __eq__(self, other):
        return Boolean(self.value == other.value)

    def __mod__(self, other):
        return Float(self.value % other.value)


class String(Value):
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return f'"{self.value}"'

    def __add__(self, other):
        return String(self.value + other.value)

    def __lt__(self, other):
        return Boolean(self.value < other.value)

    def __gt__(self, other):
        return Boolean(self.value > other.value)

    def __eq__(self, other):
        return Boolean(self.value == other.value)


class Boolean(Value):
    def __init__(self, value: bool):
        self.value = value

    def __repr__(self):
        return f'{self.value}'

    def __eq__(self, other):
        return Boolean(self.value == other.value)

    def __bool__(self):
        return self.value
