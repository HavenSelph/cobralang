import logging
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Literals
    StringLiteral = auto()
    IntegerLiteral = auto()
    FloatLiteral = auto()
    BooleanLiteral = auto()
    NullLiteral = auto()

    # Identifiers
    Identifier = auto()

    # Operators
    Plus = auto()
    Minus = auto()
    Multiply = auto()
    Divide = auto()
    Equal = auto()

    # Delimiters
    LeftParen = auto()
    RightParen = auto()
    Semicolon = auto()
    Colon = auto()


@dataclass
class Position:
    index: int
    line: int
    column: int

    def __repr__(self):
        return f"Position({self.line}, {self.column})"


@dataclass
class Token:
    type: TokenType
    value: str = None
    position_start: Position = None
    position_end: Position = position_start

    def __repr__(self):
        if self.value:
            return f"Token({self.type}, {self.value})"
        return f"Token({self.type})"


