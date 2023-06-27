import xml.dom.minidom
from collections.abc import Iterable, Iterator
from pathlib import Path

from hdk.jack_analyzer.syntax_tokens import (
    ALLOWED_KEYWORDS,
    ALLOWED_LEXICAL_ELEMENTS,
    ALLOWED_SYMBOLS,
    Token,
    TokenType,
)


def parse_line(line: str) -> Iterator[Token]:
    cur_tok = ""
    for s in line:
        if s in ALLOWED_SYMBOLS:
            if cur_tok != "":
                yield parse_token(cur_tok)
            yield parse_token(s)
            cur_tok = ""
        elif s == " " and (len(cur_tok) == 0 or cur_tok[0] != '"'):
            if cur_tok != "":
                yield parse_token(cur_tok)
            cur_tok = ""
        else:
            cur_tok += s
            if cur_tok[0] == cur_tok[-1] == '"' and len(cur_tok) != 1:
                yield parse_token(cur_tok)
                cur_tok = ""
    if cur_tok != "":
        yield parse_token(cur_tok)


def parse_token(tok: str) -> Token:
    if tok in ALLOWED_SYMBOLS:
        return Token(TokenType.Symbol, tok)
    if tok in ALLOWED_KEYWORDS:
        return Token(TokenType.Keyword, tok)
    if tok.isdigit():
        return Token(TokenType.IntegerConstant, tok)
    if tok[0] == '"' and tok[-1] == '"':
        return Token(TokenType.StringConstant, tok[1:-1])
    return Token(TokenType.Identifier, tok)


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
    dom_tree = xml.dom.minidom.parseString("<tokens></tokens>")
    for token in tokens:
        newToken = dom_tree.createElement(
            ALLOWED_LEXICAL_ELEMENTS[token.token_type.value]
        )
        newToken.appendChild(dom_tree.createTextNode(token.value))
        dom_tree.childNodes[0].appendChild(newToken)
    return dom_tree


def get_tokens(source_path: Path) -> xml.dom.minidom.Document:
    return to_xml(parse_program(source_path))
