import xml.dom.minidom
from collections.abc import Iterable, Iterator
from enum import Enum
from pathlib import Path
from typing import NamedTuple


class TokenType(Enum):
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
    token_type: TokenType
    value: str


def parse_line(line: str) -> Iterator[Token]:
    current_token = ""
    for char in line:
        if char in _SYMBOLS:
            if current_token != "":
                yield parse_token(current_token)
            yield parse_token(char)
            current_token = ""
        elif char == " " and (len(current_token) == 0 or current_token[0] != '"'):
            if current_token != "":
                yield parse_token(current_token)
            current_token = ""
        else:
            current_token += char
            if current_token[0] == current_token[-1] == '"' and len(current_token) != 1:
                yield parse_token(current_token)
                current_token = ""
    if current_token != "":
        yield parse_token(current_token)


def parse_token(token: str) -> Token:
    if token in _SYMBOLS:
        return Token(TokenType.SYMBOL, token)
    if token in _KEYWORDS:
        return Token(TokenType.KEYWORD, token)
    if token.isdigit():
        return Token(TokenType.INTEGER_CONSTANT, token)
    if token[0] == '"' and token[-1] == '"':
        return Token(TokenType.STRING_CONSTANT, token[1:-1])
    return Token(TokenType.IDENTIFIER, token)


def parse_source_code(lines: Iterable[str]) -> Iterator[Token]:
    is_comment = False
    for line_num, line in enumerate(lines):
        line = line.strip().split("//")[0]
        if line.startswith("/*"):
            is_comment = True
        if line.endswith("*/"):
            is_comment = False
            continue
        if len(line) == 0 or is_comment:
            continue
        try:
            yield from parse_line(line)
        except ValueError as e:
            raise ValueError(f"Cannot parse line {line_num + 1}.") from e


def parse_program(source_path: Path) -> Iterator[Token]:
    def _file_lines() -> Iterator[str]:
        with open(source_path) as file:
            yield from file

    return parse_source_code(_file_lines())


def to_xml(tokens: Iterable[Token]) -> xml.dom.minidom.Document:
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
