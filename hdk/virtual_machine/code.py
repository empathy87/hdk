"""Provides functions to translate VM commands into their assembly instructions."""
from collections.abc import Iterable, Iterator

from hdk.virtual_machine.syntax import (
    ArithmeticLogicalCommand,
    BranchingCommand,
    FunctionCommand,
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


def translate_label(label_name: str) -> list[str]:
    """Translates a label operation into assembly instructions.

    Args:
        label_name: The symbol defined by the Label.

    Returns:
        A list of Hack assembly instructions.
    """
    return [f"({label_name})"]


def translate_goto(label_name: str) -> list[str]:
    """Translates a goto operation into assembly instructions.

    Args:
        label_name: The symbol defined by the Label.

    Returns:
        A list of Hack assembly instructions.
    """
    return [f"@{label_name}", "0;JMP"]


def translate_if_goto(label_name: str) -> list[str]:
    """Translates an if-goto operation into assembly instructions.

    Args:
        label_name: The symbol defined by the Label.

    Returns:
        A list of Hack assembly instructions.
    """
    return ["@SP", "AM=M-1", "D=M", f"@{label_name}", "D;JNE"]


def translate_branching_command(command: BranchingCommand) -> list[str]:
    """Translates a BranchingCommand into its assembly code.

    Args:
        command: The BranchingCommand to translate.

    Returns:
         A list of assembly code instructions.
    """
    if command.operation == "label":
        return translate_label(command.label_name)
    if command.operation == "goto":
        return translate_goto(command.label_name)
    if command.operation == "if-goto":
        return translate_if_goto(command.label_name)
    raise ValueError(f"Wrong operation {command.operation!r} for branching command.")


def translate_call(
    function_name: str, n_args: int | None, command_id: int
) -> list[str]:
    """Translates a call command into its assembly code.

    Args:
        function_name: The symbol defined by the function.
        n_args: The number of arguments.
        command_id: The current command number.

    Returns:
        A list of assembly code instructions.
    """
    output = [
        f"@{function_name}{command_id}",
        "D=A",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
    ]
    for segment in ["LCL", "ARG", "THIS", "THAT"]:
        output += [f"@{segment}", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1"]
    output += [
        "@SP",
        "D=M",
        "@5",
        "D=D-A",
        f"@{n_args}",
        "D=D-A",
        "@ARG",
        "M=D",
        "@SP",
        "D=M",
        "@LCL",
        "M=D",
        f"@{function_name}",
        "0;JMP",
        f"({function_name}{command_id})",
    ]
    return output


def translate_return():
    """Translates a return command into its assembly code.

    Returns:
        A list of assembly code instructions.
    """
    output = [
        "@LCL",
        "D=M",
        "@R13",
        "M=D",
        "@5",
        "A=D-A",
        "D=M",
        "@R14",
        "M=D",
        "@SP",
        "AM=M-1",
        "D=M",
        "@ARG",
        "A=M",
        "M=D",
        "@ARG",
        "D=M+1",
        "@SP",
        "M=D",
    ]
    for seg in ["THAT", "THIS", "ARG", "LCL"]:
        output += ["@R13", "AM=M-1", "D=M", f"@{seg}", "M=D"]
    return output + ["@R14", "A=M", "0;JMP"]


def translate_function(function_name: str, n_vars: int | None) -> list[str]:
    """Translates a function command into its assembly code.

    Args:
        function_name: The symbol defined by the function.
        n_vars: The number of the function's variables.

    Returns:
         A list of assembly code instructions.
    """
    initialize_locals = []
    for _ in range(n_vars if n_vars is not None else 0):
        initialize_locals += translate_push("constant", 0) + _SAVE_D_INSTRUCTIONS
    return [f"({function_name})"] + initialize_locals


def translate_function_command(command: FunctionCommand, command_id) -> list[str]:
    """Translates a FunctionCommand into its assembly code.

    Args:
        command: The FunctionCommand to translate.
        command_id: The current command number.

    Returns:
         A list of assembly code instructions.
    """
    if command.operation == "return":
        return translate_return()
    if command.operation == "call":
        return translate_call(
            str(command.function_name), command.n_vars_args, command_id
        )
    if command.operation == "function":
        return translate_function(str(command.function_name), command.n_vars_args)
    raise ValueError(f"Invalid command {command.operation!r} for function command.")


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
        f"Invalid command {command.operation!r} for arithmetic-logical command."
    )


def translate_push(segment: str, index: int, file_name: str = "None") -> list[str]:
    """Translates a push operation into assembly instructions.

    Args:
        file_name:
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
        return [f"@{file_name}.{index}", "D=M"]
    raise ValueError(f"Wrong segment {segment!r} for VMcommand.")


def translate_pop(segment: str, index: int, file_name: str = "None") -> list[str]:
    """Translates a pop operation into Hack assembly instructions.

    Args:
        file_name:
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
            f"@{index + 5}",
            "D=A",
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
        return [f"@{file_name}.{index}", "D=A", "@R13", "M=D"]
    raise ValueError(f"Wrong segment {segment!r} for VMcommand.")


def translate_memory_transfer_command(
    command: MemoryTransferCommand, file_name: str
) -> list[str]:
    """Translates a MemoryTransferCommand into its assembly code.
    Args:
        file_name:
        command: The memory access instruction to be translated.

    Returns:
        The assembly code for the given memory access instruction.
    """
    if command.operation == "push":
        return (
            translate_push(command.segment, command.index, file_name)
            + _SAVE_D_INSTRUCTIONS
        )
    return (
        translate_pop(command.segment, command.index, file_name)
        + _RESTORE_D_INSTRUCTIONS
    )


def translate(commands: Iterable[VMCommand], file_name: str) -> Iterator[str]:
    """Translate VM-commands into assembly symbolic instructions.

    Args:
        file_name:
        commands: An iterable of commands to be translated.

    Yields:
        Strings representing the assembly code for each command.
    """
    for command_id, command in enumerate(commands):
        if isinstance(command, ArithmeticLogicalCommand):
            yield from translate_arithmetic_logical_command(command, command_id)
        elif isinstance(command, BranchingCommand):
            yield from translate_branching_command(command)
        elif isinstance(command, FunctionCommand):
            yield from translate_function_command(command, command_id)
        else:
            yield from translate_memory_transfer_command(command, file_name)
