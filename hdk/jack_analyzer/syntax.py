from __future__ import annotations

from collections import UserList
from dataclasses import dataclass
from typing import TypeAlias
from xml.dom.minidom import Document, Element
from enum import Enum


def _add_child(element: Element, tag_name: str, value: str) -> Element:
    dom_tree = element.ownerDocument
    child = dom_tree.createElement(tag_name)
    child.appendChild(dom_tree.createTextNode(value))
    element.appendChild(child)
    return child


@dataclass(frozen=True)
class Parameter:
    type_: str
    var_name: str

    @property
    def is_identifier(self) -> bool:
        return self.type_ not in {"int", "char", "boolean"}

    def to_xml(self, element: Element):
        _add_child(element, "identifier" if self.is_identifier else "keyword", self.type_)
        _add_child(element, "identifier", self.var_name)
        return element


class ParameterList(UserList[Parameter]):
    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("parameterList")
        for i, parameter in enumerate(self):
            element = parameter.to_xml(element)
            if i < len(self) - 1:
                _add_child(element, "symbol", ",")
        return element


class ConstantType(Enum):
    KEYWORD = 0
    INTEGER = 1
    STRING = 2


@dataclass(frozen=True)
class ConstantTerm:
    type_: ConstantType
    value: str

    def to_xml(self, dom_tree: Document) -> Element:
        type_to_str: dict[ConstantType, str] = {
            ConstantType.KEYWORD: "keyword",
            ConstantType.INTEGER: "integerConstant",
            ConstantType.STRING: "stringConstant"
        }
        element = dom_tree.createElement("term")
        _add_child(element, type_to_str[self.type_], self.value)
        return element


@dataclass(frozen=True)
class VarTerm:
    var_name: str
    index: Expression | None

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("term")
        _add_child(element, "identifier", self.var_name)
        if self.index is not None:
            _add_child(element, "symbol", "[")
            element.appendChild(self.index.to_xml(dom_tree))
            _add_child(element, "symbol", "]")
        return element


@dataclass(frozen=True)
class SubroutineCallTerm:
    call: SubroutineCall

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("term")
        element = self.call.to_xml(dom_tree, element)
        return element


@dataclass(frozen=True)
class ExpressionTerm:
    expression: Expression

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("term")
        _add_child(element, "symbol", "(")
        element.appendChild(self.expression.to_xml(dom_tree))
        _add_child(element, "symbol", ")")
        return element


@dataclass(frozen=True)
class UnaryOpTerm:
    unaryOp: str
    term: ConstantTerm | VarTerm | ExpressionTerm | SubroutineCallTerm

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("term")
        _add_child(element, "symbol", self.unaryOp)
        element.appendChild(self.term.to_xml(dom_tree))
        return element


Term: TypeAlias = VarTerm | ConstantTerm | UnaryOpTerm | SubroutineCallTerm | ExpressionTerm


@dataclass(frozen=True)
class Expression:
    first_term: Term
    term_list: list[tuple[str, Term]]

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("expression")
        element.appendChild(self.first_term.to_xml(dom_tree))
        for op, term in self.term_list:
            _add_child(element, "symbol", op)
            element.appendChild(term.to_xml(dom_tree))
        return element


class Expressions(UserList[Expression]):
    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("expressionList")
        for i, expr in enumerate(self):
            element.appendChild(expr.to_xml(dom_tree))
            if i < len(self) - 1:
                _add_child(element, "symbol", ",")
        return element


@dataclass(frozen=True)
class SubroutineCall:
    owner: str | None
    name: str
    arguments: Expressions

    def to_xml(self, dom_tree: Document, element: Element) -> Element:
        if self.owner is not None:
            _add_child(element, "identifier", self.owner)
            _add_child(element, "symbol", ".")
        _add_child(element, "identifier", self.name)
        _add_child(element, "symbol", "(")
        element.appendChild(self.arguments.to_xml(dom_tree))
        _add_child(element, "symbol", ")")
        return element


@dataclass(frozen=True)
class ReturnStatement:
    expression: Expression | None

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("returnStatement")
        _add_child(element, "keyword", "return")
        if self.expression is not None:
            element.appendChild(self.expression.to_xml(dom_tree))
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class DoStatement:
    call: SubroutineCall

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("doStatement")
        _add_child(element, "keyword", "do")
        element = self.call.to_xml(dom_tree, element)
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class LetStatement:
    var_name: str
    index: Expression | None
    expression: Expression

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("letStatement")
        _add_child(element, "keyword", "let")
        _add_child(element, "identifier", self.var_name)
        if self.index is not None:
            _add_child(element, "symbol", "[")
            element.appendChild(self.index.to_xml(dom_tree))
            _add_child(element, "symbol", "]")
        _add_child(element, "symbol", "=")
        element.appendChild(self.expression.to_xml(dom_tree))
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class IfStatement:
    condition: Expression
    if_: Statements
    else_: Statements | None

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("ifStatement")
        _add_child(element, "keyword", "if")
        _add_child(element, "symbol", "(")
        element.appendChild(self.condition.to_xml(dom_tree))
        _add_child(element, "symbol", ")")
        _add_child(element, "symbol", "{")
        element.appendChild(self.if_.to_xml(dom_tree))
        _add_child(element, "symbol", "}")
        if self.else_ is not None:
            _add_child(element, "keyword", "else")
            _add_child(element, "symbol", "{")
            element.appendChild(self.else_.to_xml(dom_tree))
            _add_child(element, "symbol", "}")
        return element


@dataclass(frozen=True)
class WhileStatement:
    condition: Expression
    body: Statements

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("whileStatement")
        _add_child(element, "keyword", "while")
        _add_child(element, "symbol", "(")
        element.appendChild(self.condition.to_xml(dom_tree))
        _add_child(element, "symbol", ")")
        _add_child(element, "symbol", "{")
        element.appendChild(self.body.to_xml(dom_tree))
        _add_child(element, "symbol", "}")
        return element


Statement: TypeAlias = ReturnStatement | DoStatement | LetStatement | IfStatement | WhileStatement


class Statements(UserList[Statement]):
    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("statements")
        for statement in self:
            element.appendChild(statement.to_xml(dom_tree))
        return element


@dataclass(frozen=True)
class VarDeclaration:
    type_: str
    names: list[str]

    @property
    def is_identifier(self) -> bool:
        return self.type_ not in {"int", "char", "boolean"}

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("varDec")
        _add_child(element, "keyword", "var")
        _add_child(element, "identifier" if self.is_identifier else "keyword", self.type_)
        for i, var_name in enumerate(self.names):
            _add_child(element, "identifier", var_name)
            if i < len(self.names) - 1:
                _add_child(element, "symbol", ",")
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class SubroutineBody:
    var_declarations: list[VarDeclaration]
    statements: Statements

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("subroutineBody")
        _add_child(element, "symbol", "{")
        for var_dec in self.var_declarations:
            element.appendChild(var_dec.to_xml(dom_tree))
        element.appendChild(self.statements.to_xml(dom_tree))
        _add_child(element, "symbol", "}")
        return element


@dataclass(frozen=True)
class SubroutineDeclaration:
    type_: str
    return_type: str
    name: str
    parameters: ParameterList
    body: SubroutineBody

    @property
    def is_identifier(self) -> bool:
        return self.return_type not in {"int", "char", "boolean", "void"}

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("subroutineDec")
        _add_child(element, "keyword", self.type_)
        _add_child(element, "identifier" if self.is_identifier else "keyword", self.return_type)
        _add_child(element, "identifier", self.name)
        _add_child(element, "symbol", "(")
        element.appendChild(self.parameters.to_xml(dom_tree))
        _add_child(element, "symbol", ")")
        element.appendChild(self.body.to_xml(dom_tree))
        return element


@dataclass(frozen=True)
class ClassVarDeclaration:
    modifier: str
    type_: str
    names: list[str]

    @property
    def is_identifier(self) -> bool:
        return self.type_ not in {"int", "char", "boolean"}

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("classVarDec")
        _add_child(element, "keyword", self.modifier)
        _add_child(element, "identifier" if self.is_identifier else "keyword", self.type_)
        for i, var_name in enumerate(self.names):
            _add_child(element, "identifier", var_name)
            if i < len(self.names) - 1:
                _add_child(element, "symbol", ",")
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class Class:
    name: str
    class_vars: list[ClassVarDeclaration]
    subroutines: list[SubroutineDeclaration]

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("class")
        _add_child(element, "keyword", "class")
        _add_child(element, "identifier", self.name)
        _add_child(element, "symbol", "{")
        for class_var_dec in self.class_vars:
            element.appendChild(class_var_dec.to_xml(dom_tree))
        for subroutine_dec in self.subroutines:
            element.appendChild(subroutine_dec.to_xml(dom_tree))
        _add_child(element, "symbol", "}")
        return element
