from lexer import Token, TokenKind
from interpreter.interpreter import Node, Block
from interpreter.datatypes import *
from interpreter.statements import *
from interpreter.binaryoperations import *
import logging


class Parser:
    def __init__(self, tokens: list[Token, ...], filename: str="<stdin>", start: int=0, logger: logging.Logger=None, logging_level: int=51, log_file: str=None):
        self.tokens = tokens
        self.filename = filename
        self.index = start
        self.current_token = self.tokens[self.index]
        self.next_token = self.tokens[self.index+1]
        if logger is None:
            self.logger = logger
            self.logger = logging.getLogger("Parser")
        else:
            self.logger = logger.getChild("Parser")
            logger.propagate = True
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
            if self.logger.getEffectiveLevel() >= logging.DEBUG:
                tmp = "[\n" + "\n".join([repr(token) for token in tokens[1:]]) + "\n]"
                self.logger.debug(f"Parser(\n{filename=},\n{start=},\n{logging_level=},\n{log_file=}\n,{tmp})")
        self.logger.info("Parser initialized successfully")

    def advance(self):
        self.index += 1
        if self.index >= len(self.tokens):
            self.current_token = None
            self.next_token = None
        elif self.index == len(self.tokens)-1:
            self.current_token = self.tokens[self.index]
            self.next_token = None
        else:
            self.current_token = self.tokens[self.index]
            self.next_token = self.tokens[self.index+1]
        self.logger.debug(f"Advanced to {self.current_token}")

    def consume(self, kind: TokenKind, error_message: str="Unexpected token"):
        if self.current_token.kind == kind:
            self.advance()
        else:
            raise SyntaxError(f"{error_message}: {self.current_token.kind} != {kind}")

    def parse(self) -> Node:
        return self.parse_block()

    def parse_block(self) -> Node:
        block = []
        while self.current_token is not None:
            block.append(self.parse_statement())
        return Block(block)

    def parse_statement(self) -> Node:
        match self.current_token.kind:
            case TokenKind.Print:
                self.advance()
                self.consume(TokenKind.LeftParen, "Expected '(' after 'print' statement")
                out = PrintStatement(self.parse_expression())
                self.consume(TokenKind.RightParen, "Expected ')' after 'print' statement")
                self.consume(TokenKind.NewLine, "Expected newline after 'print' statement")
                return out
        return self.parse_expression()

    def parse_expression(self) -> Node:
        return self.parse_assignment()

    def parse_assignment(self) -> Node:
        return self.parse_comparison()

    def parse_comparison(self) -> Node:
        return self.parse_additive()

    def parse_additive(self) -> Node:
        return self.parse_multiplicative()

    def parse_multiplicative(self) -> Node:
        return self.parse_atom()

    def parse_atom(self) -> Node:
        match self.current_token.kind:
            case TokenKind.StringLiteral:
                out = StringLiteral(self.current_token.value)
                self.advance()
                return out
            case TokenKind.IntegerLiteral:
                out = IntegerLiteral(int(self.current_token.value))
                self.advance()
                return out
            case TokenKind.FloatLiteral:
                out = FloatLiteral(float(self.current_token.value))
                self.advance()
                return out
            case TokenKind.BooleanLiteral:
                out = BooleanLiteral(self.current_token.value == "True")
                self.advance()
                return out
            case TokenKind.NullLiteral:
                out = NullLiteral()
                self.advance()
                return out
            case TokenKind.Identifier:
                raise NotImplementedError("Identifier parsing not implemented yet")