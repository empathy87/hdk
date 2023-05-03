"""Provides functions to translate VM commands into their assembly instructions."""
from collections.abc import Iterable, Iterator

from hdk.virtual_machine.syntax import (
    ArithmeticLogicalCommand,
    MemoryTransferCommand,
    VMCommand,
)

_BINARY_TABLE = {
    "add": "M=D+M",
    "sub": "M=M-D",
    "and": "M=D&M",
    "or": "M=D|M",
}

_COMPARISON_TABLE = {
    "eq": "JEQ",
    "lt": "JLT",
    "gt": "JGT",
}

_SEGMENT_TABLE = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
}

_SAVE_D_INSTRUCTIONS = ["@SP", "A=M", "M=D", "@SP", "M=M+1"]
_RESTORE_D_INSTRUCTIONS = ["@SP", "AM=M-1", "D=M", "@R13", "A=M", "M=D"]


def translate_arithmetic_logical_command(
    command: ArithmeticLogicalCommand, command_id: int
) -> list[str]:
    """Translates an ArithmeticLogicalCommand into its assembly code.

    Args:
        command: The arithmetic-logical command to translate.
        command_id: The current command number.

    Returns:
         A list of assembly code instructions.
    """
    if command.operation == "neg":
        return ["@SP", "A=M-1", "M=-M"]
    if command.operation == "not":
        return ["@SP", "A=M-1", "M=!M"]
    if command.operation in _BINARY_TABLE:
        return [
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
            _BINARY_TABLE[command.operation],
        ]
    if command.operation in _COMPARISON_TABLE:
        return [
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
            "MD=M-D",
            f"@true{command_id}",
            f"D;{_COMPARISON_TABLE[command.operation]}",
            f"(false{command_id})",
            "@SP",
            "A=M-1",
            "M=0",
            f"@continue{command_id}",
            "0;JMP",
            f"(true{command_id})",
            "@SP",
            "A=M-1",
            "M=-1",
            f"(continue{command_id})",
        ]
    raise ValueError(
        f"Invalid command {command.operation!r} for arithmetic-logical instruction"
    )


def translate_push(segment: str, index: int) -> list[str]:
    """Translates a push operation into assembly instructions.

    Args:
        segment: The memory segment for the push operation.
        index: The index within the memory segment for the push operation.

    Returns:
        A list of Hack assembly instructions.
    """
    if segment == "constant":
        return [f"@{index}", "D=A"]
    if segment in _SEGMENT_TABLE:
        return [
            f"@{_SEGMENT_TABLE[segment]}",
            "D=M",
            f"@{index}",
            "A=D+A",
            "D=M",
        ]
    if segment == "temp":
        return [
            "@R5",
            "D=M",
            f"@{index + 5}",
            "A=D+A",
            "D=M",
        ]
    if segment == "pointer":
        return ["@THIS" if index == 0 else "@THAT", "D=M"]
    if segment == "static":
        return [f"@{index + 16}", "D=M"]
    raise ValueError(f"Wrong segment {segment!r} for VMcommand.")


def translate_pop(segment: str, index: int) -> list[str]:
    """Translates a pop operation into Hack assembly instructions.

    Args:
        segment: The memory segment for the pop operation.
        index: The index within the memory segment for the pop operation.

    Returns:
        A list of Hack assembly instructions.
    """
    if segment in _SEGMENT_TABLE:
        return [
            f"@{_SEGMENT_TABLE[segment]}",
            "D=M",
            f"@{index}",
            "D=D+A",
            "@R13",
            "M=D",
        ]
    if segment == "temp":
        return [
            "@R5",
            "D=M",
            f"@{index + 5}",
            "D=D+A",
            "@R13",
            "M=D",
        ]
    if segment == "pointer":
        return [
            "@THIS" if index == 0 else "@THAT",
            "D=A",
            "@R13",
            "M=D",
        ]
    if segment == "static":
        return [f"@{index + 16}", "D=A", "@R13", "M=D"]
    raise ValueError(f"Wrong segment {segment!r} for VMcommand.")


def translate_memory_transfer_command(command: MemoryTransferCommand) -> list[str]:
    """Translates a MemoryTransferCommand into its assembly code.
    Args:
        command: The memory access instruction to be translated.

    Returns:
        The assembly code for the given memory access instruction.
    """
    if command.operation == "push":
        return translate_push(command.segment, command.index) + _SAVE_D_INSTRUCTIONS
    return translate_pop(command.segment, command.index) + _RESTORE_D_INSTRUCTIONS


def translate(commands: Iterable[VMCommand]) -> Iterator[str]:
    """Translate VM-commands into assembly symbolic instructions.

    Args:
        commands: An iterable of commands to be translated.

    Yields:
        Strings representing the assembly code for each command.
    """
    for command_id, command in enumerate(commands):
        if isinstance(command, ArithmeticLogicalCommand):
            yield from translate_arithmetic_logical_command(command, command_id)
        else:
            yield from translate_memory_transfer_command(command)
