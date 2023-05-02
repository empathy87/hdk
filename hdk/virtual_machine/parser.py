"""Functions for parsing symbolic instructions into their underlying fields."""
import re

from hdk.virtual_machine.syntax import (
    Instruction,
    MemoryAccessInstruction,
    StackInstruction,
)


def remove_comment(line: str) -> str:
    """Removes any comments from a given line of vm source code.

    Args:
        line: A line of code that may contain a comment.

    Returns:
        The line of code with any comment removed.

    Typical usage example:
        >>> remove_comment('// The whole line is a comment')
        ''
        >>> remove_comment('Command // comment')
        'Command '
    """
    return line.partition("//")[0]


def remove_whitespaces(line: str) -> str:
    """Removes all whitespace characters from a given line of vm source code.

    Args:
        line: A line of code that may contain whitespace characters.

    Returns:
        The line of code with all whitespace characters removed.

    Typical usage example:
        >>> remove_whitespaces('    push    constant          17     ')
        'push constant 17'
    """
    return re.sub(r"\s+", " ", " " + line + " ")[1:-1]


def clean_line(line: str) -> str:
    """Removes comments and whitespace from a line of source code.

    Args:
        line: A string representing a line of source code.

    Returns:
        The line of source code with comments and whitespace removed.

    Typical usage example:
        >>> clean_line('     push    constant          17  // some comment')
        'push constant 17'
    """
    line = remove_comment(line)
    line = remove_whitespaces(line)
    return line


def parse_vm_instruction(instruction_text: str) -> Instruction:
    """Parses a symbolic Hack assembly instruction into its underlying fields.

    Args:
        instruction_text: The symbolic instruction to be parsed.

    Returns:
        An instance of either AInstruction, CInstruction, or Label, representing
        the parsed instruction.

    Typical usage example:
        >>> parse_vm_instruction('push constant 17')
        MemoryAccessInstruction(command='push', segment='constant', index='17')
        >>> parse_vm_instruction('add')
        StackInstruction(command='add')
    """
    if instruction_text.startswith("push") or instruction_text.startswith("pop"):
        command, segment, idx = instruction_text.split()
        return MemoryAccessInstruction(command=command, segment=segment, index=idx)
    return StackInstruction(command=instruction_text)
