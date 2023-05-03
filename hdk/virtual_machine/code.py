"""Provides functions to translate Instruction into their assembly commands."""
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


def translate_arithmetic_logical_command(
    command: ArithmeticLogicalCommand, instruction_counter: int
) -> list[str]:
    """Translates a StackInstruction into its assembly code.

    Args:
        command (StackInstruction): The stack instruction to translate.
        instruction_counter (int): The current instruction counter value.

    Returns:
         a list of assembly code instructions and the updated instruction counter value.

    Raises:
        ValueError: If the given StackInstruction has an invalid command.
    """
    if command.command == "neg":
        return ["@SP", "A=M-1", "M=-M"]
    elif command.command == "not":
        return ["@SP", "A=M-1", "M=!M"]
    elif command.command in _BINARY_TABLE:
        return [
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
            _BINARY_TABLE[command.command],
        ]
    elif command.command in {"eq", "gt", "lt"}:
        true_jump = _COMPARISON_TABLE[command.command]
        code = [
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
            "MD=M-D",
            f"@true{instruction_counter}",
            "D;" + true_jump,
            f"(false{instruction_counter})",
            "@SP",
            "A=M-1",
            "M=0",
            f"@continue{instruction_counter}",
            "0;JMP",
            f"(true{instruction_counter})",
            "@SP",
            "A=M-1",
            "M=-1",
            f"(continue{instruction_counter})",
        ]
        return code
    else:
        raise ValueError(f"Invalid command {command.command!r} for stack instruction")


def translate_memory_transfer_command(command: MemoryTransferCommand) -> list[str]:
    """Translates a MemoryAccessInstruction into its assembly code.
    Args:
        command: The memory access instruction to be translated.

    Returns:
        list[str]: The assembly code for the given memory access instruction.
    """

    def add_d_to_stack() -> list[str]:
        return ["@SP", "A=M", "M=D", "@SP", "M=M+1"]

    def pop_to_r13() -> list[str]:
        return ["@SP", "AM=M-1", "D=M", "@R13", "A=M", "M=D"]

    def translate_push() -> list[str]:
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

    def translate_pop() -> list[str]:
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

    if command.command == "push":
        return translate_push() + add_d_to_stack()
    else:
        return translate_pop() + pop_to_r13()


def translate(commands: Iterable[VMCommand]) -> Iterator[str]:
    """Translates a sequence of instructions into a sequence of assembly code lists.

    Args:
        commands: An iterable of instructions to be translated.

    Yields:
        list[str]: Lists of strings representing the assembly code for each instruction.
    """
    for command_id, command in enumerate(commands):
        if isinstance(command, ArithmeticLogicalCommand):
            yield from translate_arithmetic_logical_command(command, command_id)
        else:
            yield from translate_memory_transfer_command(command)
