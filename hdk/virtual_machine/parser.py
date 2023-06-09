"""Functions for parsing virtual machine commands into their underlying fields."""
from hdk.virtual_machine.syntax import (
    ArithmeticLogicalCommand,
    BranchingCommand,
    FunctionCommand,
    MemoryTransferCommand,
    VMCommand,
)


def parse_vm_command(line: str) -> VMCommand:
    line = line.partition("//")[0]
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
    if (
        line.startswith("label")
        or line.startswith("goto")
        or line.startswith("if-goto")
    ):
        operation, label_name = line.split()
        return BranchingCommand(operation=operation, label_name=label_name)
    if line.startswith("return"):
        return FunctionCommand(operation="return", function_name=None, n_vars_args=None)
    if line.startswith("function") or line.startswith("call"):
        operation, function_name, n_vars_args = line.split()
        return FunctionCommand(
            operation=operation,
            function_name=function_name,
            n_vars_args=int(n_vars_args),
        )
    return ArithmeticLogicalCommand(operation=line.split()[0])
