from array import array
from collections.abc import Callable, Iterable

from hdk.assembly.code import link_instructions
from hdk.assembly.syntax import AInstruction, Command, Instruction

_JUMP_TABLE: dict[str | None, Callable[[int], bool]] = {
    None: lambda comp_result: False,
    "JMP": lambda comp_result: True,
    "JLE": lambda comp_result: comp_result <= 0,
    "JNE": lambda comp_result: comp_result != 0,
    "JLT": lambda comp_result: comp_result < 0,
    "JGE": lambda comp_result: comp_result >= 0,
    "JEQ": lambda comp_result: comp_result == 0,
    "JGT": lambda comp_result: comp_result > 0,
}


_COMP_TABLE: dict[str, Callable[[int, int, int], int]] = {
    "0": lambda a, d, m: 0,
    "1": lambda a, d, m: 1,
    "-1": lambda a, d, m: -1,
    "D": lambda a, d, m: d,
    "A": lambda a, d, m: a,
    "!D": lambda a, d, m: ~d,
    "!A": lambda a, d, m: ~a,
    "-D": lambda a, d, m: -d,
    "-A": lambda a, d, m: -a,
    "D+1": lambda a, d, m: d + 1,
    "A+1": lambda a, d, m: a + 1,
    "D-1": lambda a, d, m: d - 1,
    "A-1": lambda a, d, m: a - 1,
    "D+A": lambda a, d, m: d + a,
    "D-A": lambda a, d, m: d - a,
    "A-D": lambda a, d, m: a - d,
    "D&A": lambda a, d, m: d & a,
    "D|A": lambda a, d, m: d | a,
    "M": lambda a, d, m: m,
    "!M": lambda a, d, m: ~m,
    "-M": lambda a, d, m: -m,
    "M+1": lambda a, d, m: m + 1,
    "M-1": lambda a, d, m: m - 1,
    "D+M": lambda a, d, m: d + m,
    "D-M": lambda a, d, m: d - m,
    "M-D": lambda a, d, m: m - d,
    "D&M": lambda a, d, m: d & m,
    "D|M": lambda a, d, m: d | m,
}


def run(instructions: Iterable[Instruction], steps: int, memory: array) -> None:
    """Modifies memory by instructions

    Args:
        instructions: An iterable of symbolic instructions.
        steps: number of commands to execute
        memory: an array of signed int

    Returns:

    """
    commands = link_instructions(instructions)
    pc, a, d = 0, 0, 0
    for _ in range(steps):
        curr_command: Command = commands[pc]
        if isinstance(curr_command, AInstruction):
            a = int(curr_command.symbol)
            pc += 1
            continue
        m = memory[a] if a <= 24576 else None
        result = compute(curr_command.comp, a, d, m)
        if curr_command.is_m_dest:
            memory[a] = result
        if curr_command.is_a_dest:
            a = result
        if curr_command.is_d_dest:
            d = result
        if _JUMP_TABLE[curr_command.jump](result):
            pc = a
        else:
            pc += 1


def compute(comp: str, a: int, d: int, m: int) -> int:
    """
    >>> compute("!D", a=0, d=1, m=0)
    -2
    >>> compute("D+1", a=0, d=32767, m=0)
    -32768
    >>> compute("D-1", a=0, d=-32768, m=0)
    32767
    >>> compute("D+A", a=32767, d=-32768, m=0)
    -1
    >>> compute("D-A", a=32767, d=-32768, m=0)
    1
    >>> compute("D+A", a=327, d=-32767, m=0)
    -32440
    >>> compute("D+A", a=32767, d=32767, m=0)
    -2
    >>> compute("-D", a=0, d=-32768, m=0)
    -32768
    >>> compute("A-D", a=5, d=-32768, m=0)
    -32763
    """
    result = _COMP_TABLE[comp](a, d, m)
    result &= 0xFFFF
    if (result & 0x8000) != 0:
        result = (result & 0x7FFF) - 0x7FFF - 1
    return result
