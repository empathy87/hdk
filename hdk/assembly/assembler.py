from pathlib import Path

from hdk.assembly import parser, translator


def compile_file(source: Path) -> None:
    destination = source.parents[0] / (source.stem + ".hack")
    instructions = parser.parse_source_file(source)
    with open(destination, "w") as file:
        for binary_instruction in translator.translate(instructions):
            file.write(binary_instruction + "\n")
