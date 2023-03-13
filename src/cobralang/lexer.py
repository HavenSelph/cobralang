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
        return f"Position({self.line}:{self.column})"


class TokenKind(Enum):
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
    "True": TokenKind.BooleanLiteral,
    "False": TokenKind.BooleanLiteral,
    "Null": TokenKind.NullLiteral
}

single_character_tokens = {
    "+": TokenKind.Plus,
    "-": TokenKind.Minus,
    "*": TokenKind.Multiply,
    "/": TokenKind.Divide,
    "=": TokenKind.Equal,
    "(": TokenKind.LeftParen,
    ")": TokenKind.RightParen,
    ";": TokenKind.Semicolon,
    ":": TokenKind.Colon,
}


@dataclass
class Token:
    kind: TokenKind
    position_end: Position
    position_start: Position
    value: str = None
    space_after: bool = False
    new_line_after: bool = False

    def __repr__(self):
        if self.value:
            return f"Token({self.kind}, {self.value})"
        return f"Token({self.kind})"


class LexerError(Exception):
    def __init__(self, message: str, position_start: Position, position_end: Position):
        self.position_start = position_start
        self.position_end = position_end
        self.message = message
        super().__init__(message)


class InvalidFloatError(LexerError):
    pass


class IllegalCharError(LexerError):
    pass


class Lexer:
    def __init__(self, filename: str, text: str, start: int=0, logger: logging.Logger=None, logging_level: int=51, log_file: str=None):
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
        tokens = [Token(TokenKind.SOF, Position(-1, 0, -1), Position(-1, 0, -1))]

        def push_token(kind: TokenKind, value: str, start: Position=None):
            tokens.append(Token(
                kind, position_end=self.position, position_start=start or self.position, value=value
            ))

        while self.current_char is not None:
            match self.current_char:
                case "\n":
                    tokens[-1].new_line_after = True
                    self.advance()
                case " ":
                    tokens[-1].space_after = True
                    self.advance()
                case char if char in single_character_tokens:
                    tokens.append(Token(
                        single_character_tokens[char], position_end=self.position, position_start=self.position
                    ))
                    self.advance()
                case char if char.isdigit():
                    start = self.position
                    value = ""
                    dot = False
                    while self.current_char is not None and (self.current_char.isdigit() or self.current_char == "."):
                        if self.current_char == ".":
                            if dot:
                                self.logger.error(f"Invalid float literal at {self.position}")
                                raise InvalidFloatError(f"Invalid float literal at {self.position}", start, self.position)
                            dot = True
                        value += self.current_char
                        self.advance()
                    push_token(TokenKind.FloatLiteral if dot else TokenKind.IntegerLiteral, value, start)
                case char if char.isalpha():
                    start = self.position
                    value = ""
                    while self.current_char is not None and (self.current_char.isalnum() or self.current_char == "_"):
                        value += self.current_char
                        self.advance()
                    push_token(keywords.get(value, TokenKind.Identifier), value, start)
                case char:
                    self.logger.error(f"Illegal character '{char}' at {self.position}")
                    raise IllegalCharError(f"Illegal character '{char}' at {self.position}", self.position, self.position)
        return tokens[1:]
