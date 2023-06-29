from dataclasses import dataclass
from enum import Enum
from xml.dom.minidom import Document, Element


def create_simple_element(dom_tree: Document, tag_name: str, value: str) -> Element:
    element = dom_tree.createElement(tag_name)
    element.appendChild(dom_tree.createTextNode(value))
    return element


@dataclass(frozen=True)
class Identifier:
    value: str

    def export_to_xml(self, dom_tree: Document) -> Element:
        return create_simple_element(dom_tree, "identifier", self.value)


@dataclass(frozen=True)
class SubroutineType(Enum):
    CONSTRUCTOR = 0
    FUNCTION = 1
    METHOD = 2


_type_to_str: dict[str, str] = {
    "CONSTRUCTOR": "constructor",
    "FUNCTION": "function",
    "METHOD": "method"
}


@dataclass(frozen=True)
class SubroutineReturnType(Enum):
    INT = 0
    CHAR = 1
    BOOLEAN = 2
    VOID = 3


_return_type_to_str: dict[str, str] = {
    "INT": "int",
    "CHAR": "char",
    "BOOLEAN": "boolean",
    "VOID": "void"
}


@dataclass(frozen=True)
class ReturnStatement:
    expression: None

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("returnStatement")
        element.appendChild(create_simple_element(dom_tree, "keyword", "return"))
        if self.expression is not None:
            pass
        element.appendChild(create_simple_element(dom_tree, "symbol", ";"))
        return element


@dataclass(frozen=True)
class Statement:
    statement: ReturnStatement

    def export_to_xml(self, dom_tree: Document) -> Element:
        return self.statement.export_to_xml(dom_tree)


@dataclass(frozen=True)
class Statements:
    statements_list: list[Statement]

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("statements")
        for statement in self.statements_list:
            element.appendChild(statement.export_to_xml(dom_tree))
        return element


@dataclass(frozen=True)
class ParameterList:
    parameter_list: list[None]

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("parameterList")
        for _ in self.parameter_list:
            pass
        return element


@dataclass(frozen=True)
class SubroutineBody:
    var_dec_list: list[None]
    statements: Statements

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("subroutineBody")
        element.appendChild(create_simple_element(dom_tree, "symbol", "{"))
        element.appendChild(self.statements.export_to_xml(dom_tree))
        element.appendChild(create_simple_element(dom_tree, "symbol", "}"))
        return element


@dataclass(frozen=True)
class SubroutineDec:
    subroutine_type: SubroutineType
    subroutine_return_type: SubroutineReturnType | Identifier
    subroutine_name: Identifier
    parameter_list: ParameterList
    subroutine_body: SubroutineBody

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("subroutineDec")
        element.appendChild(
            create_simple_element(dom_tree, "keyword", _type_to_str[self.subroutine_type.name])
        )
        if isinstance(self.subroutine_return_type, Identifier):
            element.appendChild(self.subroutine_return_type.export_to_xml(dom_tree))
        elif isinstance(self.subroutine_return_type, SubroutineReturnType):
            element.appendChild(
                create_simple_element(
                    dom_tree,
                    "keyword",
                    _return_type_to_str[self.subroutine_return_type.name]
                )
            )
        element.appendChild(self.subroutine_name.export_to_xml(dom_tree))
        element.appendChild(create_simple_element(dom_tree, "symbol", "("))
        element.appendChild(self.parameter_list.export_to_xml(dom_tree))
        element.appendChild(create_simple_element(dom_tree, "symbol", ")"))
        element.appendChild(self.subroutine_body.export_to_xml(dom_tree))
        return element


@dataclass(frozen=True)
class Class:
    class_name: Identifier
    # class_var_dec_list: list[ClassVarDec]
    subroutine_dec_list: list[SubroutineDec]

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("class")
        element.appendChild(create_simple_element(dom_tree, "keyword", "class"))
        element.appendChild(self.class_name.export_to_xml(dom_tree))
        element.appendChild(create_simple_element(dom_tree, "symbol", "{"))
        for subroutine_dec in self.subroutine_dec_list:
            element.appendChild(subroutine_dec.export_to_xml(dom_tree))
        element.appendChild(create_simple_element(dom_tree, "symbol", "}"))
        return element
