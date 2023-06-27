import re

ALLOWED_LEXICAL_ELEMENTS: set[str] = {
    "keyword",
    "symbol",
    "integerConstant",
    "stringConstant",
    "identifier",
}

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


class Keyword:
    value: str

    def build(self, line: str):
        if line.split()[0] == "<keyword>" and line.split()[1] in ALLOWED_KEYWORDS:
            self.value = line.split()[1]
        else:
            raise ValueError("Given line is not keyword token.")

    def __init__(self, value: str = "None"):
        if value != "None":
            if value in ALLOWED_KEYWORDS:
                self.value = value
            else:
                raise ValueError("Given value is not keyword.")


class Symbol:
    value: str

    def build(self, line: str):
        if line.split()[0] == "<symbol>" and line.split()[1] in ALLOWED_SYMBOLS:
            self.value = line.split()[1]
        else:
            raise ValueError("Given line is not symbol token.")

    def __init__(self, value: str = "None"):
        if value != "None":
            if value in ALLOWED_SYMBOLS:
                self.value = ALLOWED_SYMBOLS[value]
            else:
                raise ValueError("Given value is not symbol.")


class Identifier:
    value: str

    def build(self, line: str):
        if line.split()[0] == "<identifier>" and _is_symbol_valid(line.split()[1]):
            self.value = line.split()[1]
        else:
            raise ValueError("Given line is not identifier token.")

    def __init__(self, value: str = ""):
        if value != "":
            if _is_symbol_valid(value):
                self.value = value
            else:
                raise ValueError("Given value is not identifier.")


class StringConstant:
    value: str

    def build(self, line: str):
        if line.split()[0] == "<stringConstant>":
            self.value = line.split()[1]
        else:
            raise ValueError("Given line is not stringConstant token.")

    def __init__(self, value: str = ""):
        self.value = value


class IntegerConstant:
    value: str

    def build(self, line: str):
        if line.split()[0] == "<integerConstant>" and line.split()[1].isdigit():
            self.value = line.split()[1]
        else:
            raise ValueError("Given line is not integerConstant token.")

    def __init__(self, value: str = "None"):
        if value != "None":
            if value.isdigit():
                self.value = value
            else:
                raise ValueError("Given value is not integerConstant.")


class Token:
    _type: str
    value: str

    def build(self, line: str):
        token_class, token_value = line.split()[0:1]
        self._type = token_class
        self.value = token_value

    def __init__(self, _type, value):
        self._type = _type
        self.value = value

    @property
    def type(self):
        return self._type


def _is_symbol_valid(symbol: str) -> bool:
    """Checks if a symbol is valid.

    A symbol can be any sequence of letters, digits, underscores (_), dot (.),
    dollar sign ($), and colon (:) that does not begin with a digit.

    Args:
        symbol: A string representing the symbol.

    Returns:
        True if the symbol is correct, False otherwise.

    Typical usage example:
        >>> _is_symbol_valid('_R0$:56.')
        True
        >>> _is_symbol_valid('5A')
        False
        >>> _is_symbol_valid('A97^')
        False
    """
    if len(symbol) == 0 or symbol[0].isdigit():
        return False
    return re.fullmatch(r"[\w_$\.:]+", symbol) is not None
