"""Initializes the I/O files and drives the translation for an assembly program."""
from collections.abc import Iterable, Iterator
from pathlib import Path

from hdk.assembly import code
from hdk.assembly.parser import clean_line, parse_assembly_instruction
from hdk.assembly.syntax import Instruction


def parse_source_code(lines: Iterable[str]) -> Iterator[Instruction]:
    """Parses lines of the symbolic assembly source code into instruction objects.

    Args:
        lines: An iterable containing the lines of symbolic assembly source code.

    Yields:
        Instruction objects representing lines of parsed assembly code.

    Raises:
        ValueError if a line of source code cannot be parsed.
    """
    for line_num, line in enumerate(lines):
        preprocessed_line = clean_line(line)
        if len(preprocessed_line) == 0:
            continue
        try:
            yield parse_assembly_instruction(preprocessed_line)
        except ValueError as e:
            raise ValueError(f"Cannot parse line {line_num  + 1}.") from e


def parse_program(source_path: Path) -> Iterator[Instruction]:
    """Parses a symbolic assembly program into instruction objects.

    Args:
        source_path: The path to the source program text file.

    Yields:
        Instruction objects parsed from the source code.
    """

    def _file_lines() -> Iterator[str]:
        with open(source_path) as file:
            yield from file

    return parse_source_code(_file_lines())


def translate_program(source_path: Path) -> None:
    """Translates a Hack assembly program into executable Hack binary code.

    The resulting code is saved in a text file with the same name as the source file,
    but with a .hack extension.

    Args:
        source_path: The path to the source program text file.
    """
    destination = source_path.parents[0] / (source_path.stem + ".hack")
    instructions = parse_program(source_path)
    with open(destination, "w") as file:
        for binary_instruction in code.translate(instructions):
            file.write(binary_instruction + "\n")
