"""Defines dataclasses that represent different types of vm instructions."""
from dataclasses import dataclass
from typing import ClassVar, TypeAlias


@dataclass(frozen=True)
class StackInstruction:
    """A data class representing a stack instruction in a virtual machine.

    Attributes:
        command: The operation to be performed on the stack.
    """

    _ALLOWED_COMMAND: ClassVar[set[str]] = {
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

    command: str

    def __post_init__(self):
        cls = self.__class__
        if self.command not in cls._ALLOWED_COMMAND:
            raise ValueError(f"Wrong command {self.command!r} for operation on stack.")


@dataclass(frozen=True)
class MemoryAccessInstruction:
    """A data class representing a memory access instruction in a virtual machine.

    Attributes:
        command: The type of memory access operation to be performed.
        segment: The memory segment to be accessed.
        index: The index of the memory location to be accessed.
    """

    _ALLOWED_COMMAND: ClassVar[set[str]] = {
        "pop",
        "push",
    }

    _ALLOWED_SEGMENT: ClassVar[set[str]] = {
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

    command: str
    segment: str
    index: str

    def __post_init__(self):
        cls = self.__class__
        if self.command not in cls._ALLOWED_COMMAND:
            raise ValueError(f"Wrong command {self.command!r} for operation on stack.")
        if self.command not in cls._ALLOWED_COMMAND:
            raise ValueError(f"Wrong command {self.command!r} for operation on stack.")


# An alias for type-hints representing virtual machine instructions.
Instruction: TypeAlias = StackInstruction | MemoryAccessInstruction
