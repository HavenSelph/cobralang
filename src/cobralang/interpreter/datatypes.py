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


class ListLiteral(Node):
    def __init__(self, elements: list):
        self.elements = elements

    def __repr__(self):
        return f'[{", ".join([str(i) for i in self.elements])}]'

    def run(self, ctx: Context):
        return List([i.run(ctx) for i in self.elements])


class TupleLiteral(Node):
    def __init__(self, elements: list):
        self.elements = elements

    def __repr__(self):
        return f'({", ".join([str(i) for i in self.elements])})'

    def run(self, ctx: Context):
        return Tuple(tuple([i.run(ctx) for i in self.elements]))


class Value:
    def __init__(self, value):
        self.value = value


class List(Value):
    def __init__(self, value: list):
        super().__init__(value)

    def __repr__(self):
        return f'[{", ".join([str(i) for i in self.value])}]'

    def __str__(self):
        return self.__repr__()

    def __bool__(self):
        return len(self.value) != 0

    def __add__(self, other: Value):
        return List(self.value + other.value)

    def __getitem__(self, item: Value):
        return self.value[item.value]

    def __setitem__(self, key: Value, value: Value):
        self.value[key.value] = value

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return iter(self.value)

    def __contains__(self, item: Node):
        return item in self.value

    def __eq__(self, other):
        return Boolean(self.value == other.value)

    def __ne__(self, other):
        return Boolean(self.value != other.value)


class Tuple(Value):
    def __init__(self, value: tuple):
        super().__init__(value)

    def __repr__(self):
        return f'({", ".join([str(i) for i in self.value])})'

    def __str__(self):
        return self.__repr__()

    def __bool__(self):
        return len(self.value) != 0

    def __add__(self, other: Value):
        return Tuple(self.value + other.value)

    def __getitem__(self, item: Value):
        return self.value[item.value]

    def __setitem__(self, key: Value, value: Value):
        raise TypeError('Tuples are immutable')

    def __len__(self):
        return len(self.value)

    def __iter__(self):
        return iter(self.value)

    def __contains__(self, item: Node):
        return item in self.value

    def __eq__(self, other):
        return Boolean(self.value == other.value)

    def __ne__(self, other):
        return Boolean(self.value != other.value)


class Dict(Value):
    # TODO: Implement
    pass


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

    def __pos__(self):
        return Integer(self.value)

    def __neg__(self):
        return Integer(-self.value)


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

    def __pos__(self):
        return Float(self.value)

    def __neg__(self):
        return Float(-self.value)


class String(Value):
    def __init__(self, value: str):
        super().__init__(value)

    def __repr__(self):
        return f'"{self.value}"'

    def __str__(self):
        return self.value

    def __bool__(self):
        return self.value!=""

    def __len__(self):
        return len(self.value)

    def __getitem__(self, item: Value):
        return self.value[item.value]

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

