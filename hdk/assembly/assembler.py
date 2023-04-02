"""Initializes the I/O files and drives the assembly program translation process."""
from collections.abc import Iterable, Iterator
from pathlib import Path

from hdk.assembly import code
from hdk.assembly.parser import parse, preprocess
from hdk.assembly.syntax import Instruction


def parse_source_code(lines: Iterable[str]) -> Iterator[Instruction]:
    """Parses lines the of symbolic assembly source code into instruction objects."""
    for line_num, line in enumerate(lines):
        instruction = preprocess(line)
        if len(instruction) == 0:
            continue
        try:
            yield parse(instruction)
        except ValueError as e:
            raise ValueError(f"Cannot parse line {line_num  + 1}.") from e


def parse_program(path: Path) -> Iterator[Instruction]:
    """Parses the symbolic assembly program into instruction objects."""

    def _file_lines() -> Iterator[str]:
        with open(path) as file:
            yield from file

    return parse_source_code(_file_lines())


def translate_program(source: Path) -> None:
    """Translates Hack assembly program into executable Hack binary code.

    The generated code is written into a text file of the same name
    with .hack extension.

    Args:
        source: The path to the source program supplied in a text file.
    """
    destination = source.parents[0] / (source.stem + ".hack")
    instructions = parse_program(source)
    with open(destination, "w") as file:
        for binary_instruction in code.translate(instructions):
            file.write(binary_instruction + "\n")
