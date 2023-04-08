"""Functions for parsing symbolic instructions into their underlying fields."""
import re

from hdk.assembly.syntax import AInstruction, CInstruction, Instruction, Label


def remove_comment(line: str) -> str:
    """Removes any comments from a given line of assembly source code.

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
    """Removes all whitespace characters from a given line of assembly source code.

    Args:
        line: A line of code that may contain whitespace characters.

    Returns:
        The line of code with all whitespace characters removed.

    Typical usage example:
        >>> remove_whitespaces('    DM = A +1 ; JGZ ')
        'DM=A+1;JGZ'
    """
    return re.sub(r"\s+", "", line)


def clean_line(line: str) -> str:
    """Removes comments and whitespace from a line of source code.

    Args:
        line: A string representing a line of source code.

    Returns:
        The line of source code with comments and whitespace removed.

    Typical usage example:
        >>> clean_line('    D = D - M;JMP  // continue a loop')
        'D=D-M;JMP'
    """
    line = remove_comment(line)
    line = remove_whitespaces(line)
    return line


def parse_assembly_instruction(instruction_text: str) -> Instruction:
    """Parses a symbolic Hack assembly instruction into its underlying fields.

    Args:
        instruction_text: The symbolic instruction to be parsed.

    Returns:
        An instance of either AInstruction, CInstruction, or Label, representing
        the parsed instruction.

    Typical usage example:
        >>> parse_assembly_instruction('@i')
        AInstruction(symbol='i')
        >>> parse_assembly_instruction('(LOOP)')
        Label(symbol='LOOP')
        >>> parse_assembly_instruction('M=M+1')
        CInstruction(comp='M+1', dest='M', jump=None)
        >>> parse_assembly_instruction('D;JGT')
        CInstruction(comp='D', dest=None, jump='JGT')
        >>> parse_assembly_instruction('M=M+1;JGT')
        CInstruction(comp='M+1', dest='M', jump='JGT')
    """
    if instruction_text.startswith("@"):
        return AInstruction(instruction_text[1:])
    if instruction_text.startswith("(") and instruction_text.endswith(")"):
        return Label(instruction_text[1:-1])

    dest, jump = None, None
    if (equal_sign_index := instruction_text.find("=")) != -1:
        dest = instruction_text[:equal_sign_index]
        instruction_text = instruction_text[equal_sign_index + 1 :]
    if (semicolon_index := instruction_text.find(";")) != -1:
        jump = instruction_text[semicolon_index + 1 :]
        instruction_text = instruction_text[:semicolon_index]
    return CInstruction(comp=instruction_text, dest=dest, jump=jump)
