"""Provides functions to translate VM commands into their assembly commands."""
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
        command (StackInstruction): The stack instruction to translate.
        command_id (int): The current instruction counter value.

    Returns:
         a list of assembly code instructions and the updated instruction counter value.

    Raises:
        ValueError: If the given StackInstruction has an invalid command.
    """
    if command.operation == "neg":
        return ["@SP", "A=M-1", "M=-M"]
    elif command.operation == "not":
        return ["@SP", "A=M-1", "M=!M"]
    elif command.operation in _BINARY_TABLE:
        return [
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
            _BINARY_TABLE[command.operation],
        ]
    elif command.operation in _COMPARISON_TABLE:
        code = [
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
        return code
    else:
        raise ValueError(f"Invalid command {command.operation!r} for stack instruction")


def translate_push(command: MemoryTransferCommand) -> list[str]:
    if command.segment == "constant":
        return [f"@{command.index}", "D=A"]
    if command.segment in _SEGMENT_TABLE:
        return [
            f"@{_SEGMENT_TABLE[command.segment]}",
            "D=M",
            f"@{command.index}",
            "A=D+A",
            "D=M",
        ]
    if command.segment == "temp":
        return [
            "@R5",
            "D=M",
            f"@{command.index + 5}",
            "A=D+A",
            "D=M",
        ]
    if command.segment == "pointer":
        return ["@THIS" if command.index == 0 else "@THAT", "D=M"]
    return [f"@{command.index + 16}", "D=M"]


def translate_pop(command: MemoryTransferCommand) -> list[str]:
    if command.segment in _SEGMENT_TABLE:
        return [
            f"@{_SEGMENT_TABLE[command.segment]}",
            "D=M",
            f"@{command.index}",
            "D=D+A",
            "@R13",
            "M=D",
        ]
    if command.segment == "temp":
        return [
            "@R5",
            "D=M",
            f"@{command.index + 5}",
            "D=D+A",
            "@R13",
            "M=D",
        ]
    if command.segment == "pointer":
        return [
            "@THIS" if command.index == 0 else "@THAT",
            "D=A",
            "@R13",
            "M=D",
        ]
    return [f"@{command.index + 16}", "D=A", "@R13", "M=D"]


def translate_memory_transfer_command(command: MemoryTransferCommand) -> list[str]:
    """Translates a MemoryTransferCommand into its assembly code.
    Args:
        command: The memory access instruction to be translated.

    Returns:
        list[str]: The assembly code for the given memory access instruction.
    """
    if command.operation == "push":
        return translate_push(command) + _SAVE_D_INSTRUCTIONS
    else:
        return translate_pop(command) + _RESTORE_D_INSTRUCTIONS


def translate(commands: Iterable[VMCommand]) -> Iterator[str]:
    """Translate VM-commands into assembly symbolic instructions.

    Args:
        commands: An iterable of commands to be translated.

    Yields:
        str: String representing the assembly code for each command.
    """
    for command_id, command in enumerate(commands):
        if isinstance(command, ArithmeticLogicalCommand):
            yield from translate_arithmetic_logical_command(command, command_id)
        else:
            yield from translate_memory_transfer_command(command)
