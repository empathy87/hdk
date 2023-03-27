"""Translates instructions into corresponding binary values."""
import collections
from collections.abc import Iterable

from hdk.assembly.syntax import AInstruction, CInstruction, Label

Instruction = Label | AInstruction | CInstruction


_COMP_TRANSLATION_TABLE = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "!D": "0001101",
    "!A": "0110001",
    "-D": "0001111",
    "-A": "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000",
    "!M": "1110001",
    "-M": "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101",
}
_JMP_TRANSLATION_TABLE = {
    None: "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}


class SymbolTable(collections.UserDict):
    """Manages the symbol table."""

    _predefined_symbols = {
        **{f"R{i}": i for i in range(16)},
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "THIS": 3,
        "THAT": 4,
        "SCREEN": 16384,
        "KBD": 24576,
    }

    def __init__(self):
        super().__init__(self._predefined_symbols)
        self._last_variable_location = 15

    def map_variable(self, symbol: str) -> int:
        if symbol in self.data:
            raise ValueError(f"Variable name {symbol!r} is already in use.")
        self._last_variable_location += 1
        self.data[symbol] = self._last_variable_location
        return self._last_variable_location


def translate_a_instruction(a: AInstruction, symbols: SymbolTable) -> str:
    if a.is_constant:
        value = int(a.symbol)
    else:
        if a.symbol in symbols:
            value = symbols[a.symbol]
        else:
            value = symbols.map_variable(a.symbol)
    return "0" + f"{value:b}".zfill(15)


def _translate_dest(dest):
    """Translates destination into binary code.

    >>> _translate_dest('AM')
    '101'
    """
    if dest is None:
        return "000"
    return f"{int('A' in dest)}{int('D' in dest)}{int('M' in dest)}"


def translate_c_instruction(c: CInstruction) -> str:
    """Translates C-Instruction into binary code

    >>> translate_c_instruction(CInstruction(comp="1", dest="M"))
    '1110111111001000'
    """
    return (
        "111"
        + _COMP_TRANSLATION_TABLE[c.comp]
        + _translate_dest(c.dest)
        + _JMP_TRANSLATION_TABLE[c.jump]
    )


def _first_pass(instructions) -> tuple[list[AInstruction | CInstruction], SymbolTable]:
    symbol_table = SymbolTable()
    ac_instructions: list[AInstruction | CInstruction] = []
    for instruction in instructions:
        if isinstance(instruction, Label):
            symbol = instruction.symbol
            if symbol in symbol_table:
                raise ValueError(f"Label symbol {symbol!r} is already in use.")
            symbol_table[symbol] = len(ac_instructions)
        else:
            ac_instructions.append(instruction)
    return ac_instructions, symbol_table


def translate(instructions: Iterable[Instruction]) -> Iterable[str]:
    ac_instructions, symbol_table = _first_pass(instructions)
    for instruction in ac_instructions:
        if isinstance(instruction, AInstruction):
            yield translate_a_instruction(instruction, symbol_table)
        else:
            yield translate_c_instruction(instruction)
