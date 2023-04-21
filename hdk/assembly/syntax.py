"""Defines dataclasses that represent different types of Hack assembly instructions."""
import re
from collections import Counter
from dataclasses import dataclass
from typing import ClassVar, TypeAlias


@dataclass(frozen=True)
class Label:
    """Represents a Label symbolic assembly instruction.

    Attributes:
        symbol: The symbol defined by the Label instruction.
    """

    symbol: str

    def __post_init__(self):
        if not _is_symbol_valid(self.symbol):
            raise ValueError(f"Invalid symbol {self.symbol!r} for Label.")


@dataclass(frozen=True)
class AInstruction:
    """Represents an A-instruction in Hack assembly language.

    Attributes:
        symbol: The symbol or constant value specified in the A-instruction.
    """

    symbol: str

    @property
    def is_constant(self) -> bool:
        """True if the symbol represents a constant value."""
        return self.symbol.isdecimal()

    def __post_init__(self):
        if self.is_constant or _is_symbol_valid(self.symbol):
            return
        raise ValueError(f"Incorrect symbol {self.symbol!r} for A-Instruction.")


@dataclass(frozen=True)
class CInstruction:
    """Represents a C- symbolic assembly instruction, which performs a computation.

    Attributes:
        comp: The computation to be performed.
        dest: The destination registers or memory for the computation result.
        jump: The jump conditions.
    """

    _ALLOWED_COMP: ClassVar[set[str]] = {
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
    _ALLOWED_JUMP: ClassVar[set[str | None]] = {
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

    @property
    def is_m_dest(self) -> bool:
        """Check if memory[a resistor] is dest."""
        return bool(self.dest and "M" in self.dest)

    @property
    def is_a_dest(self) -> bool:
        """Check if a resistor is dest."""
        return bool(self.dest and "A" in self.dest)

    @property
    def is_d_dest(self) -> bool:
        """Check if d resistor is dest."""
        return bool(self.dest and "D" in self.dest)

    @staticmethod
    def _is_dest_correct(dest: str) -> bool:
        """Check if the destination part of the instruction is correct."""
        if dest is None:
            return True
        if not all(c in "ADM" for c in dest):
            return False
        return Counter(dest).most_common()[0][1] == 1

    def __post_init__(self):
        cls = self.__class__
        if not self._is_dest_correct(self.dest):
            raise ValueError(f"Wrong dest {self.dest!r} for C-Instruction.")
        if self.comp not in cls._ALLOWED_COMP:
            raise ValueError(f"Wrong comp {self.comp!r} for C-Instruction.")
        if self.jump not in cls._ALLOWED_JUMP:
            raise ValueError(f"Wrong jump {self.jump!r} for C-Instruction.")


def _is_symbol_valid(symbol: str) -> bool:
    """Checks if a symbol is valid.

    A symbol can be any sequence of letters, digits, underscores (_), dot (.),
    dollar sign ($), and colon (:) that does not begin with a digit.

    Args:
        symbol: A string representing the symbol.

    Returns:
        True if the symbol is correct, False otherwise.

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


# An alias for type-hints representing symbolic assembly instructions.
Command: TypeAlias = AInstruction | CInstruction
Instruction: TypeAlias = Label | Command
