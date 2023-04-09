"""Provides automated testing for the Hack assembler."""
import filecmp
import shutil
from pathlib import Path

import pytest
from _pytest.fixtures import fixture

from hdk.assembly import assembler


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
    """A test case for correct Hack assembly programs.

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
