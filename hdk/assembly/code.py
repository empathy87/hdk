"""Provides functions to translate 'Instruction' objects into their binary values."""
import collections
from collections.abc import Iterable, Iterator
from typing import NamedTuple

from hdk.assembly.syntax import AInstruction, CInstruction, Command, Instruction, Label

_COMP_BINARY_CODES = {
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
_JUMP_BINARY_CODES = {
    None: "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}


class HackSymbolTable(collections.UserDict):
    """Manages a Hack program's symbol table.

    The symbol table is used to keep track of symbols (labels and variables)
    encountered in the assembly code, and their corresponding memory locations.
    """

    _PREDEFINED_SYMBOLS = {
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
        super().__init__(self._PREDEFINED_SYMBOLS)
        self._last_variable_location = 15

    def assign_variable_address(self, name: str) -> int:
        """Assigns a variable to the next available address in the Hack RAM.

        Variables are mapped to consecutive RAM locations as they are first
        encountered in a program, starting at RAM 16.

        Args:
            name: A string representing variable name.

        Returns:
            The integer address of the Hack RAM where the variable value is stored.
        """
        if name in self.data:
            raise ValueError(f"Variable name {name!r} is already in use.")
        self._last_variable_location += 1
        location = self._last_variable_location
        self.data[name] = location
        return location

    def get_address(self, symbol: str) -> int:
        """Returns the address assigned to a given symbol.
        It assigns a new address if the symbol is not already in the symbol table.

        Args:
            symbol: A string representing the symbol name.
        Returns:
            An integer representing the memory address assigned to the symbol.
        """
        if symbol in self:
            return self[symbol]
        return self.assign_variable_address(symbol)


def translate_a_instruction(a: AInstruction, symbols: HackSymbolTable) -> str:
    """Translates an A-Instruction into its 16-bit binary code using the symbol table.

    The symbol table contains the label symbols filled during the first pass.
    The variable symbols are handled in this function.

    Args:
        a: An A-Instruction object.
        symbols: A symbol table.

    Returns:
        A string that contains the 16-bit instruction code.
    """
    if a.is_constant:
        value = int(a.symbol)
    else:
        value = symbols.get_address(a.symbol)
    return format(value, "016b")


def _translate_dest(dest: str | None) -> str:
    """Converts a destination field into its binary code.

    Args:
        dest: An optional string representing the destination field of a C-Instruction.

    Returns:
        A string representing the binary code of the destination field.

    Typical usage example:
        >>> _translate_dest('AM')
        '101'
    """
    if dest is None:
        return "000"
    a_bit = int("A" in dest)
    d_bit = int("D" in dest)
    m_bit = int("M" in dest)

    return f"{a_bit}{d_bit}{m_bit}"


def translate_c_instruction(c: CInstruction) -> str:
    """Translates a C-Instruction into the binary code.

    Args:
        c: A C-Instruction object.

    Returns:
        A string that contains the 16-bit binary code for the instruction.

    Typical usage example:
        >>> translate_c_instruction(CInstruction(comp="1", dest="M"))
        '1110111111001000'
    """
    return (
        "111"
        + _COMP_BINARY_CODES[c.comp]
        + _translate_dest(c.dest)
        + _JUMP_BINARY_CODES[c.jump]
    )


class _FirstPassResult(NamedTuple):
    commands: list[Command]
    symbol_table: HackSymbolTable


def _do_first_pass(instructions: Iterable[Instruction]) -> _FirstPassResult:
    """Performs the first pass of the translation process and builds a symbol table.

    During this pass, the assembler reads the symbolic assembly code from beginning to
    end, adds all the label symbols to the symbol table, and generates no code.

    Args:
        instructions: An iterable of symbolic assembly instructions.

    Returns:
        A tuple containing a list of A- and C-Instructions, and the symbol table.
    """
    symbol_table = HackSymbolTable()
    commands: list[Command] = []
    for instruction in instructions:
        if isinstance(instruction, Label):
            symbol = instruction.symbol
            if symbol in symbol_table:
                raise ValueError(f"Label symbol {symbol!r} is already in use.")
            symbol_table[symbol] = len(commands)
        else:
            commands.append(instruction)
    return _FirstPassResult(commands, symbol_table)


def translate(instructions: Iterable[Instruction]) -> Iterator[str]:
    """Translates symbolic instructions into 16-bit codes represented as strings.

    Args:
        instructions: An iterable of symbolic instructions.

    Yields:
        A string representation of the 16-bit code for each instruction.
    """
    commands, symbol_table = _do_first_pass(instructions)
    for instruction in commands:
        if isinstance(instruction, AInstruction):
            yield translate_a_instruction(instruction, symbol_table)
        else:
            yield translate_c_instruction(instruction)


def link_instructions(instructions: Iterable[Instruction]) -> list[Command]:
    """Translates symbolic instructions into executable commands.

    Args:
        instructions: An iterable of symbolic instructions.

    Returns:
        A list of linked commands.
    """
    commands, symbol_table = _do_first_pass(instructions)
    linked_commands = []
    for command in commands:
        if isinstance(command, AInstruction) and not command.symbol.isdigit():
            address = symbol_table.get_address(command.symbol)
            command = AInstruction(symbol=str(address))
        linked_commands.append(command)
    return linked_commands
