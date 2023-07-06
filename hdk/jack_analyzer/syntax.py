from __future__ import annotations

from collections import UserList
from dataclasses import dataclass
from typing import TypeAlias
from xml.dom.minidom import Document, Element
from enum import Enum


def _add_child(element: Element, tag_name: str, value: str | None) -> Element:
    dom_tree = element.ownerDocument
    child = dom_tree.createElement(tag_name)
    child.appendChild(dom_tree.createTextNode(value))
    element.appendChild(child)
    return child


@dataclass(frozen=True)
class Parameter:
    type_: str
    var_name: str


class ParameterList(UserList[Parameter]):
    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("parameterList")
        for i, parameter in enumerate(self):
            element_type = (
                "keyword" if parameter.type_ in {"int", "char", "boolean"}
                else "identifier"
            )
            _add_child(element, element_type, parameter.type_)
            _add_child(element, "identifier", parameter.var_name)
            if i < len(self) - 1:
                _add_child(element, "symbol", ",")
        return element


class ConstantTermType(Enum):
    KEYWORD = 0
    INTEGER = 1
    STRING = 2


@dataclass(frozen=True)
class ConstantTerm:
    type_: ConstantTermType
    value: str

    def to_xml(self, dom_tree: Document) -> Element:
        type_to_str: dict[ConstantTermType, str] = {
            ConstantTermType.KEYWORD: "keyword",
            ConstantTermType.INTEGER: "integerConstant",
            ConstantTermType.STRING: "stringConstant"
        }
        element = dom_tree.createElement("term")
        _add_child(element, type_to_str[self.type_], self.value)
        return element


@dataclass(frozen=True)
class VarTerm:
    var_name: str
    expression: Expression | None

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("term")
        _add_child(element, "identifier", self.var_name)
        if self.expression is not None:
            _add_child(element, "symbol", "[")
            element.appendChild(self.expression.to_xml(dom_tree))
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
        if self.unaryOp is not None:
            element = dom_tree.createElement("term")
            _add_child(element, "symbol", self.unaryOp)
            element.appendChild(self.term.to_xml(dom_tree))
            return element
        return self.term.to_xml(dom_tree)


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
    expressions: Expressions

    def to_xml(self, dom_tree: Document, element: Element) -> Element:
        if self.owner is not None:
            _add_child(element, "identifier", self.owner)
            _add_child(element, "symbol", ".")
        _add_child(element, "identifier", self.name)
        _add_child(element, "symbol", "(")
        element.appendChild(self.expressions.to_xml(dom_tree))
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
    subroutine_call: SubroutineCall

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("doStatement")
        _add_child(element, "keyword", "do")
        element = self.subroutine_call.to_xml(dom_tree, element)
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class LetStatement:
    var_name: str
    indexer: Expression | None
    expression: Expression

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("letStatement")
        _add_child(element, "keyword", "let")
        _add_child(element, "identifier", self.var_name)
        if self.indexer is not None:
            _add_child(element, "symbol", "[")
            element.appendChild(self.indexer.to_xml(dom_tree))
            _add_child(element, "symbol", "]")
        _add_child(element, "symbol", "=")
        element.appendChild(self.expression.to_xml(dom_tree))
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class IfStatement:
    expression: Expression
    if_statements: Statements
    else_statements: Statements | None

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("ifStatement")
        _add_child(element, "keyword", "if")
        _add_child(element, "symbol", "(")
        element.appendChild(self.expression.to_xml(dom_tree))
        _add_child(element, "symbol", ")")
        _add_child(element, "symbol", "{")
        element.appendChild(self.if_statements.to_xml(dom_tree))
        _add_child(element, "symbol", "}")
        if self.else_statements is not None:
            _add_child(element, "keyword", "else")
            _add_child(element, "symbol", "{")
            element.appendChild(self.else_statements.to_xml(dom_tree))
            _add_child(element, "symbol", "}")
        return element


@dataclass(frozen=True)
class WhileStatement:
    expression: Expression
    statements: Statements

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("whileStatement")
        _add_child(element, "keyword", "while")
        _add_child(element, "symbol", "(")
        element.appendChild(self.expression.to_xml(dom_tree))
        _add_child(element, "symbol", ")")
        _add_child(element, "symbol", "{")
        element.appendChild(self.statements.to_xml(dom_tree))
        _add_child(element, "symbol", "}")
        return element


Statement: TypeAlias = ReturnStatement | DoStatement | LetStatement | IfStatement | WhileStatement


@dataclass(frozen=True)
class Statements:
    statements: list[Statement]

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("statements")
        for statement in self.statements:
            element.appendChild(statement.to_xml(dom_tree))
        return element


@dataclass(frozen=True)
class VarDeclaration:
    type_: str
    names: list[str]

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("varDec")
        _add_child(element, "keyword", "var")
        element_type = (
            "keyword"
            if self.type_ in {"int", "char", "boolean"}
            else "identifier"
        )
        _add_child(element, element_type, self.type_)
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
    type_: [str, str]
    name: str
    parameters: ParameterList
    body: SubroutineBody

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("subroutineDec")
        _add_child(element, "keyword", self.type_[0])
        element_type = (
            "keyword"
            if self.type_[1] in {"int", "char", "boolean", "void"}
            else "identifier"
        )
        _add_child(element, element_type, self.type_[1])
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

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("classVarDec")
        _add_child(element, "keyword", self.modifier)
        element_type = (
            "keyword"
            if self.type_ in {"int", "char", "boolean"}
            else "identifier"
        )
        _add_child(element, element_type, self.type_)
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
