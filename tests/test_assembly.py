import shutil
from pathlib import Path

from _pytest.fixtures import fixture

from hdk.assembly import assembler


@fixture
def test_files(tmpdir, request) -> Path:
    tmpdir = Path(tmpdir) / "test_files"
    test_path = Path(request.module.__file__)
    test_data_path = test_path.parents[0] / (test_path.stem + "_data")
    if test_data_path.is_dir():
        shutil.copytree(test_data_path, tmpdir)
    return tmpdir


def test_compile_add_programs(test_files):
    programs = [
        "Add.asm",
        "Max.asm",
        "MaxL.asm",
        "Pong.asm",
        "PongL.asm",
        "Rect.asm",
        "RectL.asm",
    ]
    for program in programs:
        assembler.translate_program(test_files / program)
