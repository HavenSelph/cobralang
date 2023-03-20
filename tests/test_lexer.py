import unittest
from src.cobralang import parser
from src.cobralang import lexer


def lex_then_unpack(text: str) -> list[tuple[lexer.TokenKind, str]]:
    tokens = lexer.Lexer(text, "<stdin>").tokenize()
    return [(token.kind, token.value) for token in tokens][:-1]


class TestLexer(unittest.TestCase):
    def test_string_literals(self):
        self.assertEqual(
            [(lexer.TokenKind.StringLiteral, "Hello, world!"), (lexer.TokenKind.StringLiteral, "Hello, world!")],
            lex_then_unpack('"Hello, world!" "Hello, world!"'),
        )

    def test_string_literals_with_escaped_quotes(self):
        self.assertEqual(
            [(lexer.TokenKind.StringLiteral, 'Hello, world!" !')],
            lex_then_unpack('"Hello, world!\\" !"')
        )

    def test_string_literals_with_newlines(self):
        self.assertEqual(
            [(lexer.TokenKind.StringLiteral, "Hello, world!\n !")],
            lex_then_unpack('"Hello, world!\n !"')
        )

    def test_string_literals_with_escaped_newlines(self):
        self.assertEqual(
            [(lexer.TokenKind.StringLiteral, "Hello, world!\nnewline")],
            lex_then_unpack(r'"Hello, world!\nnewline"')
        )

    def test_integer_literals(self):
        self.assertEqual(
            [(lexer.TokenKind.IntegerLiteral, "123")],
            lex_then_unpack("123")
        )

    def test_float_literals(self):
        self.assertEqual(
            [(lexer.TokenKind.FloatLiteral, "123.456")],
            lex_then_unpack("123.456")
        )

    def test_float_literals_with_leading_dot(self):
        self.assertEqual(
            [(lexer.TokenKind.FloatLiteral, ".456")],
            lex_then_unpack(".456")
        )

    def test_float_literals_with_trailing_dot(self):
        self.assertEqual(
            [(lexer.TokenKind.FloatLiteral, "123.")],
            lex_then_unpack("123.")
        )

    def test_parens(self):
        self.assertEqual(
            [(lexer.TokenKind.LeftParen, None), (lexer.TokenKind.RightParen, None)],
            lex_then_unpack("()")
        )

    def test_brackets(self):
        self.assertEqual(
            [(lexer.TokenKind.LeftBracket, None), (lexer.TokenKind.RightBracket, None)],
            lex_then_unpack("[]")
        )

    def test_braces(self):
        self.assertEqual(
            [(lexer.TokenKind.LeftBrace, None), (lexer.TokenKind.RightBrace, None)],
            lex_then_unpack("{}")
        )

    def test_semicolons(self):
        self.assertEqual(
            [(lexer.TokenKind.Semicolon, None)],
            lex_then_unpack(";")
        )

    def test_colons(self):
        self.assertEqual(
            [(lexer.TokenKind.Colon, None)],
            lex_then_unpack(":")
        )

    def test_commas(self):
        self.assertEqual(
            [(lexer.TokenKind.Comma, None)],
            lex_then_unpack(",")
        )

    def test_boolean(self):
        self.assertEqual(
            [(lexer.TokenKind.BooleanLiteral, "True"), (lexer.TokenKind.BooleanLiteral, "False")],
            lex_then_unpack("True False")
        )

    def test_null(self):
        self.assertEqual(
            [(lexer.TokenKind.NullLiteral, "Null")],
            lex_then_unpack("Null")
        )

    def test_plus(self):
        self.assertEqual(
            [(lexer.TokenKind.Plus, None)],
            lex_then_unpack("+")
        )

    def test_minus(self):
        self.assertEqual(
            [(lexer.TokenKind.Minus, None)],
            lex_then_unpack("-")
        )

    def test_multiply(self):
        self.assertEqual(
            [(lexer.TokenKind.Multiply, None)],
            lex_then_unpack("*")
        )

    def test_divide(self):
        self.assertEqual(
            [(lexer.TokenKind.Divide, None)],
            lex_then_unpack("/")
        )

    def test_equal(self):
        self.assertEqual(
            [(lexer.TokenKind.Equal, None)],
            lex_then_unpack("=")
        )


class TestExpectedErrors(unittest.TestCase):
    def test_unterminated_string_literal(self):
        with self.assertRaises(lexer.InvalidStringError):
            lexer.Lexer("'Hello, world!").tokenize()

    def test_unterminated_string_literal_with_newline(self):
        with self.assertRaises(lexer.InvalidStringError):
            lexer.Lexer("'Hello, world!").tokenize()

    def test_unterminated_string_literal_with_escaped_newline(self):
        with self.assertRaises(lexer.InvalidStringError):
            lexer.Lexer(r"'Hello, world!\n").tokenize()

    def test_invalid_syntax(self):
        with self.assertRaises(lexer.InvalidFloatError):
            lexer.Lexer("123.456.789").tokenize()
