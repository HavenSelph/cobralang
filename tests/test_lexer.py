import unittest
from src.cobralang.lexer import Lexer, Token, TokenKind, make_lexer_from_file_path


def make_lexer(file_path: str) -> Lexer:
    return make_lexer_from_file_path(file_path).tokenize()


def lex_then_unpack(text: str) -> list[tuple[TokenKind, str]]:
    tokens = Lexer("<stdin>", text).tokenize()
    return [(token.kind, token.value) for token in tokens]


class TestLexer(unittest.TestCase):
    def test_string_literals(self):
        self.assertEqual(
            [(TokenKind.StringLiteral, "Hello, world!"), (TokenKind.StringLiteral, "Hello, world!")],
        )
