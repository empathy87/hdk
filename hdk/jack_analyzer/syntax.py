from dataclasses import dataclass
from typing import TypeAlias
from xml.dom.minidom import Document, Element


def _add_child(element: Element, tag_name: str, value: str | None) -> Element:
    dom_tree = element.ownerDocument
    child = dom_tree.createElement(tag_name)
    child.appendChild(dom_tree.createTextNode(value))
    element.appendChild(child)
    return child


@dataclass(frozen=True)
class ReturnStatement:
    expression: None

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("returnStatement")
        _add_child(element, "keyword", "return")
        if self.expression is not None:
            pass
        _add_child(element, "symbol", ";")
        return element


Statement: TypeAlias = ReturnStatement


@dataclass(frozen=True)
class Subroutine:
    type_: str
    return_type: str
    name: str
    parameters: list[None]
    variables: list[None]
    statements: list[Statement]

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("subroutineDec")
        _add_child(element, "keyword", self.type_)
        element_type = (
            "keyword"
            if self.return_type in {"int", "char", "boolean", "void"}
            else "identifier"
        )
        _add_child(element, element_type, self.return_type)
        _add_child(element, "identifier", self.name)
        _add_child(element, "symbol", "(")
        parameters = dom_tree.createElement("parameterList")
        for _ in self.parameters:
            pass
        element.appendChild(parameters)
        _add_child(element, "symbol", ")")
        body = dom_tree.createElement("subroutineBody")
        _add_child(body, "symbol", "{")
        statements = dom_tree.createElement("statements")
        for statement in self.statements:
            statements.appendChild(statement.export_to_xml(dom_tree))
        body.appendChild(statements)
        _add_child(body, "symbol", "}")
        element.appendChild(body)
        return element


@dataclass(frozen=True)
class Class:
    name: str
    # class_var_dec_list: list[ClassVarDec]
    subroutines: list[Subroutine]

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("class")
        _add_child(element, "keyword", "class")
        _add_child(element, "identifier", self.name)
        _add_child(element, "symbol", "{")
        for subroutine_dec in self.subroutines:
            element.appendChild(subroutine_dec.export_to_xml(dom_tree))
        _add_child(element, "symbol", "}")
        return element
