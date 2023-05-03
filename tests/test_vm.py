"""Provides automated testing for the Hack assembler."""
import array
import shutil
from pathlib import Path

from _pytest.fixtures import fixture

from hdk.assembly import emulator
from hdk.assembly.assembler import parse_program
from hdk.assembly.emulator import HACK_RAM_SIZE
from hdk.virtual_machine.vm import translate_program


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
    """A test case for emulating correct vm programs.

    Runs the translation for several correct vm programs and compares the
    outgoing memory with the expected results.
    """
    programs = [
        ("SimpleAdd", 60, [(0, 256)], [(0, 257), (256, 15)]),
        (
            "StackTest",
            1000,
            [(0, 256)],
            [
                (0, 266),
                (256, -1),
                (257, 0),
                (258, 0),
                (259, 0),
                (260, -1),
                (261, 0),
                (262, -1),
                (263, 0),
                (264, 0),
                (265, -91),
            ],
        ),
        (
            "BasicTest",
            600,
            [(0, 256), (1, 300), (2, 400), (3, 3000), (4, 3010)],
            [
                (256, 472),
                (300, 10),
                (401, 21),
                (402, 22),
                (3006, 36),
                (3012, 42),
                (3015, 45),
                (11, 510),
            ],
        ),
        (
            "PointerTest",
            450,
            [(0, 256)],
            [(256, 6084), (3, 3030), (4, 3040), (3032, 32), (3046, 46)],
        ),
        ("StaticTest", 200, [(0, 256)], [(256, 1110)]),
    ]
    for program, steps, initial_memory_values, target_memory_values in programs:
        vm_file = tmpdir_with_programs / (program + ".vm")
        translate_program(vm_file)
        asm_file = tmpdir_with_programs / (program + ".asm")
        instructions = parse_program(asm_file)
        memory = array.array("h", [0] * HACK_RAM_SIZE)
        for address, value in initial_memory_values:
            memory[address] = value
        emulator.run(instructions, steps, memory)
        for address, target_value in target_memory_values:
            value = memory[address]
            assert (
                value == target_value
            ), f"Program {program} M[{address}]={value} instead of {target_value}."
