from . import lexer
from .interpreter.datatypes import *
from .interpreter.statements import *
from .interpreter import nodes, binaryoperations, unaryoperations
from .interpreter.builtins import all_builtins
import logging


class Parser:
    def __init__(self, tokens: list[lexer.Token, ...], filename: str="<stdin>", logger: logging.Logger=None, logging_level: int=51, log_file: str=None):
        self.tokens = tokens
        self.filename = filename
        self.log_file = log_file
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

    def advance(self, i: int=1):
        self.logger.debug(f"Advancing index from {self.index} to {self.index+1}")
        self.index += i
        if self.index >= len(self.tokens):
            self.current_token = None
            self.next_token = None
        elif self.index == len(self.tokens)-1:
            self.current_token = self.tokens[self.index]
            self.next_token = None
        else:
            self.current_token = self.tokens[self.index]
            self.next_token = self.tokens[self.index+1]
        if self.current_token is not None:
            self.logger.debug(f"Current token is now {self.current_token}{self.current_token.position_end}:{self.current_token.position_start}")
        else:
            self.logger.debug("Current token is now None EOF")

    def consume(self, kind: lexer.TokenKind, error_message: str="Unexpected token"):
        if self.current_token is not None and self.current_token.kind == kind:
            self.advance()
        else:
            raise SyntaxError(f"{error_message}: {self.current_token} is not {kind}")

    def parse(self) -> Node:
        return self.parse_program()

    def parse_program(self) -> nodes.Program:
        block = []
        while self.current_token is not None:
            block.append(self.parse_statement())
            if self.current_token is not None and not self.tokens[self.index-1].newline_after and (self.next_token is not None and self.next_token.kind != lexer.TokenKind.RightBrace):
                raise SyntaxError(f"Expected newline after {block[-1]}")
            self.logger.debug(f"Pushed {block[-1]} to block")
        if self.logger.getEffectiveLevel() >= logging.DEBUG:
            program = "\n".join([repr(node) for node in block])
            self.logger.debug(f"Returning program:\nSTART OF {self.filename}\n{program}\nEND OF {self.filename}")
        return nodes.Program(block)

    def parse_block(self) -> Node | Block:
        block = []
        while self.current_token is not None and self.current_token.kind != lexer.TokenKind.RightBrace:
            block.append(self.parse_statement())
            if self.current_token is not None and not self.tokens[self.index-1].newline_after and (self.next_token is not None and self.next_token.kind != lexer.TokenKind.RightBrace):
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
            case lexer.TokenKind.Fn:
                self.logger.debug("Parsing function declaration")
                self.advance()
                name = self.current_token.value
                self.consume(lexer.TokenKind.Identifier, "Expected identifier after 'fn' statement")
                self.consume(lexer.TokenKind.LeftParen, "Expected '(' after identifier in 'fn' statement")
                args = []
                varargs = None
                kwargs = []
                varkwargs = None
                while self.current_token is not None and self.current_token.kind != lexer.TokenKind.RightParen:
                    match self.current_token.kind:
                        case lexer.TokenKind.Identifier if varkwargs is None:
                            arg = self.current_token.value
                            self.advance()
                            if self.current_token is not None and varkwargs is None and self.current_token.kind == lexer.TokenKind.Equal:
                                self.advance()
                                value = self.parse_expression()
                                kwargs.append((arg, value))
                            elif varargs is None and kwargs == [] and varkwargs is None:
                                args.append(arg)
                            else:
                                self.advance(-1)
                                raise SyntaxError(f"Unexpected token {self.current_token} in function definition")
                        case lexer.TokenKind.Multiply if varargs is None and kwargs == [] and varkwargs is None:
                            self.advance()
                            varargs = self.current_token.value
                            self.consume(lexer.TokenKind.Identifier, "Expected identifier after '*' in function definition")
                        case lexer.TokenKind.Power if varkwargs is None:
                            self.advance()
                            varkwargs = self.current_token.value
                            self.consume(lexer.TokenKind.Identifier, "Expected identifier after '**' in function definition")
                        case _:
                            raise SyntaxError(f"Unexpected token {self.current_token} in function definition")
                    if self.current_token is not None and self.current_token.kind == lexer.TokenKind.Comma:
                        self.advance()
                    else:
                        break
                self.consume(lexer.TokenKind.RightParen, "Expected ')' after arguments in 'fn' statement")
                self.consume(lexer.TokenKind.LeftBrace, "Expected '{' after arguments in 'fn' statement")
                body = nodes.FunctionBlock(self.parse_block().statements)
                self.consume(lexer.TokenKind.RightBrace, "Expected '}' after function body in 'fn' statement")
                out = nodes.FunctionDefinition(nodes.Function(name, args, varargs, {k:v for k,v in kwargs}, varkwargs, body))
                self.logger.debug(f"Returning {out}")
                return out
            case lexer.TokenKind.Import:
                self.logger.debug("Parsing import statement")
                self.advance()
                name = all_builtins.get(self.current_token.value, self.current_token.value)
                if name[-3:] != ".cb":
                    name += ".cb"
                self.consume(lexer.TokenKind.Identifier, "Expected identifier after 'import' statement")
                self.logger.debug(f"Attempting to locate file {name}")
                from pathlib import Path
                path = Path("./" + name).absolute()
                if not path.exists():
                    raise FileNotFoundError(f"File {name} not found")
                self.logger.debug(f"File {name} found")
                self.logger.debug(f"Attempting to parse file {name}")
                with open(path, "r") as f:
                    code = f.read()
                _lexer = lexer.Lexer(code, filename=f"<name>", logger=self.logger, logging_level=self.logger.getEffectiveLevel(), log_file=self.log_file)
                # insert tokens into token list
                # tmp = "[\n" + "\n".join([repr(token) for token in self.tokens]) + "\n]"
                tokens = _lexer.tokenize()
                self.tokens = self.tokens[:self.index] + tokens + self.tokens[self.index:]
                self.advance(0)
                self.logger.debug(f"File {name} added to token list")
                return self.parse_statement()
            # case lexer.TokenKind.Print:
            #     self.logger.debug("Parsing print statement")
            #     self.advance()
            #     self.consume(lexer.TokenKind.LeftParen, "Expected '(' after 'print' statement")
            #     out = PrintStatement(self.parse_expression())
            #     self.consume(lexer.TokenKind.RightParen, "Expected ')' after 'print' statement")
            #     self.logger.debug(f"Returning {out}")
            #     return out
            case lexer.TokenKind.Return:
                self.logger.debug("Parsing return statement")
                self.advance()
                out = ReturnStatement(self.parse_expression())
                self.logger.debug(f"Returning {out}")
                return out
            case lexer.TokenKind.Break:
                self.logger.debug("Parsing break statement")
                self.advance()
                out = ReturnStatement(NullLiteral())
                self.logger.debug(f"Returning {out}")
                return out
        return self.parse_block_statements()

    def parse_block_statements(self) -> Node:
        match self.current_token.kind:
            case lexer.TokenKind.If:
                self.logger.debug("Parsing if statement")
                self.advance()
                condition = self.parse_expression()
                self.consume(lexer.TokenKind.LeftBrace, "Expected '{' after condition in 'if' statement")
                if_body = self.parse_block()
                self.consume(lexer.TokenKind.RightBrace, "Expected '}' after body in 'if' statement")
                if_statement = [(condition, if_body),]
                while self.current_token is not None and self.current_token.kind == lexer.TokenKind.Elif:
                    self.advance()
                    condition = self.parse_expression()
                    self.consume(lexer.TokenKind.LeftBrace, "Expected '{' after condition in 'elif' statement")
                    elif_body = self.parse_block()
                    self.consume(lexer.TokenKind.RightBrace, "Expected '}' after body in 'elif' statement")
                    if_statement.append((condition, elif_body))
                if self.current_token is not None and self.current_token.kind == lexer.TokenKind.Else:
                    self.advance()
                    self.consume(lexer.TokenKind.LeftBrace, "Expected '{' after 'else' in 'if' statement")
                    else_body = self.parse_block()
                    self.consume(lexer.TokenKind.RightBrace, "Expected '}' after 'else' body in 'if' statement")
                    if_statement.append((BooleanLiteral(True), else_body))
                out = IfStatement(if_statement)
                self.logger.debug(f"Returning {out}")
                return out
            case lexer.TokenKind.While:
                self.logger.debug("Parsing while statement")
                self.advance()
                condition = self.parse_expression()
                self.consume(lexer.TokenKind.LeftBrace, "Expected '{' after condition in 'while' statement")
                body = self.parse_block()
                self.consume(lexer.TokenKind.RightBrace, "Expected '}' after body in 'while' statement")
                out = WhileStatement(condition, body)
                self.logger.debug(f"Returning {out}")
                return out
        return self.parse_assignment()

    def parse_assignment(self) -> Node:
        left = self.parse_expression()
        if self.current_token is not None and self.current_token.kind in (lexer.TokenKind.Equal, lexer.TokenKind.PlusEqual, lexer.TokenKind.MinusEqual, lexer.TokenKind.MultiplyEqual, lexer.TokenKind.DivideEqual, lexer.TokenKind.PlusPlus, lexer.TokenKind.MinusMinus, lexer.TokenKind.ModEqual):
            match self.current_token.kind:
                case lexer.TokenKind.PlusPlus:
                    self.advance()
                    right = binaryoperations.Add(left, IntegerLiteral(1))
                case lexer.TokenKind.MinusMinus:
                    self.advance()
                    right = binaryoperations.Subtract(left, IntegerLiteral(1))
                case lexer.TokenKind.Equal:
                    self.advance()
                    right = self.parse_comparison()
                case lexer.TokenKind.PlusEqual:
                    self.advance()
                    right = binaryoperations.Add(left, self.parse_assignment())
                case lexer.TokenKind.MinusEqual:
                    self.advance()
                    right = binaryoperations.Subtract(left, self.parse_assignment())
                case lexer.TokenKind.MultiplyEqual:
                    self.advance()
                    right = binaryoperations.Multiply(left, self.parse_assignment())
                case lexer.TokenKind.DivideEqual:
                    self.advance()
                    right = binaryoperations.Divide(left, self.parse_assignment())
                case lexer.TokenKind.ModEqual:
                    self.advance()
                    right = binaryoperations.Modulo(left, self.parse_assignment())
                case _:  # Should never run, but needed so type checker doesn't complain
                    raise NotImplementedError(f"Assignment operator {self.current_token.kind} is not yet implemented")
            left = nodes.Assignment(left, right)
        return left

    def parse_expression(self) -> Node:
        left = self.parse_comparison()
        if self.current_token is not None and self.current_token.kind == lexer.TokenKind.Or:
            self.advance()
            right = self.parse_comparison()
            out = binaryoperations.Or(left, right)
        elif self.current_token is not None and self.current_token.kind == lexer.TokenKind.And:
            self.advance()
            right = self.parse_comparison()
            out = binaryoperations.And(left, right)
        elif self.current_token is not None and self.current_token.kind == lexer.TokenKind.In:
            self.advance()
            right = self.parse_comparison()
            out = binaryoperations.In(left, right)
        else:
            out = left
        return out

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
        left = self.parse_atom_subscript()
        while self.current_token is not None and self.current_token.kind in (lexer.TokenKind.Multiply, lexer.TokenKind.Power, lexer.TokenKind.Divide, lexer.TokenKind.FloorDivide, lexer.TokenKind.Mod):
            match self.current_token.kind:
                case lexer.TokenKind.Multiply:
                    self.advance()
                    left = binaryoperations.Multiply(left, self.parse_multiplicative())
                case lexer.TokenKind.Power:
                    self.advance()
                    left = binaryoperations.Power(left, self.parse_multiplicative())
                case lexer.TokenKind.Divide:
                    self.advance()
                    left = binaryoperations.Divide(left, self.parse_multiplicative())
                case lexer.TokenKind.FloorDivide:
                    self.advance()
                    left = binaryoperations.FloorDivide(left, self.parse_multiplicative())
                case lexer.TokenKind.Mod:
                    self.advance()
                    left = binaryoperations.Modulo(left, self.parse_multiplicative())
        return left

    def parse_atom_subscript(self) -> Node:
        left = self.parse_atom()
        while self.current_token is not None and self.current_token.kind == lexer.TokenKind.LeftBracket:
            self.advance()
            start, stop = NullLiteral(), NullLiteral()
            if self.current_token is not None and self.current_token.kind != lexer.TokenKind.Colon:
                start = self.parse_expression()
                stop = start
            if self.current_token is not None and self.current_token.kind == lexer.TokenKind.Colon:
                self.advance()
                if self.current_token is not None and self.current_token.kind != lexer.TokenKind.RightBracket:
                    stop = self.parse_expression()
            if start == stop:
                left = nodes.Subscript(left, start)
            else:
                left = nodes.Subscript(left, SliceLiteral(start, stop))
            self.consume(lexer.TokenKind.RightBracket, "Expected ']' after subscript")
        return left

    def parse_atom(self):
        if self.current_token is None:
            raise SyntaxError("Unexpected end of file")
        match self.current_token.kind:
            case lexer.TokenKind.Plus:
                self.advance()
                return unaryoperations.Plus(self.parse_atom())
            case lexer.TokenKind.Minus:
                self.advance()
                return unaryoperations.Minus(self.parse_atom())
            case lexer.TokenKind.PlusPlus:
                self.advance()
                return unaryoperations.Plus(self.parse_atom())
            case lexer.TokenKind.MinusMinus:
                self.advance()
                return unaryoperations.Plus(self.parse_atom())
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
            case lexer.TokenKind.Not:
                self.advance()
                out = unaryoperations.Not(self.parse_comparison())
                self.logger.debug(f"Returning {out}")
                return out
            case lexer.TokenKind.Identifier:
                name = self.current_token.value
                self.advance()
                if self.current_token is not None and self.current_token.kind == lexer.TokenKind.LeftParen:
                    self.advance()
                    args = []
                    kwargs = {}
                    while self.current_token is not None and self.current_token.kind != lexer.TokenKind.RightParen:
                        node = self.parse_assignment()
                        if isinstance(node, nodes.Assignment):
                            kwargs[node.left.name] = node.right
                        else:
                            args.append(node)
                        if self.current_token is not None and self.current_token.kind == lexer.TokenKind.Comma:
                            self.advance()
                        else:
                            break
                    self.consume(lexer.TokenKind.RightParen, "Expected ')' after function call")
                    out = nodes.FunctionCall(name, args, kwargs)
                else:
                    out = nodes.VariableReference(name)
                self.logger.debug(f"Returning {out}")
                return out
            case lexer.TokenKind.LeftParen:
                self.advance()
                out = self.parse_expression()
                if self.current_token is not None and self.current_token.kind == lexer.TokenKind.Comma:
                    self.advance()
                    elements = [out]
                    while self.current_token is not None and self.current_token.kind != lexer.TokenKind.RightParen:
                        elements.append(self.parse_expression())
                        if self.current_token is not None and self.current_token.kind == lexer.TokenKind.Comma:
                            self.advance()
                        else:
                            break
                    out = TupleLiteral(elements)
                self.consume(lexer.TokenKind.RightParen, "Expected ')' after expression/tuple")
                self.logger.debug(f"Returning {out}")
                return out
            case lexer.TokenKind.LeftBracket:
                self.advance()
                elements = []
                while self.current_token is not None and self.current_token.kind != lexer.TokenKind.RightBracket:
                    elements.append(self.parse_expression())
                    if self.current_token is not None and self.current_token.kind == lexer.TokenKind.Comma:
                        self.advance()
                    else:
                        break
                self.consume(lexer.TokenKind.RightBracket, "Expected ']' after list")
                out = ListLiteral(elements)
                self.logger.debug(f"Returning {out}")
                return out
            case lexer.TokenKind.LeftBrace:
                self.advance()
                elements = []
                while self.current_token is not None and self.current_token.kind != lexer.TokenKind.RightBrace:
                    key = self.parse_expression()
                    self.consume(lexer.TokenKind.Colon, "Expected ':' after key in dictionary")
                    value = self.parse_expression()
                    elements.append((key, value))
                    if self.current_token is not None and self.current_token.kind == lexer.TokenKind.Comma:
                        self.advance()
                    else:
                        break
                self.consume(lexer.TokenKind.RightBrace, "Expected '}' after dictionary")
                out = DictionaryLiteral(elements)
                self.logger.debug(f"Returning {out}")
                return out
        raise SyntaxError(f"Unexpected token: {self.current_token} {self.current_token.position_end}:{self.current_token.position_end}")
