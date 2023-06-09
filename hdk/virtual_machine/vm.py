"""Initializes the I/O files and drives the translation for a vm program."""
from collections.abc import Iterable, Iterator
from pathlib import Path

from hdk.virtual_machine import code
from hdk.virtual_machine.parser import parse_vm_command
from hdk.virtual_machine.syntax import VMCommand


def parse_source_code(lines: Iterable[str]) -> Iterator[VMCommand]:
    """Parses lines of the vm code into command objects..

    Args:
        lines: An iterable containing the lines of vm code.

    Yields:
        Command objects representing lines of parsed vm code.

    Raises:
        ValueError if a line of source code cannot be parsed.
    """
    for line_num, line in enumerate(lines):
        line = line.strip()
        if len(line) == 0 or line.startswith("//"):
            continue
        try:
            yield parse_vm_command(line)
        except ValueError as e:
            raise ValueError(f"Cannot parse line {line_num  + 1}.") from e


def parse_program(source_path: Path) -> Iterator[VMCommand]:
    """Parses a vm program into command objects.

    Args:
        source_path: The path to the source program text file.

    Yields:
        Command objects parsed from the source code.
    """

    def _file_lines() -> Iterator[str]:
        with open(source_path) as file:
            yield from file

    return parse_source_code(_file_lines())


def translate_program(source_path: Path) -> None:
    """Translates a vm program into assembly code.

    The resulting code is saved in a text file with the same name as the source file,
    but with a .asm extension.

    Args:
        source_path: The path to the source program text file.
    """
    destination_path = source_path.parents[0] / (source_path.stem + ".asm")
    commands = parse_program(source_path)
    with open(destination_path, "w") as output_file:
        for assembly_code_line in code.translate(commands, source_path.stem):
            output_file.write(assembly_code_line + "\n")
