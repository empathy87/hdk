"""Provides function 'run' to emulate assembler code."""
from array import array
from collections.abc import Callable, Iterable

from hdk.assembly.code import link_instructions
from hdk.assembly.syntax import AInstruction, Instruction

HACK_RAM_SIZE = 24576

JUMP_CONDITIONS: dict[str | None, Callable[[int], bool]] = {
    None: lambda comp_result: False,
    "JMP": lambda comp_result: True,
    "JLE": lambda comp_result: comp_result <= 0,
    "JNE": lambda comp_result: comp_result != 0,
    "JLT": lambda comp_result: comp_result < 0,
    "JGE": lambda comp_result: comp_result >= 0,
    "JEQ": lambda comp_result: comp_result == 0,
    "JGT": lambda comp_result: comp_result > 0,
}


COMPUTE_OPERATIONS: dict[str, Callable[[int, int, int], int]] = {
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
    """Modifies the memory array according to the iterable of symbolic instructions.

    Args:
        instructions: An iterable of symbolic instructions.
        steps: An integer number of commands to execute.
        memory: An array of signed integers to be modified by the instructions.

    Raises:
        ValueError: If the instruction tries to access memory beyond the HACK_RAM_SIZE.
    """
    commands = link_instructions(instructions)
    pc, a, d = 0, 0, 0
    for _ in range(steps):
        curr_command = commands[pc]
        if isinstance(curr_command, AInstruction):
            a = int(curr_command.symbol)
            pc += 1
            continue
        if "M" not in curr_command.comp:
            m = 0
        elif a >= HACK_RAM_SIZE:
            raise ValueError("Out of memory.")
        else:
            m = memory[a]
        comp_result = compute(curr_command.comp, a, d, m)
        if curr_command.is_m_dest:
            memory[a] = comp_result
        if curr_command.is_a_dest:
            a = comp_result
        if curr_command.is_d_dest:
            d = comp_result
        if JUMP_CONDITIONS[curr_command.jump](comp_result):
            pc = a
        else:
            pc += 1


def compute(comp: str, a: int, d: int, m: int) -> int:
    """Computes the result from the registers using the comp instruction.

    Args:
        a: An integer value of A-register.
        d: An integer value of D-register.
        m: An integer value of RAM (addressed by A-register).

    Returns:
        An integer of computation result.

    Typical usage example:
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
    result = COMPUTE_OPERATIONS[comp](a, d, m)
    result &= 0xFFFF
    if (result & 0x8000) != 0:
        result = (result & 0x7FFF) - 0x7FFF - 1
    return result
