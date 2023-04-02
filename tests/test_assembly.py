import filecmp
import shutil
from pathlib import Path

import pytest
from _pytest.fixtures import fixture

from hdk.assembly import assembler


@fixture
def test_source_files(tmpdir, request) -> Path:
    tmpdir = Path(tmpdir) / "test_files"
    test_path = Path(request.module.__file__)
    test_data_path = test_path.parents[0] / (test_path.stem + "_data")
    if test_data_path.is_dir():
        shutil.copytree(test_data_path, tmpdir)
    return tmpdir


def test_translate_correct_programs(test_source_files):
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
        assembly_file = test_source_files / (program + ".asm")
        hack_file = test_source_files / (program + ".hack")
        target_hack_file = test_source_files / (program + ".hack_target")
        assembler.translate_program(assembly_file)
        is_correct = filecmp.cmp(hack_file, target_hack_file, shallow=False)
        assert is_correct, f"Program {program} translation is incorrect"


def test_translate_incorrect_program():
    with pytest.raises(ValueError) as e:
        list(
            assembler.parse_source_code(
                """
               D=M              // D = second number
               @OUTPUT_D
               0;JMP            // goto output_d
            (OUTPUT_FIRST
               @R0
           """.split(
                    "\n"
                )
            )
        )
    assert e.value.args[0] == "Cannot parse line 5."
