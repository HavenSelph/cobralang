import logging
from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class Position:
    index: int
    line: int
    column: int

    def __gt__(self, other):
        if isinstance(other, Position):
            return self.index > other.index
        return self.index > other

    def __ge__(self, other):
        if isinstance(other, Position):
            return self.index >= other.index
        return self.index >= other

    def __lt__(self, other):
        if isinstance(other, Position):
            return self.index < other.index
        return self.index < other

    def __le__(self, other):
        if isinstance(other, Position):
            return self.index <= other.index
        return self.index <= other

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.index == other.index
        return self.index == other

    def __ne__(self, other):
        if isinstance(other, Position):
            return self.index != other.index
        return self.index != other

    def __repr__(self):
        return f"Position({self.line}, {self.column})"


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

    # Misc
    SOF = auto()
    EOF = auto()


keywords = {
    "True": TokenType.BooleanLiteral,
    "False": TokenType.BooleanLiteral,
    "Null": TokenType.NullLiteral
}

single_character_tokens = {
    "+": TokenType.Plus,
    "-": TokenType.Minus,
    "*": TokenType.Multiply,
    "/": TokenType.Divide,
    "=": TokenType.Equal,
    "(": TokenType.LeftParen,
    ")": TokenType.RightParen,
    ";": TokenType.Semicolon,
    ":": TokenType.Colon,
}


@dataclass
class Token:
    type: TokenType
    value: str = None
    space_after: bool = False
    new_line_after: bool = False
    position_start: Position = None
    position_end: Position = position_start

    def __repr__(self):
        if self.value:
            return f"Token({self.type}, {self.value})"
        return f"Token({self.type})"


class Lexer:
    def __init__(self, filename: str, text: str, start: int = 0, logger: logging.Logger = None, logging_level: int = 51, log_file: str = None):
        self.filename = filename
        self.text = text
        self.current_char = None
        self.position = Position(start-1, 0, start-1)
        self.advance()
        if logger is None:
            self.logger = logger
            self.logger = logging.getLogger("Lexer")
        else:
            self.logger = logger.getChild("Lexer")
        self.logger.setLevel(logging_level)
        formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
        if log_file is not None:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        else:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)
        self.logger.info("Lexer initialized successfully")
        self.logger.debug(f"Lexer (\n\t{filename=},\n\t{start=},\n\t{logging_level=},\n\t{log_file=}\n)")

    def advance(self):
        if self.position >= len(self.text)-1:
            self.logger.debug("Reached end of file")
            self.current_char = None
        else:
            self.position.index += 1
            self.current_char = self.text[self.position.index]
            if self.current_char == "\n":
                self.position.line += 1
                self.position.column = 0

    def tokenize(self):
        tokens = [Token(TokenType.SOF, position_start=self.position)]
        while self.current_char is not None:
            match self.current_char:
                case "\n":
                    tokens[-1].new_line_after = True
                    self.advance()
                case " ":
                    tokens[-1].space_after = True
                    self.advance()

        return tokens[1:]
