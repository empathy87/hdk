"""Defines dataclasses that represent different types of vm commands."""
import re
from dataclasses import dataclass
from typing import ClassVar, TypeAlias


@dataclass(frozen=True)
class BranchingCommand:
    """Represents a Branching command in a virtual machine.

    Attributes:
        operation: The type of branching operation to be performed.
        label_name: The symbol defined by the Label.
    """

    _ALLOWED_OPERATIONS: ClassVar[set[str]] = {"label", "goto", "if-goto"}

    operation: str
    label_name: str

    def __post_init__(self):
        cls = self.__class__
        if not _is_symbol_valid(self.label_name):
            raise ValueError(f"Invalid symbol {self.label_name!r} for Label.")
        if self.operation not in cls._ALLOWED_OPERATIONS:
            raise ValueError(
                f"Wrong operation {self.operation!r} for branching command."
            )


@dataclass(frozen=True)
class FunctionCallCommand:
    """Represents a call command in a virtual machine.

    Attributes:
        function_name: The symbol defined by the Function.
        n_args: The number of arguments.
    """

    function_name: str
    n_args: int

    def __post_init__(self):
        if self.function_name is not None and not _is_symbol_valid(self.function_name):
            raise ValueError(
                f"Invalid symbol {self.function_name!r} for function name."
            )


@dataclass(frozen=True)
class FunctionDefinitionCommand:
    """Represents a function definition command in a virtual machine.

    Attributes:
        function_name: The symbol defined by the Function.
        n_vars: The number of variables or arguments.
    """

    function_name: str
    n_vars: int

    def __post_init__(self):
        if self.function_name is not None and not _is_symbol_valid(self.function_name):
            raise ValueError(
                f"Invalid symbol {self.function_name!r} for function name."
            )


@dataclass(frozen=True)
class ReturnCommand:
    """Represents a return command in a virtual machine."""


@dataclass(frozen=True)
class ArithmeticLogicalCommand:
    """Represents an ArithmeticLogical command in a virtual machine.

    Attributes:
        operation: The operation to be performed on the stack.
    """

    _ALLOWED_OPERATIONS: ClassVar[set[str]] = {
        "add",
        "sub",
        "neg",
        "eq",
        "gt",
        "lt",
        "and",
        "or",
        "not",
    }

    operation: str

    def __post_init__(self):
        cls = self.__class__
        if self.operation not in cls._ALLOWED_OPERATIONS:
            raise ValueError(
                f"Wrong operation {self.operation!r} for arithmetic-logical command."
            )


@dataclass(frozen=True)
class MemoryTransferCommand:
    """Represents a memory transfer command in a virtual machine.

    Attributes:
        operation: The type of memory access operation to be performed.
        segment: The memory segment to be accessed.
        index: The index of the memory location to be accessed.
    """

    _ALLOWED_OPERATIONS: ClassVar[set[str]] = {
        "pop",
        "push",
    }

    _ALLOWED_SEGMENTS: ClassVar[set[str]] = {
        "local",
        "argument",
        "local",
        "this",
        "that",
        "pointer",
        "temp",
        "constant",
        "static",
        "reg",
    }

    operation: str
    segment: str
    index: int

    def __post_init__(self):
        cls = self.__class__
        if self.index < 0:
            raise ValueError(f"Wrong index {self.index!r} for memory transfer command.")
        if self.operation not in cls._ALLOWED_OPERATIONS:
            raise ValueError(
                f"Wrong operation {self.operation!r} for memory transfer command"
            )
        if self.segment not in cls._ALLOWED_SEGMENTS:
            raise ValueError(
                f"Wrong segment {self.segment!r} for memory transfer command"
            )


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


# An alias for type-hints representing virtual machine instructions.
VMCommand: TypeAlias = (
    ArithmeticLogicalCommand
    | MemoryTransferCommand
    | FunctionDefinitionCommand
    | ReturnCommand
    | FunctionCallCommand
    | BranchingCommand
)
