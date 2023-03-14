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
    def __init__(self, value):
        self.value = value


class Integer(Value):
    def __init__(self, value: int):
        super().__init__(value)

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return self.__repr__()

    def __float__(self):
        return float(self.value)

    def __bool__(self):
        return self.value == 0

    def __add__(self, other):
        return Integer(self.value + other.value)

    def __sub__(self, other):
        return Integer(self.value - other.value)

    def __mul__(self, other):
        return Integer(self.value * other.value)

    def __pow__(self, power, modulo=None):
        return Integer(self.value ** power.value)

    def __truediv__(self, other):
        return Float(self.value / other.value)

    def __floordiv__(self, other):
        return Integer(self.value // other.value)

    def __floor__(self):
        return Integer(self.value // 1)

    def __ceil__(self):
        return Integer(self.value // 1 + 1)

    def __lt__(self, other):
        return Boolean(self.value < other.value)

    def __le__(self, other):
        return Boolean(self.value <= other.value)

    def __gt__(self, other):
        return Boolean(self.value > other.value)

    def __ge__(self, other):
        return Boolean(self.value >= other.value)

    def __eq__(self, other):
        return Boolean(self.value == other.value)

    def __mod__(self, other):
        return Integer(self.value % other.value)


class Float(Value):
    def __init__(self, value: float):
        super().__init__(value)

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return self.__repr__()

    def __bool__(self):
        return self.value != 0.0

    # rt

    def __add__(self, other):
        return Float(self.value + other.value)

    def __sub__(self, other):
        return Float(self.value - other.value)

    def __mul__(self, other):
        return Float(self.value * other.value)

    def __pow__(self, power, modulo=None):
        return Float(self.value ** power.value)

    def __truediv__(self, other):
        return Float(self.value / other.value)

    def __floordiv__(self, other):
        return Float(self.value // other.value)

    def __floor__(self):
        return Float(self.value // 1)

    def __ceil__(self):
        return Float(self.value // 1 + 1)

    def __lt__(self, other):
        return Boolean(self.value < other.value)

    def __le__(self, other):
        return Boolean(self.value <= other.value)

    def __gt__(self, other):
        return Boolean(self.value > other.value)

    def __ge__(self, other):
        return Boolean(self.value >= other.value)

    def __eq__(self, other):
        return Boolean(self.value == other.value)

    def __mod__(self, other):
        return Float(self.value % other.value)


class String(Value):
    def __init__(self, value: str):
        super().__init__(value)

    def __repr__(self):
        return f'"{self.value}"'

    def __str__(self):
        return self.value

    def __bool__(self):
        return self.value!=""

    # rt

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
        super().__init__(value)

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return self.__repr__()

    # rt
    def __int__(self):
        if self.value:
            return Integer(1)
        return Integer(0)

    def __eq__(self, other):
        return Boolean(self.value == other.value)

    def __bool__(self):
        return self.value


class Null(Value):
    def __init__(self):
        super().__init__(value=None)

    def __repr__(self):
        return 'null'

    # rt
    def __bool__(self):
        return Boolean(False)

    def __eq__(self, other):
        return Boolean(self.value == other.value)

