import xml.dom.minidom
from collections.abc import Iterable, Iterator
from pathlib import Path

from hdk.jack_analyzer.lex_analyzer_parser import parse_line
from hdk.jack_analyzer.syntax_tokens import Token


def parse_source_code(lines: Iterable[str]) -> Iterator[Token]:
    is_comment = False
    for line_num, line in enumerate(lines):
        line = line.strip().split("//")[0]
        if line.startswith("/*"):
            is_comment = True
        if line.endswith("*/"):
            is_comment = False
            continue
        if len(line) == 0 or is_comment:
            continue
        try:
            yield from parse_line(line)
        except ValueError as e:
            raise ValueError(f"Cannot parse line {line_num  + 1}.") from e


def parse_program(source_path: Path) -> Iterator[Token]:
    def _file_lines() -> Iterator[str]:
        with open(source_path) as file:
            yield from file

    return parse_source_code(_file_lines())


def get_tokens(source_path: Path) -> None:
    destination_path = source_path.parents[0] / (source_path.stem + "_myT.xml")
    tokens = parse_program(source_path)

    dom_tree = xml.dom.minidom.parseString("<tokens></tokens>")
    for token in tokens:
        newToken = dom_tree.createElement(token.type)
        newToken.appendChild(dom_tree.createTextNode(token.value))
        dom_tree.childNodes[0].appendChild(newToken)
    with open(destination_path, "w") as f:
        f.write(dom_tree.childNodes[0].toprettyxml())
