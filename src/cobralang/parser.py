from . import lexer
from .interpreter.interpreter import Node
from .interpreter.datatypes import *
from .interpreter.statements import *
from .interpreter import nodes, binaryoperations, unaryoperations
import logging


class Parser:
    def __init__(self, tokens: list[lexer.Token, ...], filename: str="<stdin>", logger: logging.Logger=None, logging_level: int=51, log_file: str=None):
        self.tokens = tokens
        self.filename = filename
        self.index = -1
        self.current_token = None
        self.next_token = None
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
                self.logger.debug(f"Parser(\n{filename=},\n{logging_level=},\n{log_file=}\n,{tmp})")
        self.logger.info("Parser initialized successfully")
        self.advance()

    def advance(self):
        self.logger.debug(f"Advancing index from {self.index} to {self.index+1}")
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
        self.logger.debug(f"Current token is now {self.current_token}")

    def consume(self, kind: lexer.TokenKind, error_message: str="Unexpected token"):
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
            if self.current_token is not None and not self.tokens[self.index-1].newline_after:
                raise SyntaxError(f"Expected newline after {block[-1]}")
            self.logger.debug(f"Pushed {block[-1]} to block")
        return nodes.Block(block)

    def parse_statement(self) -> Node:
        match self.current_token.kind:
            case lexer.TokenKind.Let:
                self.logger.debug("Parsing let statement")
                self.advance()
                name = self.current_token.value
                self.consume(lexer.TokenKind.Identifier, "Expected identifier after 'let' statement")
                self.consume(lexer.TokenKind.Equal, "Expected '=' after identifier in 'let' statement")
                value = self.parse_expression()
                out = nodes.VariableDeclaration(name, value)
                self.logger.debug(f"Returning {out}")
                return out
            case lexer.TokenKind.Print:
                self.logger.debug("Parsing print statement")
                self.advance()
                self.consume(lexer.TokenKind.LeftParen, "Expected '(' after 'print' statement")
                out = PrintStatement(self.parse_expression())
                self.consume(lexer.TokenKind.RightParen, "Expected ')' after 'print' statement")
                self.logger.debug(f"Returning {out}")
                return out
            case lexer.TokenKind.Return:
                self.logger.debug("Parsing return statement")
                self.advance()
                out = ReturnStatement(self.parse_expression())
                self.logger.debug(f"Returning {out}")
                return out
        return self.parse_expression()

    def parse_expression(self) -> Node:
        return self.parse_assignment()

    def parse_assignment(self) -> Node:
        left = self.parse_comparison()
        if self.current_token is not None and self.current_token.kind == lexer.TokenKind.Equal:
            self.advance()
            left = nodes.Assignment(left, self.parse_assignment())
        return left

    def parse_comparison(self) -> Node:
        left = self.parse_additive()
        if self.current_token is not None and self.current_token.kind in (lexer.TokenKind.EqualEqual, lexer.TokenKind.NotEqual, lexer.TokenKind.Less, lexer.TokenKind.LessEqual, lexer.TokenKind.Greater, lexer.TokenKind.GreaterEqual):
            match self.current_token.kind:
                case lexer.TokenKind.EqualEqual:
                    self.advance()
                    left = binaryoperations.Equals(left, self.parse_comparison())
                case lexer.TokenKind.NotEqual:
                    self.advance()
                    left = binaryoperations.NotEquals(left, self.parse_comparison())
                case lexer.TokenKind.Less:
                    self.advance()
                    left = binaryoperations.LessThan(left, self.parse_comparison())
                case lexer.TokenKind.LessEqual:
                    self.advance()
                    left = binaryoperations.LessThanOrEqual(left, self.parse_comparison())
                case lexer.TokenKind.Greater:
                    self.advance()
                    left = binaryoperations.GreaterThan(left, self.parse_comparison())
                case lexer.TokenKind.GreaterEqual:
                    self.advance()
                    left = binaryoperations.GreaterThanOrEqual(left, self.parse_comparison())
        return left

    def parse_additive(self) -> Node:
        left = self.parse_multiplicative()
        while self.current_token is not None and self.current_token.kind in (lexer.TokenKind.Plus, lexer.TokenKind.Minus):
            match self.current_token.kind:
                case lexer.TokenKind.Plus:
                    self.advance()
                    left = binaryoperations.Add(left, self.parse_multiplicative())
                case lexer.TokenKind.Minus:
                    self.advance()
                    left = binaryoperations.Subtract(left, self.parse_multiplicative())
        return left

    def parse_multiplicative(self) -> Node:
        left = self.parse_atom()
        while self.current_token is not None and self.current_token.kind in (lexer.TokenKind.Multiply, lexer.TokenKind.Divide):
            match self.current_token.kind:
                case lexer.TokenKind.Multiply:
                    self.advance()
                    left = binaryoperations.Multiply(left, self.parse_multiplicative())
                case lexer.TokenKind.Divide:
                    self.advance()
                    left = binaryoperations.Divide(left, self.parse_multiplicative())
        return left

    def parse_atom(self) -> Node:
        if self.current_token is None:
            raise SyntaxError("Unexpected end of file")
        match self.current_token.kind:
            case lexer.TokenKind.StringLiteral:
                out = StringLiteral(self.current_token.value)
                self.advance()
                self.logger.debug(f"Returning {out}")
                return out
            case lexer.TokenKind.IntegerLiteral:
                out = IntegerLiteral(int(self.current_token.value))
                self.advance()
                self.logger.debug(f"Returning {out}")
                return out
            case lexer.TokenKind.FloatLiteral:
                out = FloatLiteral(float(self.current_token.value))
                self.advance()
                self.logger.debug(f"Returning {out}")
                return out
            case lexer.TokenKind.BooleanLiteral:
                out = BooleanLiteral(self.current_token.value == "True")
                self.advance()
                self.logger.debug(f"Returning {out}")
                return out
            case lexer.TokenKind.NullLiteral:
                out = NullLiteral()
                self.advance()
                self.logger.debug(f"Returning {out}")
                return out
            case lexer.TokenKind.Identifier:
                name = nodes.VariableReference(self.current_token.value)
                self.advance()
                self.logger.debug(f"Returning {name}")
                return name
            case _:
                raise SyntaxError(f"Unexpected token: {self.current_token} {self.current_token.position_end}:{self.current_token.position_end}")
