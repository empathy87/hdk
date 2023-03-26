import re
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class LabelDeclaration:
    symbol: str

    def __post_init__(self):
        if not _is_valid_symbol(self.symbol):
            raise ValueError(f"Incorrect symbol {self.symbol!r} for Label.")


@dataclass(frozen=True)
class AInstruction:
    symbol: str

    @property
    def is_constant(self) -> bool:
        return self.symbol.isdecimal()

    def __post_init__(self):
        if self.is_constant or _is_valid_symbol(self.symbol):
            return
        raise ValueError(f"Incorrect symbol {self.symbol!r} for A-Instruction.")


@dataclass(frozen=True)
class CInstruction:
    _allowed_destinations: ClassVar[set[str | None]] = {
        None,
        "M",
        "D",
        "DM",
        "A",
        "AM",
        "AD",
        "ADM",
    }
    _allowed_computations: ClassVar[set[str | None]] = {
        "0",
        "1",
        "-1",
        "D",
        "A",
        "!D",
        "!A",
        "-D",
        "-A",
        "D+1",
        "A+1",
        "D-1",
        "A-1",
        "D+A",
        "D-A",
        "A-D",
        "D&A",
        "D|A",
        "M",
        "!M",
        "-M",
        "M+1",
        "M-1",
        "D+M",
        "D-M",
        "M-D",
        "D&M",
        "D|M",
    }
    _allowed_jumps: ClassVar[set[str | None]] = {
        None,
        "JGT",
        "JEQ",
        "JGE",
        "JLT",
        "JNE",
        "JLE",
        "JMP",
    }

    computation: str
    destination: str | None = None
    jump: str | None = None

    def __post_init__(self):
        cls = self.__class__
        if self.destination not in cls._allowed_destinations:
            raise ValueError(f"Wrong dest {self.destination!r} for C-Instruction.")
        if self.computation not in cls._allowed_computations:
            raise ValueError(f"Wrong comp {self.computation!r} for C-Instruction.")
        if self.jump not in cls._allowed_jumps:
            raise ValueError(f"Wrong jump {self.jump!r} for C-Instruction.")


def _is_valid_symbol(symbol: str) -> bool:
    """Checks if the string is valid symbol.

    A symbol can be any sequence of letters, digits, underscores (_), dot (.),
    dollar sign ($), and colon (:) that does not begin with a digit.

    >>> _is_valid_symbol('_R0$:56.')
    True
    >>> _is_valid_symbol('5A')
    False
    >>> _is_valid_symbol('A97^')
    False
    """
    if len(symbol) == 0 or symbol[0].isdigit():
        return False
    return re.fullmatch(r"[\w_$\.:]+", symbol) is not None
