import shutil
from pathlib import Path

from _pytest.fixtures import fixture

from hdk.jack_analyzer.tokenizer import get_tokens


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
    programs = [
        "ArrayTest\\Main.jack",
        "ExpressionLessSquare\\Main.jack",
        "ExpressionLessSquare\\Square.jack",
        "ExpressionLessSquare\\SquareGame.jack",
        "Square\\Main.jack",
        "Square\\Square.jack",
        "Square\\SquareGame.jack",
    ]
    for path in programs:
        full_path = tmpdir_with_programs / path

        dom_tree = get_tokens(full_path)
        z1 = tmpdir_with_programs / path.split("\\")[0] / (full_path.stem + "_myT.xml")
        with open(z1, "w") as f:
            f.write(dom_tree.childNodes[0].toprettyxml())

        z2 = tmpdir_with_programs / path.split("\\")[0] / (full_path.stem + "T.xml")
        f1 = z1.open().readlines()
        f2 = z2.open().readlines()
        for i in range(max(len(f1), len(f2))):
            line1 = f1[i].replace(" ", "").replace("\t", "") if i < len(f1) else ""
            line2 = f2[i].replace(" ", "").replace("\t", "") if i < len(f1) else ""
            assert line1 == line2, f"Program {path} {line1} instead of {line2}."
