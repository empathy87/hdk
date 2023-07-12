"""Functions for parsing Jack code into tokens."""
import xml.dom.minidom
from collections.abc import Iterable, Iterator
from enum import Enum
from pathlib import Path
from typing import NamedTuple


class TokenType(Enum):
    """Represents a token types."""

    KEYWORD = 0
    SYMBOL = 1
    INTEGER_CONSTANT = 2
    STRING_CONSTANT = 3
    IDENTIFIER = 4


_KEYWORDS: set[str] = {
    "class",
    "method",
    "function",
    "constructor",
    "int",
    "boolean",
    "char",
    "var",
    "static",
    "field",
    "let",
    "do",
    "if",
    "else",
    "while",
    "return",
    "true",
    "false",
    "null",
    "this",
    "void",
}

_SYMBOLS: set[str] = {
    "{",
    "}",
    "(",
    ")",
    "[",
    "]",
    ".",
    ",",
    ";",
    "+",
    "-",
    "*",
    "/",
    "&",
    "|",
    "~",
    "<",
    ">",
    "=",
}


class Token(NamedTuple):
    """Represents a token with its type and value."""

    token_type: TokenType
    value: str


def tokenize(text: str) -> Iterator[Token]:
    """Tokenizes the given text into a sequence of tokens.

    Args:
        text: The input line to be tokenized.

    Yields:
        A generator that yields tokens.
    """
    current_token = ""
    for char in text:
        if char in _SYMBOLS:
            if current_token != "":
                yield build_token(current_token)
            yield build_token(char)
            current_token = ""
        elif char == " " and (len(current_token) == 0 or current_token[0] != '"'):
            if current_token != "":
                yield build_token(current_token)
            current_token = ""
        else:
            current_token += char
            if current_token[0] == current_token[-1] == '"' and len(current_token) != 1:
                yield build_token(current_token)
                current_token = ""
    if current_token != "":
        yield build_token(current_token)


def build_token(token: str) -> Token:
    """Builds a token based on the given string.

    Args:
        token: The string to be converted into a token.

    Returns:
        The token object representing the given string.
    """
    if token in _SYMBOLS:
        return Token(TokenType.SYMBOL, token)
    if token in _KEYWORDS:
        return Token(TokenType.KEYWORD, token)
    if token.isdigit():
        return Token(TokenType.INTEGER_CONSTANT, token)
    if token[0] == '"' and token[-1] == '"':
        return Token(TokenType.STRING_CONSTANT, token[1:-1])
    return Token(TokenType.IDENTIFIER, token)


def tokenize_source_code(lines: Iterable[str]) -> Iterator[Token]:
    """Tokenizes the source code provided as a sequence of lines.

    Args:
        lines: An iterable of strings representing the lines of source code.

    Yields:
        A generator that yields tokens.

    Raises:
        ValueError: If there is an error parsing a line of source code.
    """
    is_comment = False
    for line_num, line in enumerate(lines):
        line = line.strip().split("//")[0]
        if line.startswith("/*"):
            is_comment = True
        if not (len(line) == 0 or is_comment):
            try:
                yield from tokenize(line)
            except ValueError as e:
                raise ValueError(f"Cannot parse line {line_num + 1}.") from e
        if line.endswith("*/"):
            is_comment = False


def tokenize_program(source_path: Path) -> Iterator[Token]:
    """Tokenizes the program source code from the given file.

    Args:
        source_path: The path to the source code file.

    Yields:
        A generator that yields tokens.
    """

    def _file_lines() -> Iterator[str]:
        with open(source_path) as file:
            yield from file

    return tokenize_source_code(_file_lines())


def to_xml(tokens: Iterable[Token]) -> xml.dom.minidom.Document:
    """Converts a sequence of tokens into an XML representation.

    Args:
        tokens: An iterable of Token objects.

    Returns:
        The XML document representing the tokens.
    """
    type_to_tag: dict[TokenType, str] = {
        TokenType.KEYWORD: "keyword",
        TokenType.SYMBOL: "symbol",
        TokenType.INTEGER_CONSTANT: "integerConstant",
        TokenType.STRING_CONSTANT: "stringConstant",
        TokenType.IDENTIFIER: "identifier",
    }
    dom_tree = xml.dom.minidom.parseString("<tokens></tokens>")
    for token in tokens:
        newToken = dom_tree.createElement(type_to_tag[token.token_type])
        newToken.appendChild(dom_tree.createTextNode(token.value))
        dom_tree.childNodes[0].appendChild(newToken)
    return dom_tree
