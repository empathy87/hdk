"""Functions for parsing virtual machine commands into their underlying fields."""
from hdk.virtual_machine.syntax import (
    ArithmeticLogicalCommand,
    Instruction,
    MemoryTransferCommand,
)


def parse_vm_instruction(instruction_text: str) -> Instruction:
    """Parses a symbolic Hack assembly instruction into its underlying fields.

    Args:
        instruction_text: The symbolic instruction to be parsed.

    Returns:
        An instance of either AInstruction, CInstruction, or Label, representing
        the parsed instruction.

    Typical usage example:
        >>> parse_vm_instruction('push constant 17')
        MemoryAccessInstruction(command='push', segment='constant', index='17')
        >>> parse_vm_instruction('add')
        StackInstruction(command='add')
    """
    if instruction_text.startswith("push") or instruction_text.startswith("pop"):
        command, segment, idx = instruction_text.split()
        return MemoryTransferCommand(command=command, segment=segment, index=int(idx))
    return ArithmeticLogicalCommand(command=instruction_text)
