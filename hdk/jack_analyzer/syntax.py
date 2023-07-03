from __future__ import annotations
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
class ParameterList:
    parameters: list[tuple[str, str]]

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("parameterList")
        for i, (_type, var_name) in enumerate(self.parameters):
            element_type = (
                "keyword" if _type in {"int", "char", "boolean"}
                else "identifier"
            )
            _add_child(element, element_type, _type)
            _add_child(element, "identifier", var_name)
            if i < len(self.parameters) - 1:
                _add_child(element, "symbol", ",")
        return element


class SimpleTermType(Enum):
    KEYWORD_CONSTANT = 0
    INTEGER_CONSTANT = 1
    STRING_CONSTANT = 2
    VAR_NAME = 3


@dataclass(frozen=True)
class Term:
    unaryOp: str | None
    type_: SimpleTermType | Expression | SubroutineCall | Term
    value: str | None
    expression: Expression | None

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("term")
        type_to_str: dict[SimpleTermType, str] = {
            SimpleTermType.KEYWORD_CONSTANT: "keyword",
            SimpleTermType.VAR_NAME: "identifier",
            SimpleTermType.INTEGER_CONSTANT: "integerConstant",
            SimpleTermType.STRING_CONSTANT: "stringConstant"
        }
        if self.unaryOp is not None:
            _add_child(element, "symbol", self.unaryOp)
            element.appendChild(self.type_.export_to_xml(dom_tree))
            return element
        if isinstance(self.type_, SimpleTermType):
            _add_child(element, type_to_str[self.type_], self.value)
            if self.expression is not None:
                _add_child(element, "symbol", "[")
                element.appendChild(self.expression.export_to_xml(dom_tree))
                _add_child(element, "symbol", "]")
        elif isinstance(self.type_, Expression):
            _add_child(element, "symbol", "(")
            element.appendChild(self.type_.export_to_xml(dom_tree))
            _add_child(element, "symbol", ")")
        else:
            element = self.type_.export_to_xml(dom_tree, element)
        return element


@dataclass(frozen=True)
class Expression:
    first_term: Term
    term_list: list[tuple[str, Term]]

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("expression")
        element.appendChild(self.first_term.export_to_xml(dom_tree))
        for op, term in self.term_list:
            _add_child(element, "symbol", op)
            element.appendChild(term.export_to_xml(dom_tree))
        return element


@dataclass(frozen=True)
class ExpressionList:
    expression_list: list[Expression]

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("expressionList")
        for i, expr in enumerate(self.expression_list):
            element.appendChild(expr.export_to_xml(dom_tree))
            if i < len(self.expression_list) - 1:
                _add_child(element, "symbol", ",")
        return element


@dataclass(frozen=True)
class SubroutineCall:
    name: tuple[str | None, str]
    expressions: ExpressionList

    def export_to_xml(self, dom_tree: Document, element: Element) -> Element:
        if self.name[0] is not None:
            _add_child(element, "identifier", self.name[0])
            _add_child(element, "symbol", ".")
        _add_child(element, "identifier", self.name[1])
        _add_child(element, "symbol", "(")
        element.appendChild(self.expressions.export_to_xml(dom_tree))
        _add_child(element, "symbol", ")")
        return element


@dataclass(frozen=True)
class ReturnStatement:
    expression: Expression | None

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("returnStatement")
        _add_child(element, "keyword", "return")
        if self.expression is not None:
            element.appendChild(self.expression.export_to_xml(dom_tree))
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class DoStatement:
    subroutine_call: SubroutineCall

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("doStatement")
        _add_child(element, "keyword", "do")
        element = self.subroutine_call.export_to_xml(dom_tree, element)
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class LetStatement:
    var_name: str
    var_expression: Expression | None
    expression: Expression

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("letStatement")
        _add_child(element, "keyword", "let")
        _add_child(element, "identifier", self.var_name)
        if self.var_expression is not None:
            _add_child(element, "symbol", "[")
            element.appendChild(self.var_expression.export_to_xml(dom_tree))
            _add_child(element, "symbol", "]")
        _add_child(element, "symbol", "=")
        element.appendChild(self.expression.export_to_xml(dom_tree))
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class IfStatement:
    expression: Expression
    statements_if: Statements
    statements_else: Statements | None

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("ifStatement")
        _add_child(element, "keyword", "if")
        _add_child(element, "symbol", "(")
        element.appendChild(self.expression.export_to_xml(dom_tree))
        _add_child(element, "symbol", ")")
        _add_child(element, "symbol", "{")
        element.appendChild(self.statements_if.export_to_xml(dom_tree))
        _add_child(element, "symbol", "}")
        if self.statements_else is not None:
            _add_child(element, "keyword", "else")
            _add_child(element, "symbol", "{")
            element.appendChild(self.statements_else.export_to_xml(dom_tree))
            _add_child(element, "symbol", "}")
        return element


@dataclass(frozen=True)
class WhileStatement:
    expression: Expression
    statements: Statements

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("whileStatement")
        _add_child(element, "keyword", "while")
        _add_child(element, "symbol", "(")
        element.appendChild(self.expression.export_to_xml(dom_tree))
        _add_child(element, "symbol", ")")
        _add_child(element, "symbol", "{")
        element.appendChild(self.statements.export_to_xml(dom_tree))
        _add_child(element, "symbol", "}")
        return element


Statement: TypeAlias = ReturnStatement | DoStatement | LetStatement | IfStatement | WhileStatement


@dataclass(frozen=True)
class Statements:
    statements: list[Statement]

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("statements")
        for statement in self.statements:
            element.appendChild(statement.export_to_xml(dom_tree))
        return element


@dataclass(frozen=True)
class Var:
    type_: str
    vars_names: list[str]

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("varDec")
        _add_child(element, "keyword", "var")
        element_type = (
            "keyword"
            if self.type_ in {"int", "char", "boolean"}
            else "identifier"
        )
        _add_child(element, element_type, self.type_)
        for i, var_name in enumerate(self.vars_names):
            _add_child(element, "identifier", var_name)
            if i < len(self.vars_names) - 1:
                _add_child(element, "symbol", ",")
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class SubroutineBody:
    var_dec_list: list[Var]
    statements: Statements

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("subroutineBody")
        _add_child(element, "symbol", "{")
        for var_dec in self.var_dec_list:
            element.appendChild(var_dec.export_to_xml(dom_tree))
        element.appendChild(self.statements.export_to_xml(dom_tree))
        _add_child(element, "symbol", "}")
        return element


@dataclass(frozen=True)
class Subroutine:
    type_: [str, str]
    name: str
    parameters: ParameterList
    body: SubroutineBody

    def export_to_xml(self, dom_tree: Document) -> Element:
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
        element.appendChild(self.parameters.export_to_xml(dom_tree))
        _add_child(element, "symbol", ")")
        element.appendChild(self.body.export_to_xml(dom_tree))
        return element


@dataclass(frozen=True)
class ClassVar:
    type_: tuple[str, str]
    vars_names: list[str]

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("classVarDec")
        _add_child(element, "keyword", self.type_[0])
        element_type = (
            "keyword"
            if self.type_[1] in {"int", "char", "boolean"}
            else "identifier"
        )
        _add_child(element, element_type, self.type_[1])
        for i, var_name in enumerate(self.vars_names):
            _add_child(element, "identifier", var_name)
            if i < len(self.vars_names) - 1:
                _add_child(element, "symbol", ",")
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class Class:
    name: str
    class_vars: list[ClassVar]
    subroutines: list[Subroutine]

    def export_to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("class")
        _add_child(element, "keyword", "class")
        _add_child(element, "identifier", self.name)
        _add_child(element, "symbol", "{")
        for class_var_dec in self.class_vars:
            element.appendChild(class_var_dec.export_to_xml(dom_tree))
        for subroutine_dec in self.subroutines:
            element.appendChild(subroutine_dec.export_to_xml(dom_tree))
        _add_child(element, "symbol", "}")
        return element
