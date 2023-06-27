from enum import Enum
from typing import NamedTuple

ALLOWED_LEXICAL_ELEMENTS: list[str] = [
    "keyword",
    "symbol",
    "integerConstant",
    "stringConstant",
    "identifier",
]

ALLOWED_KEYWORDS: set[str] = {
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

ALLOWED_SYMBOLS: dict[str, str] = {
    "{": "{",
    "}": "}",
    "(": "(",
    ")": ")",
    "[": "[",
    "]": "]",
    ".": ".",
    ",": ",",
    ";": ";",
    "+": "+",
    "-": "-",
    "*": "*",
    "/": "/",
    "&": "&amp;",
    "|": "|",
    "~": "~",
    "<": "&lt;",
    ">": "&gt;",
    "=": "=",
}


class TokenType(Enum):
    Keyword = 0
    Symbol = 1
    IntegerConstant = 2
    StringConstant = 3
    Identifier = 4


class Token(NamedTuple):
    token_type: TokenType
    value: str
