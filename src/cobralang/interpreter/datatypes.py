# This code is licensed under the MIT License (see LICENSE file for details)
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
        return Null()


class ListLiteral(Node):
    def __init__(self, elements: list):
        self.elements = elements

    def __repr__(self):
        return f'[{", ".join([str(i) for i in self.elements])}]'

    def run(self, ctx: Context):
        return List([i.run(ctx) for i in self.elements])


class TupleLiteral(Node):
    def __init__(self, elements: tuple):
        self.elements = elements

    def __repr__(self):
        return f'({", ".join([str(i) for i in self.elements])})'

    def run(self, ctx: Context):
        return Tuple(tuple([i.run(ctx) for i in self.elements]))


class DictionaryLiteral(Node):
    def __init__(self, elements: list):
        self.elements = elements

    def __repr__(self):
        return f'{{{", ".join([str(i) for i in self.elements])}}}'

    def run(self, ctx: Context):
        return Dict({item[0].run(ctx): item[1].run(ctx) for item in self.elements})


class SliceLiteral(Node):
    def __init__(self, start: Node, end: Node):
        self.start = start
        self.end = end

    def __repr__(self):
        return f'{self.start}:{self.end}'

    def run(self, ctx: Context):
        return Slice(self.start.run(ctx), self.end.run(ctx))


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

    def __hash__(self):
        return hash(self.value)


class Dict(Value):
    def __init__(self, value: dict):
        super().__init__(value)

    def __repr__(self):
        return f'{{{", ".join([f"{str(k)}: {str(v)}" for k, v in self.value.items()])}}}'

    def __str__(self):
        return self.__repr__()

    def __bool__(self):
        return len(self.value) != 0

    def __getitem__(self, item: Value):
        try:
            return self.value[item]
        except KeyError as e:
            raise KeyError(f'Key {item} not found in dictionary') from e

    def __setitem__(self, key: Value, value: Value):
        self.value[key] = value

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

    def __hash__(self):
        return hash(self.value)


class Float(Value):
    def __init__(self, value: float):
        super().__init__(value)

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return self.__repr__()

    # rt
    def __bool__(self):
        return self.value != 0.0

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

    def __hash__(self):
        return hash(self.value)


class String(Value):
    def __init__(self, value: str):
        super().__init__(value)

    def __repr__(self):
        return self.value.__repr__()

    def __str__(self):
        return self.value

    def __bool__(self):
        return self.value!=""

    def __len__(self):
        return len(self.value)

    def __getitem__(self, item: Value):
        return String(self.value[item.value])

    # rt

    def __add__(self, other):
        return String(self.value + other.value)

    def __lt__(self, other):
        return Boolean(self.value < other.value)

    def __gt__(self, other):
        return Boolean(self.value > other.value)

    def __eq__(self, other):
        return Boolean(self.value == other.value)

    def __hash__(self):
        return hash(self.value)


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

    def __hash__(self):
        return hash(self.value)


class Null(Value):
    def __init__(self):
        super().__init__(value=None)

    def __repr__(self):
        return 'Null'

    # rt
    def __bool__(self):
        return Boolean(False)

    def __eq__(self, other):
        return Boolean(self.value == other.value)


class Slice(Value):
    def __init__(self, start: Value, stop: Value):
        super().__init__(value=slice(start.value, stop.value))

    def __repr__(self):
        return f'{self.value[0]}:{self.value[1]}'

    def __str__(self):
        return self.__repr__()
