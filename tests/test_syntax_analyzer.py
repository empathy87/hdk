import shutil
import xml.dom.minidom
from pathlib import Path
from xml.dom.minidom import Document, Element

from _pytest.fixtures import fixture

from hdk.jack_analyzer.parser import TokensIterator, parse_class

from hdk.jack_analyzer.tokenizer import tokenize_program, to_xml


@fixture
def tmpdir_with_programs(tmpdir, request) -> Path:
    """Returns a path to a temporary directory containing files for testing."""
    path = Path(tmpdir) / "programs"
    test_path = Path(request.module.__file__)
    test_data_path = test_path.parents[0] / (test_path.stem + "_data")
    if test_data_path.is_dir():
        shutil.copytree(test_data_path, path)
    return path


def compare_node_values(element1: Element, element2: Element) -> bool:
    if element1.nodeName != element2.nodeName:
        return False
    if element1.nodeValue is None or element2.nodeValue is None:
        return element1.nodeValue == element2.nodeValue
    node_value1 = element1.nodeValue.replace(" ", "").replace("\t", "")
    node_value2 = element2.nodeValue.replace(" ", "").replace("\t", "")
    return node_value1 == node_value2


def compare_elements(element1: Element, element2: Element) -> bool:
    if len(element1.childNodes) != len(element2.childNodes) or not compare_node_values(
            element1, element2
    ):
        return False
    if len(element1.childNodes) == 0:
        return True
    for i in range(len(element1.childNodes)):
        if compare_elements(element1.childNodes[i], element2.childNodes[i]) is False:
            return False
    return True


def test_tokenizer_programs(tmpdir_with_programs):
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
        my_dom_tree = to_xml(tokenize_program(full_path))
        compare_to_file_path = full_path.parents[0] / (full_path.stem + "T.xml")
        f = "".join(open(compare_to_file_path).read().split("\n"))
        compare_to_dom_tree = xml.dom.minidom.parseString(f)
        assert compare_elements(
            my_dom_tree.childNodes[0], compare_to_dom_tree.childNodes[0]
        ), "Error."


def test_parser_program(tmpdir_with_programs):
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
        program_tokens = TokensIterator(tokenize_program(Path(full_path)))
        A = parse_class(program_tokens)
        d_tree = Document()
        a = A.export_to_xml(d_tree)
        d_tree.appendChild(a)
        compare_to_file_path = full_path.parents[0] / (full_path.stem + ".xml")
        file_to_compare = open(compare_to_file_path, "r")
        compare_to_tree = xml.dom.minidom.parse(file_to_compare)
        _clean_formatting(compare_to_tree)

        assert compare_elements(
            d_tree.childNodes[0], compare_to_tree.childNodes[0]
        ), "Error."


def _clean_formatting(element: Element):
    children = list(element.childNodes)
    has_child_element = any(isinstance(e, Element) for e in children)
    if has_child_element:
        for e in children:
            if not isinstance(e, Element):
                element.removeChild(e)
            else:
                _clean_formatting(e)
    else:
        for e in children:
            e.data = e.data.strip()
            if len(e.data) == 0:
                element.removeChild(e)
