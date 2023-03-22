# This code is licensed under the MIT License (see LICENSE file for details)
import logging
from dataclasses import dataclass
from enum import Enum, auto
from os.path import split
from os.path import isfile


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
    PlusPlus = auto()
    Minus = auto()
    MinusMinus = auto()
    Multiply = auto()
    Power = auto()
    Divide = auto()
    FloorDivide = auto()
    Mod = auto()
    Equal = auto()
    PlusEqual = auto()
    MinusEqual = auto()
    MultiplyEqual = auto()
    DivideEqual = auto()
    ModEqual = auto()

    # Comparison
    EqualEqual = auto()
    Not = auto()
    NotEqual = auto()
    Greater = auto()
    GreaterEqual = auto()
    Less = auto()
    LessEqual = auto()
    And = auto()
    Or = auto()
    In = auto()

    # Delimiters
    LeftParen = auto()
    RightParen = auto()
    LeftBrace = auto()
    RightBrace = auto()
    LeftBracket = auto()
    RightBracket = auto()
    Semicolon = auto()
    Colon = auto()
    Comma = auto()

    # Statements
    Import = auto()
    From = auto()
    Return = auto()
    Break = auto()
    Let = auto()
    Fn = auto()
    Var = auto()
    For = auto()

    # Blocks
    If = auto()
    Elif = auto()
    Else = auto()
    While = auto()

    # EOF
    EOF = auto()


keywords = {
    "True": TokenKind.BooleanLiteral,
    "False": TokenKind.BooleanLiteral,
    "Null": TokenKind.NullLiteral,

    # comparison
    "not": TokenKind.Not,
    "and": TokenKind.And,
    "or": TokenKind.Or,
    "in": TokenKind.In,

    # statements
    "import": TokenKind.Import,
    "from": TokenKind.From,
    "return": TokenKind.Return,
    "break": TokenKind.Break,
    "let": TokenKind.Let,
    "fn": TokenKind.Fn,
    "var": TokenKind.Var,

    # blocks
    "if": TokenKind.If,
    "elif": TokenKind.Elif,
    "else": TokenKind.Else,
    "while": TokenKind.While,
    "for": TokenKind.For,
}

single_character_tokens = {
    "=": TokenKind.Equal,
    "(": TokenKind.LeftParen,
    ")": TokenKind.RightParen,
    "{": TokenKind.LeftBrace,
    "}": TokenKind.RightBrace,
    "[": TokenKind.LeftBracket,
    "]": TokenKind.RightBracket,
    ":": TokenKind.Colon,
    ",": TokenKind.Comma,
    "|": TokenKind.Or,
    "&": TokenKind.And,
}


@dataclass
class Token:
    kind: TokenKind
    position_end: Position
    position_start: Position
    value: str = None
    space_after: bool = False
    newline_after: bool = False

    def __repr__(self):
        if self.value:
            return f"Token({self.kind}, {self.value!r}, {self.space_after=}, {self.newline_after=})"
        return f"Token({self.kind}, {self.space_after=}, {self.newline_after=})"


class LexerError(Exception):
    def __init__(self, message: str, position_start: Position, position_end: Position):
        self.position_start = position_start
        self.position_end = position_end
        self.message = message
        super().__init__(message)


class InvalidFloatError(LexerError):
    pass


class InvalidSyntaxError(LexerError):
    pass


class IllegalCharError(LexerError):
    pass


class InvalidStringError(LexerError):
    pass


def make_lexer_from_file_path(file_path: str, logger: logging.Logger=None, logging_level: int=51, log_file: str=None):
    if not isfile(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist")
    with open(file_path) as file:
        text = file.read()
    return Lexer(text, f"<{split(file_path)[-1]}>", logger, logging_level, log_file)


class Lexer:
    def __init__(self, text: str, filename: str="<stdin>", logger: logging.Logger=None, logging_level: int=51, log_file: str=None):
        self.filename = filename
        self.text = text
        if self.text == "":
            raise ValueError("Cannot initialize lexer with empty text")
        self.current_char = None
        self.position = Position(-1, 1, 0)
        if logger is None:
            self.logger = logger
            self.logger = logging.getLogger("Lexer")
        else:
            self.logger = logger.getChild("Lexer")
            self.logger.propagate = True
        self.logger.setLevel(logging_level)
        if not self.logger.hasHandlers():
            formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
            if log_file is not None:
                file_handler = logging.FileHandler(log_file)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            else:
                stream_handler = logging.StreamHandler()
                stream_handler.setFormatter(formatter)
                self.logger.addHandler(stream_handler)
        self.logger.debug(f"Lexer(\n{filename=},\n{logging_level=},\n{log_file=}\n)")
        self.logger.info("Lexer initialized successfully")
        self.advance()

    def advance(self):
        if self.position >= len(self.text)-1:
            self.logger.debug("Reached end of file")
            self.current_char = None
        else:
            self.position.index += 1
            self.position.column += 1
            self.current_char = self.text[self.position.index]
            if self.current_char == "\n":
                self.position.line += 1
                self.position.column = 0
        self.logger.debug(f"Advanced to {self.position}")

    def tokenize(self) -> list[Token]:
        # Initialize tokens list, EOF token is only there so that we can always access tokens[-1], removed at return
        tokens = [Token(TokenKind.EOF, Position(-1, 0, -1), Position(-1, 0, -1))]

        def make_position() -> Position:
            return Position(self.position.index, self.position.line, self.position.column)

        def push_token(kind: TokenKind, _value: str, _start: Position=None):
            tokens.append(Token(
                kind, position_end=make_position(), position_start=_start or make_position(), value=_value
            ))
            self.logger.debug(f"Pushed {tokens[-1]}) to stack")

        while self.current_char is not None:
            match self.current_char:
                case "\n" | ";":
                    self.logger.debug(f"Found newline, updating {tokens[-1]}.newline_after to True")
                    tokens[-1].newline_after = True
                    self.advance()
                case char if char.isspace():
                    self.logger.debug(f"Found whitespace, updating {tokens[-1]}.space_after to True")
                    tokens[-1].space_after = True
                    self.advance()
                # Special characters
                case "!":
                    self.logger.debug("Found !, checking for not equal")
                    self.advance()
                    if self.current_char == "=":
                        self.logger.debug("Found !=, pushing NotEqual token to stack")
                        tokens.append(Token(TokenKind.NotEqual, position_end=make_position(), position_start=make_position()))
                        self.advance()
                    else:
                        self.logger.debug("Found !, pushing Not token to stack")
                        tokens.append(Token(TokenKind.Not, position_end=make_position(), position_start=make_position()))
                case "#":
                    self.logger.debug("Found #, skipping to end of line")
                    while self.current_char != "\n":
                        self.advance()
                case "=":
                    self.logger.debug("Found =, checking for equality")
                    self.advance()
                    if self.current_char == "=":
                        self.logger.debug("Found ==, pushing Equals token to stack")
                        tokens.append(Token(TokenKind.EqualEqual, position_end=make_position(), position_start=make_position()))
                        self.advance()
                    else:
                        self.logger.debug("Found =, pushing Assign token to stack")
                        tokens.append(Token(TokenKind.Equal, position_end=make_position(), position_start=make_position()))
                case char if char == "<" or char == ">":
                    self.logger.debug(f"Found {self.current_char}, checking for equality")
                    self.advance()
                    if self.current_char == "=":
                        self.logger.debug(f"Found {self.current_char}, pushing {self.current_char}{self.current_char} token to stack")
                        tokens.append(Token(
                            TokenKind.LessEqual if char == "<" else TokenKind.GreaterEqual,
                            position_end=make_position(), position_start=make_position()
                        ))
                        self.advance()
                    else:
                        self.logger.debug(f"Found {self.current_char}, pushing {self.current_char} token to stack")
                        tokens.append(Token(
                            TokenKind.Less if char == "<" else TokenKind.Greater,
                            position_end=make_position(), position_start=make_position()
                        ))
                case char if char == "+" or char == "-":
                    self.logger.debug(f"Found {self.current_char}, checking for equals")
                    self.advance()
                    if self.current_char == "=":
                        self.logger.debug(f"Found {self.current_char}, pushing {self.current_char}{self.current_char} token to stack")
                        tokens.append(Token(
                            TokenKind.PlusEqual if char == "+" else TokenKind.MinusEqual,
                            position_end=make_position(), position_start=make_position()
                        ))
                        self.advance()
                    elif self.current_char == char:
                        self.logger.debug(f"Found {self.current_char}, pushing {self.current_char}{self.current_char} token to stack")
                        tokens.append(Token(
                            TokenKind.PlusPlus if char == "+" else TokenKind.MinusMinus,
                            position_end=make_position(), position_start=make_position()
                        ))
                        self.advance()
                    else:
                        self.logger.debug(f"Found {self.current_char}, pushing {self.current_char} token to stack")
                        tokens.append(Token(
                            TokenKind.Plus if char == "+" else TokenKind.Minus,
                            position_end=make_position(), position_start=make_position()
                        ))
                case char if char == "*" or char == "/" or char == "%":
                    self.logger.debug(f"Found {self.current_char}, checking for equals")
                    self.advance()
                    if self.current_char == "=":
                        self.logger.debug(f"Found =, pushing {char}= token to stack")
                        tokens.append(Token(
                            TokenKind.MultiplyEqual if char == "*" else TokenKind.DivideEqual if char == "/" else TokenKind.ModEqual,
                            position_end=make_position(), position_start=make_position()
                        ))
                        self.advance()
                    elif self.current_char == "*" and char=="*":
                        self.logger.debug(f"Found *, pushing ** token to stack")
                        tokens.append(Token(TokenKind.Power, position_end=make_position(), position_start=make_position()))
                        self.advance()
                    elif self.current_char == "/" and char=="/":
                        self.logger.debug(f"Found /, pushing // token to stack")
                        tokens.append(Token(TokenKind.FloorDivide, position_end=make_position(), position_start=make_position()))
                        self.advance()
                    else:
                        self.logger.debug(f"Found {self.current_char}, pushing {self.current_char} token to stack")
                        tokens.append(Token(
                            TokenKind.Multiply if char == "*" else TokenKind.Divide if char == "/" else TokenKind.Mod,
                            position_end=make_position(), position_start=make_position()
                        ))
                # All characters
                case char if char in single_character_tokens:
                    self.logger.debug(f"Pushing Token({single_character_tokens[char]}) to stack")
                    tokens.append(Token(
                        single_character_tokens[char], position_end=make_position(), position_start=make_position()
                    ))
                    self.advance()
                case char if char.isdigit() or char == ".":
                    self.logger.debug("Found digit, parsing integer or float literal")
                    start = self.position
                    dot = char == "."
                    value = char
                    self.advance()
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
                    self.logger.debug("Found letter, parsing identifier or keyword")
                    start = self.position
                    value = ""
                    while self.current_char is not None and (self.current_char.isalnum() or self.current_char == "_"):
                        value += self.current_char
                        self.advance()
                    push_token(keywords.get(value, TokenKind.Identifier), value, start)
                case char if char=="'" or char=='"':
                    self.logger.debug("Found quote, parsing string literal")
                    start = self.position
                    value = ""
                    multi_line = False
                    self.advance()
                    if self.current_char == "*":
                        multi_line = True
                        self.advance()
                        if self.current_char == "\n":
                            self.advance()
                    while self.current_char is not None and self.current_char != char:
                        if self.current_char == "\\":
                            self.advance()
                            if self.current_char == "n":
                                value += "\n"
                            elif self.current_char == "t":
                                value += "\t"
                            elif self.current_char == char:
                                value += char
                            else:
                                value += "\\" + self.current_char
                        elif self.current_char == '*' and multi_line:
                            self.advance()
                            if self.current_char != char:
                                value += "*"
                            else:
                                break
                        elif self.current_char == "\n" and not multi_line:
                            break
                        else:
                            value += self.current_char
                        self.advance()
                    if self.current_char is not char:
                        self.logger.error(f"Unterminated string literal at {start}")
                        raise InvalidStringError(f"Unterminated string literal at {start}", start, self.position)
                    self.advance()
                    push_token(TokenKind.StringLiteral, value, start)
                case char:
                    self.logger.error(f"Illegal character '{char}' at {self.position}")
                    raise IllegalCharError(f"Illegal character '{char}' at {self.position}", self.position, self.position)
        tokens[-1].newline_after = True
        self.logger.debug("Reached end of file, returning tokens")
        if self.logger.getEffectiveLevel() >= logging.DEBUG:
            tmp = "[\n" + "\n".join([repr(token) for token in tokens[1:]]) + "\n]"
            self.logger.debug(f"Tokens: {tmp}")
        return tokens[1:]
