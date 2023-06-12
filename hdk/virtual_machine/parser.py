"""Functions for parsing virtual machine commands into their underlying fields."""
from hdk.virtual_machine.syntax import (
    ArithmeticLogicalCommand,
    BranchingCommand,
    FunctionCallCommand,
    FunctionDefinitionCommand,
    MemoryTransferCommand,
    ReturnCommand,
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
    line = line.partition("//")[0]
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
        return ReturnCommand()
    if line.startswith("function"):
        operation, function_name, n_vars = line.split()
        return FunctionDefinitionCommand(
            function_name=function_name,
            n_vars=int(n_vars),
        )
    if line.startswith("call"):
        operation, function_name, n_args = line.split()
        return FunctionCallCommand(
            function_name=function_name,
            n_args=int(n_args),
        )
    return ArithmeticLogicalCommand(operation=line.split()[0])
