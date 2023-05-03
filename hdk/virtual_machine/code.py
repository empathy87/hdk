"""Provides functions to translate Instruction into their assembly commands."""
from collections.abc import Iterable, Iterator

from hdk.virtual_machine.syntax import (
    ArithmeticLogicalCommand,
    Instruction,
    MemoryTransferCommand,
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


def translate_stack_instruction(
    stack_instruction: ArithmeticLogicalCommand, instruction_counter: int
) -> tuple[list[str], int]:
    """Translates a StackInstruction into its assembly code.

    Args:
        stack_instruction (StackInstruction): The stack instruction to translate.
        instruction_counter (int): The current instruction counter value.

    Returns:
         a list of assembly code instructions and the updated instruction counter value.

    Raises:
        ValueError: If the given StackInstruction has an invalid command.
    """
    if stack_instruction.command == "neg":
        return ["@SP", "A=M-1", "M=-M"], instruction_counter
    elif stack_instruction.command == "not":
        return ["@SP", "A=M-1", "M=!M"], instruction_counter
    elif stack_instruction.command in _BINARY_TABLE:
        return [
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
            _BINARY_TABLE[stack_instruction.command],
        ], instruction_counter
    elif stack_instruction.command in {"eq", "gt", "lt"}:
        true_jump = _COMPARISON_TABLE[stack_instruction.command]
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
        return code, instruction_counter + 1
    else:
        raise ValueError(
            f"Invalid command {stack_instruction.command!r} for stack instruction"
        )


def translate_memory_access_instruction(m: MemoryTransferCommand) -> list[str]:
    """Translates a MemoryAccessInstruction into its assembly code.
    Args:
        m (MemoryAccessInstruction): The memory access instruction to be translated.

    Returns:
        list[str]: The assembly code for the given memory access instruction.
    """

    def add_d_to_stack() -> list[str]:
        return ["@SP", "A=M", "M=D", "@SP", "M=M+1"]

    def pop_to_r13() -> list[str]:
        return ["@SP", "AM=M-1", "D=M", "@R13", "A=M", "M=D"]

    if m.command == "push":
        if m.segment == "constant":
            return [f"@{m.index}", "D=A"] + add_d_to_stack()
        if m.segment in _SEGMENT_TABLE:
            return [
                f"@{_SEGMENT_TABLE[m.segment]}",
                "D=M",
                f"@{m.index}",
                "A=D+A",
                "D=M",
            ] + add_d_to_stack()
        if m.segment == "temp":
            return [
                "@R5",
                "D=M",
                f"@{str(int(m.index) + 5)}",
                "A=D+A",
                "D=M",
            ] + add_d_to_stack()
        if m.segment == "pointer":
            return ["@THIS" if m.index == "0" else "@THAT", "D=M"] + add_d_to_stack()
        return [f"@{m.index + 16}", "D=M"] + add_d_to_stack()
    else:
        if m.segment in _SEGMENT_TABLE:
            return [
                f"@{_SEGMENT_TABLE[m.segment]}",
                "D=M",
                f"@{m.index}",
                "D=D+A",
                "@R13",
                "M=D",
            ] + pop_to_r13()
        if m.segment == "temp":
            return [
                "@R5",
                "D=M",
                f"@{m.index + 5}",
                "D=D+A",
                "@R13",
                "M=D",
            ] + pop_to_r13()
        if m.segment == "pointer":
            return [
                "@THIS" if m.index == "0" else "@THAT",
                "D=A",
                "@R13",
                "M=D",
            ] + pop_to_r13()
        return [f"@{str(int(m.index) + 16)}", "D=A", "@R13", "M=D"] + pop_to_r13()


def translate(instructions: Iterable[Instruction]) -> Iterator[str]:
    """Translates a sequence of instructions into a sequence of assembly code lists.

    Args:
        instructions: An iterable of instructions to be translated.

    Yields:
        list[str]: Lists of strings representing the assembly code for each instruction.
    """
    label_counter = 0

    for instruction in instructions:
        if isinstance(instruction, ArithmeticLogicalCommand):
            asm_code, label_counter = translate_stack_instruction(
                instruction, label_counter
            )
            yield from asm_code
        else:
            yield from translate_memory_access_instruction(instruction)
