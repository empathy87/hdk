"""Provides automated testing for the Hack assembler."""
import array
import filecmp
import shutil
from pathlib import Path

import pytest
from _pytest.fixtures import fixture

from hdk.assembly import assembler, emulator
from hdk.assembly.assembler import parse_program
from hdk.assembly.emulator import HACK_RAM_SIZE


@fixture
def tmpdir_with_programs(tmpdir, request) -> Path:
    """Returns a path to a temporary directory containing files for testing."""
    path = Path(tmpdir) / "programs"
    test_path = Path(request.module.__file__)
    test_data_path = test_path.parents[0] / (test_path.stem + "_data")
    if test_data_path.is_dir():
        shutil.copytree(test_data_path, path)
    return path


def test_translate_correct_programs(tmpdir_with_programs):
    """A test case for emulating correct Hack assembly programs.

    Runs the translation for several correct Hack assembly programs and compares the
    output of the assembler with the expected results stored in .hack_target files.
    """
    programs = [
        "Add",
        "Max",
        "MaxL",
        "Pong",
        "PongL",
        "Rect",
        "RectL",
    ]
    for program in programs:
        assembly_file = tmpdir_with_programs / (program + ".asm")
        hack_file = tmpdir_with_programs / (program + ".hack")
        target_hack_file = tmpdir_with_programs / (program + ".hack_target")
        assembler.translate_program(assembly_file)
        is_correct = filecmp.cmp(hack_file, target_hack_file, shallow=False)
        assert is_correct, f"Program {program} translation is incorrect"


def test_emulate_correct_programs(tmpdir_with_programs):
    """A test case for correct Hack assembly programs.

    Runs the emulator for several correct Hack assembly programs and compares memory
    with the expected results in some cells.
    """

    programs = [
        ("Add", 6, [], [(0, 5)]),
        ("Max", 20, [(0, 5), (1, 18)], [(2, 18)]),
        ("MaxL", 20, [(0, 100), (1, -18)], [(2, 100)]),
        ("Pong", 25, [], [(0, 257), (14, 27058), (256, 145)]),
        ("Rect", 10, [(0, 11)], [(16, 11), (17, 16384)]),
    ]
    for program, steps, initial_memory_values, target_memory_values in programs:
        assembly_file = tmpdir_with_programs / (program + ".asm")
        instructions = parse_program(assembly_file)
        memory = array.array("h", [0] * HACK_RAM_SIZE)
        for address, value in initial_memory_values:
            memory[address] = value
        emulator.run(instructions, steps, memory)
        for address, target_value in target_memory_values:
            value = memory[address]
            assert (
                value == target_value
            ), f"Program {program} M[{address}]={value} instead of {target_value}"


def test_translate_incorrect_program():
    """A test case for an incorrect Hack assembly program.

    Ensures that the assembler raises an exception with a message that contains the
    line number with the syntax error.
    """
    program = """
           D=M              // D = second number
           @OUTPUT_D
           0;JMP            // goto output_d
        (OUTPUT_FIRST
           @R0
    """
    with pytest.raises(ValueError) as e:
        list(assembler.parse_source_code(program.split("\n")))
    assert e.value.args[0] == "Cannot parse line 5."
