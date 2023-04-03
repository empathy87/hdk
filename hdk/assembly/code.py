"""Translates instruction objects into corresponding binary values."""
import collections
from collections.abc import Iterable
from typing import NamedTuple

from hdk.assembly.syntax import AInstruction, CInstruction, Command, Instruction, Label

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
    """Manages a Hack program's symbol table."""

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

    def map_variable(self, name: str) -> int:
        """Assigns a variable to the address in the Hack RAM.

        Variables are mapped to consecutive RAM locations as they are first
        encountered in a program, starting at RAM 16.

        Args:
            name: The variable symbol.

        Returns:
            An integer address in the Hack RAM where the variable value is stored.
        """
        if name in self.data:
            raise ValueError(f"Variable name {name!r} is already in use.")
        self._last_variable_location += 1
        self.data[name] = self._last_variable_location
        return self._last_variable_location


def translate_a_instruction(a: AInstruction, symbols: SymbolTable) -> str:
    """Translates an A-Instruction into the binary code using the symbol table.

    The symbol table contains the label symbols filled during the first pass.
    The variable symbols are handled in this function.

    Args:
        a: The A-Instruction object.
        symbols: The symbol table.

    Returns:
        The string that contains 16-bit instruction code.
    """
    if a.is_constant:
        value = int(a.symbol)
    else:
        if a.symbol in symbols:
            value = symbols[a.symbol]
        else:
            value = symbols.map_variable(a.symbol)
    return "0" + f"{value:b}".zfill(15)


def _translate_dest(dest: str | None) -> str:
    """Translates a destination field into the corresponding binary code.

    >>> _translate_dest('AM')
    '101'
    """
    if dest is None:
        return "000"
    return f"{int('A' in dest)}{int('D' in dest)}{int('M' in dest)}"


def translate_c_instruction(c: CInstruction) -> str:
    """Translates a C-Instruction into the binary code.

    >>> translate_c_instruction(CInstruction(comp="1", dest="M"))
    '1110111111001000'
    """
    return (
        "111"
        + _COMP_TRANSLATION_TABLE[c.comp]
        + _translate_dest(c.dest)
        + _JMP_TRANSLATION_TABLE[c.jump]
    )


class _FirstPassResult(NamedTuple):
    ac_instructions: list[Command]
    symbol_table: SymbolTable


def _do_first_pass(instructions: Iterable[Instruction]) -> _FirstPassResult:
    """Performs the first pass of the translation process and builds the symbol table.

    In the first pass, the assembler reads the code from start to end, builds a symbol
    table, adds all the label symbols into the table, and generates no code.

    Args:
        instructions: Symbolic assembly instructions.

    Returns:
        A tuple where the first element is a list of A- and C-Instructions (without
        Label instructions), and the second element is a symbol table.
    """
    symbol_table = SymbolTable()
    ac_instructions: list[Command] = []
    for instruction in instructions:
        if isinstance(instruction, Label):
            symbol = instruction.symbol
            if symbol in symbol_table:
                raise ValueError(f"Label symbol {symbol!r} is already in use.")
            symbol_table[symbol] = len(ac_instructions)
        else:
            ac_instructions.append(instruction)
    return _FirstPassResult(ac_instructions, symbol_table)


def translate(instructions: Iterable[Instruction]) -> Iterable[str]:
    """Translates symbolic instructions into 16-bit codes represented as strings."""
    ac_instructions, symbol_table = _do_first_pass(instructions)
    for instruction in ac_instructions:
        if isinstance(instruction, AInstruction):
            yield translate_a_instruction(instruction, symbol_table)
        else:
            yield translate_c_instruction(instruction)
