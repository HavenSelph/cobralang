import unittest
from src.cobralang.lexer import Lexer, TokenKind, make_lexer_from_file_path, InvalidStringError, InvalidSyntaxError, InvalidFloatError


def make_lexer(file_path: str) -> Lexer:
    return make_lexer_from_file_path(file_path).tokenize()


def lex_then_unpack(text: str) -> list[tuple[TokenKind, str]]:
    tokens = Lexer(text, "<stdin>").tokenize()
    return [(token.kind, token.value) for token in tokens]


class TestLexer(unittest.TestCase):
    def test_string_literals(self):
        self.assertEqual(
            [(TokenKind.StringLiteral, "Hello, world!"), (TokenKind.StringLiteral, "Hello, world!")],
            lex_then_unpack('"Hello, world!" "Hello, world!"'),
        )

    def test_string_literals_with_escaped_quotes(self):
        self.assertEqual(
            [(TokenKind.StringLiteral, 'Hello, world!" !')],
            lex_then_unpack('"Hello, world!\\" !"')
        )

    def test_string_literals_with_newlines(self):
        self.assertEqual(
            [(TokenKind.StringLiteral, "Hello, world!\n !")],
            lex_then_unpack('"Hello, world!\n !"')
        )

    def test_string_literals_with_escaped_newlines(self):
        self.assertEqual(
            [(TokenKind.StringLiteral, "Hello, world!\nnewline")],
            lex_then_unpack(r'"Hello, world!\nnewline"')
        )

    def test_integer_literals(self):
        self.assertEqual(
            [(TokenKind.IntegerLiteral, "123")],
            lex_then_unpack("123")
        )

    def test_float_literals(self):
        self.assertEqual(
            [(TokenKind.FloatLiteral, "123.456")],
            lex_then_unpack("123.456")
        )

    def test_float_literals_with_leading_dot(self):
        self.assertEqual(
            [(TokenKind.FloatLiteral, ".456")],
            lex_then_unpack(".456")
        )

    def test_float_literals_with_trailing_dot(self):
        self.assertEqual(
            [(TokenKind.FloatLiteral, "123.")],
            lex_then_unpack("123.")
        )

    def test_parens(self):
        self.assertEqual(
            [(TokenKind.LeftParen, None), (TokenKind.RightParen, None)],
            lex_then_unpack("()")
        )

    def test_brackets(self):
        self.assertEqual(
            [(TokenKind.LeftBracket, None), (TokenKind.RightBracket, None)],
            lex_then_unpack("[]")
        )

    def test_braces(self):
        self.assertEqual(
            [(TokenKind.LeftBrace, None), (TokenKind.RightBrace, None)],
            lex_then_unpack("{}")
        )

    def test_semicolons(self):
        self.assertEqual(
            [(TokenKind.Semicolon, None)],
            lex_then_unpack(";")
        )

    def test_colons(self):
        self.assertEqual(
            [(TokenKind.Colon, None)],
            lex_then_unpack(":")
        )

    def test_commas(self):
        self.assertEqual(
            [(TokenKind.Comma, None)],
            lex_then_unpack(",")
        )

    def test_boolean(self):
        self.assertEqual(
            [(TokenKind.BooleanLiteral, "True"), (TokenKind.BooleanLiteral, "False")],
            lex_then_unpack("True False")
        )

    def test_null(self):
        self.assertEqual(
            [(TokenKind.NullLiteral, "Null")],
            lex_then_unpack("Null")
        )

    def test_plus(self):
        self.assertEqual(
            [(TokenKind.Plus, None)],
            lex_then_unpack("+")
        )

    def test_minus(self):
        self.assertEqual(
            [(TokenKind.Minus, None)],
            lex_then_unpack("-")
        )

    def test_multiply(self):
        self.assertEqual(
            [(TokenKind.Multiply, None)],
            lex_then_unpack("*")
        )

    def test_divide(self):
        self.assertEqual(
            [(TokenKind.Divide, None)],
            lex_then_unpack("/")
        )

    def test_equal(self):
        self.assertEqual(
            [(TokenKind.Equal, None)],
            lex_then_unpack("=")
        )


class TestExpectedErrors(unittest.TestCase):
    def test_unterminated_string_literal(self):
        with self.assertRaises(InvalidStringError):
            Lexer("'Hello, world!").tokenize()

    def test_unterminated_string_literal_with_newline(self):
        with self.assertRaises(InvalidStringError):
            Lexer("'Hello, world!").tokenize()

    def test_unterminated_string_literal_with_escaped_newline(self):
        with self.assertRaises(InvalidStringError):
            Lexer(r"'Hello, world!\n").tokenize()

    def test_invalid_syntax(self):
        with self.assertRaises(InvalidFloatError):
            Lexer("123.456.789").tokenize()
