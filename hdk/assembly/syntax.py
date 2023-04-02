"""Dataclasses that represent symbolic instructions underlying fields."""
import re
from collections import Counter
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class Label:
    """Represents a Label symbolic assembly instruction."""

    symbol: str

    def __post_init__(self):
        if not _is_symbol_valid(self.symbol):
            raise ValueError(f"Invalid symbol {self.symbol!r} for Label.")


@dataclass(frozen=True)
class AInstruction:
    """Represents an A- symbolic assembly instruction."""

    symbol: str

    @property
    def is_constant(self) -> bool:
        return self.symbol.isdecimal()

    def __post_init__(self):
        if self.is_constant or _is_symbol_valid(self.symbol):
            return
        raise ValueError(f"Incorrect symbol {self.symbol!r} for A-Instruction.")


@dataclass(frozen=True)
class CInstruction:
    """Represents a C- symbolic assembly instruction."""

    _allowed_comp: ClassVar[set[str | None]] = {
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
    _allowed_jump: ClassVar[set[str | None]] = {
        None,
        "JGT",
        "JEQ",
        "JGE",
        "JLT",
        "JNE",
        "JLE",
        "JMP",
    }

    comp: str
    dest: str | None = None
    jump: str | None = None

    @staticmethod
    def _is_dest_correct(dest):
        if dest is None:
            return True
        counts = Counter(list(dest))
        wrong_chars = set(counts.keys()) - set(list("ADM"))
        max_char_count = max(counts.values())
        return len(wrong_chars) == 0 and max_char_count == 1

    def __post_init__(self):
        cls = self.__class__
        if not self._is_dest_correct(self.dest):
            raise ValueError(f"Wrong dest {self.dest!r} for C-Instruction.")
        if self.comp not in cls._allowed_comp:
            raise ValueError(f"Wrong comp {self.comp!r} for C-Instruction.")
        if self.jump not in cls._allowed_jump:
            raise ValueError(f"Wrong jump {self.jump!r} for C-Instruction.")


def _is_symbol_valid(symbol: str) -> bool:
    """Checks if the string is a valid symbol.

    A symbol can be any sequence of letters, digits, underscores (_), dot (.),
    dollar sign ($), and colon (:) that does not begin with a digit.

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


# An alias for type-hints representing any symbolic assembly instruction.
Instruction = Label | AInstruction | CInstruction
