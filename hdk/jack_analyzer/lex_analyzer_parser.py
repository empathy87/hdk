from collections.abc import Iterator

from hdk.jack_analyzer.syntax_tokens import ALLOWED_KEYWORDS, ALLOWED_SYMBOLS, Token


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
        return Token("symbol", tok)
    if tok in ALLOWED_KEYWORDS:
        return Token("keyword", tok)
    if tok.isdigit():
        return Token("integerConstant", tok)
    if tok[0] == '"' and tok[-1] == '"':
        return Token("stringConstant", tok[1:-1])
    return Token("identifier", tok)
