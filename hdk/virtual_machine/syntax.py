"""Defines dataclasses that represent different types of vm commands."""
from dataclasses import dataclass
from typing import ClassVar, TypeAlias


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


# An alias for type-hints representing virtual machine instructions.
VMCommand: TypeAlias = ArithmeticLogicalCommand | MemoryTransferCommand
