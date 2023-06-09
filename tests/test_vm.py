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
        (
            "SimpleFunction",
            300,
            [
                (0, 317),
                (1, 317),
                (2, 310),
                (3, 3000),
                (4, 4000),
                (310, 1234),
                (311, 37),
                (312, 1000),
                (313, 305),
                (314, 300),
                (315, 3010),
                (316, 4010),
            ],
            [(0, 311), (1, 305), (2, 300), (3, 3010), (4, 4010), (310, 1196)],
        ),
        (
            "BasicLoop",
            600,
            [(0, 256), (1, 300), (2, 400), (400, 3)],
            [(0, 257), (256, 6)],
        ),
        (
            "FibonacciSeries",
            600,
            [(0, 256), (1, 300), (2, 400), (400, 6), (401, 3000)],
            [(3000, 0), (3001, 1), (3002, 1), (3003, 2), (3004, 3), (3005, 5)],
        ),
        (
            "NestedCall",
            4000,
            [
                (0, 261),
                (1, 261),
                (2, 256),
                (3, -3),
                (4, -4),
                (5, -1),
                (6, -1),
                (256, 1234),
                (257, -1),
                (258, -2),
                (259, -3),
                (260, -4),
                (261, -1),
                (262, -1),
                (263, -1),
                (264, -1),
                (265, -1),
                (266, -1),
                (267, -1),
                (268, -1),
                (269, -1),
                (270, -1),
                (271, -1),
                (272, -1),
                (273, -1),
                (274, -1),
                (275, -1),
                (276, -1),
                (277, -1),
                (278, -1),
                (279, -1),
                (280, -1),
                (281, -1),
                (282, -1),
                (283, -1),
                (284, -1),
                (285, -1),
                (286, -1),
                (287, -1),
                (288, -1),
                (289, -1),
                (290, -1),
                (291, -1),
                (292, -1),
                (293, -1),
                (294, -1),
                (295, -1),
                (296, -1),
                (297, -1),
                (298, -1),
                (299, -1),
            ],
            [(0, 261), (1, 261), (2, 256), (3, 4000), (4, 5000), (5, 135), (6, 246)],
        ),
        (
            "StaticsTest|Class1|Class2",
            2500,
            [(0, 256)],
            [(0, 263), (261, -2), (262, 8)],
        ),
        ("FibonacciElement|Main", 6000, [(0, 256)], [(0, 262), (261, 3)]),
    ]
    for files, steps, initial_memory_values, target_memory_values in programs:
        asm_file = tmpdir_with_programs / (files.split("|")[0] + ".asm")
        f = asm_file.open("w")
        for file in files.split("|"):
            vm_file = tmpdir_with_programs / (file + ".vm")
            asm_f = tmpdir_with_programs / (file + ".asm")
            translate_program(vm_file)
            for cmd in asm_f.open("r").readlines():
                f.write(cmd)
        f.close()
        instructions = parse_program(asm_file)
        memory = array.array("h", [0] * HACK_RAM_SIZE)
        for address, value in initial_memory_values:
            memory[address] = value
        emulator.run(instructions, steps, memory)
        for address, target_value in target_memory_values:
            value = memory[address]
            assert (
                value == target_value
            ), f"Program {programs} M[{address}]={value} instead of {target_value}."
