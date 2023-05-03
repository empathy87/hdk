"""Functions for parsing virtual machine commands into their underlying fields."""
from hdk.virtual_machine.syntax import (
    ArithmeticLogicalCommand,
    MemoryTransferCommand,
    VMCommand,
)


def parse_vm_command(line: str) -> VMCommand:
    """Parses a symbolic vm command into its underlying fields.

    Args:
        line: The symbolic command to be parsed.

    Returns:
        An instance of either MemoryTransferCommand or ArithmeticLogicalCommand,
        representing the parsed command.

    Typical usage example:
        >>> parse_vm_command('push constant 17')
        MemoryTransferCommand(command='push', segment='constant', index='17')
        >>> parse_vm_command('add')
        ArithmeticLogicalCommand(command='add')
    """
    if line.startswith("push") or line.startswith("pop"):
        operation, segment, idx = line.split()
        return MemoryTransferCommand(
            operation=operation, segment=segment, index=int(idx)
        )
    return ArithmeticLogicalCommand(operation=line)
