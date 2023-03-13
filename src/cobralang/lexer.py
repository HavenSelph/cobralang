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
    Minus = auto()
    Multiply = auto()
    Divide = auto()
    Equal = auto()

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

    # Misc
    SOF = auto()


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
    "{": TokenKind.LeftBrace,
    "}": TokenKind.RightBrace,
    "[": TokenKind.LeftBracket,
    "]": TokenKind.RightBracket,
    ";": TokenKind.Semicolon,
    ":": TokenKind.Colon,
    ",": TokenKind.Comma,
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
            return f"Token({self.kind}, {self.value!r})"
        return f"Token({self.kind})"


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


def make_lexer_from_file_path(file_path: str, start: int=0, logger: logging.Logger=None, logging_level: int=51, log_file: str=None):
    if not isfile(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist")
    with open(file_path) as file:
        text = file.read()
    return Lexer(text, f"<{split(file_path)[-1]}>", start, logger, logging_level, log_file)


class Lexer:
    def __init__(self, text: str, filename: str="<stdin>", start: int=0, logger: logging.Logger=None, logging_level: int=51, log_file: str=None):
        self.filename = filename
        self.text = text
        if self.text == "":
            raise ValueError("Cannot initialize lexer with empty text")
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
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
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
        # Initialize tokens list, SOF token is only there so that we can always access tokens[-1]
        tokens = [Token(TokenKind.SOF, Position(-1, 0, -1), Position(-1, 0, -1))]

        def push_token(kind: TokenKind, value: str, start: Position=None):
            tokens.append(Token(
                kind, position_end=self.position, position_start=start or self.position, value=value
            ))
            self.logger.debug(f"Pushed {tokens[-1]}) to stack")

        while self.current_char is not None:
            match self.current_char:
                case "\n":
                    self.logger.debug(f"Found newline, updating {tokens[-1]}.new_line_after to True")
                    tokens[-1].new_line_after = True
                    self.advance()
                case " ":
                    self.logger.debug(f"Found whitespace, updating {tokens[-1]}.space_after to True")
                    tokens[-1].space_after = True
                    self.advance()
                case char if char in single_character_tokens:
                    self.logger.debug(f"Pushing Token({single_character_tokens[char]}) to stack")
                    tokens.append(Token(
                        single_character_tokens[char], position_end=self.position, position_start=self.position
                    ))
                    self.advance()
                case char if char.isdigit():
                    self.logger.debug("Found digit, parsing integer or float literal")
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
                    self.advance()
                    while self.current_char is not None and (self.current_char != char):
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
                        else:
                            value += self.current_char
                        self.advance()
                    if self.current_char is None:
                        self.logger.error(f"Unterminated string literal at {start}")
                        raise InvalidStringError(f"Unterminated string literal at {start}", start, self.position)
                    self.advance()
                    push_token(TokenKind.StringLiteral, value, start)
                case char:
                    self.logger.error(f"Illegal character '{char}' at {self.position}")
                    raise IllegalCharError(f"Illegal character '{char}' at {self.position}", self.position, self.position)
        self.logger.debug("Reached end of file, returning tokens")
        if self.logger.getEffectiveLevel() >= logging.DEBUG:
            tmp = "[\n" + "\n".join([repr(token) for token in tokens[1:]]) + "\n]"
            self.logger.debug(f"Tokens: {tmp}")
        return tokens[1:]


make_lexer_from_file_path("./test.txt", logging_level=logging.DEBUG).tokenize()
