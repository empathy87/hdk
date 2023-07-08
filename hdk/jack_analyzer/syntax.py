"""Defines classes that represent different types of Jack syntax structures."""
from __future__ import annotations

import abc
from collections import UserList
from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar, NamedTuple, TypeAlias
from xml.dom.minidom import Document, Element


def _add_child(parent: Element, child_tag: str, child_value: str):
    """Builds and adds a child to the XML element.

    Args:
        parent: The XML element to add the child element to.
        child_tag: The tag of the child element.
        child_value: The text value of the child element.
    """
    doc = parent.ownerDocument
    child = doc.createElement(child_tag)
    child.appendChild(doc.createTextNode(child_value))
    parent.appendChild(child)


def _add_children(parent: Element, *children: Any):
    for child in children:
        match child:
            case str() as value:
                _add_child(parent, child_tag="symbol", child_value=value)
            case (str() as tag, str() as value):
                _add_child(parent, child_tag=tag, child_value=value)
            case Element() as child:
                parent.appendChild(child)


class AbstractSyntaxTree(abc.ABC):
    """Represents the abstract syntax tree."""

    @abc.abstractmethod
    def to_xml(self, doc: Document) -> Element:
        """Builds an XML element that represents the syntax structure.

        Args:
            doc: The owner XML document.

        Returns:
            The constructed XML element within the document.
        """
        pass


class Parameter(NamedTuple):
    """Represents a parameter with a type and variable name.

    Attributes:
        type_: The type of the parameter.
        var_name: The variable name of the parameter.
    """

    type_: str
    var_name: str

    @property
    def is_identifier(self) -> bool:
        """True if the parameter type is not one of the reserved keywords."""
        return self.type_ not in {"int", "char", "boolean"}


class ParameterList(UserList[Parameter], AbstractSyntaxTree):
    """Represents a list of parameters."""

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("parameterList")
        for i, parameter in enumerate(self):
            tag = "identifier" if parameter.is_identifier else "keyword"
            _add_children(
                element, (tag, parameter.type_), ("identifier", parameter.var_name)
            )
            if i < len(self) - 1:
                _add_child(element, "symbol", ",")
        return element


class ConstantType(Enum):
    """Represents constant types."""

    KEYWORD = 0
    INTEGER = 1
    STRING = 2


@dataclass(frozen=True)
class ConstantTerm(AbstractSyntaxTree):
    """Represents a constant term.

    Attributes:
        type_: The type of the constant term.
        value: The value of the constant term.
    """

    type_: ConstantType
    value: str
    _type_to_str: ClassVar[dict[ConstantType, str]] = {
        ConstantType.KEYWORD: "keyword",
        ConstantType.INTEGER: "integerConstant",
        ConstantType.STRING: "stringConstant",
    }

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("term")
        _add_child(element, ConstantTerm._type_to_str[self.type_], self.value)
        return element


@dataclass(frozen=True)
class VarTerm(AbstractSyntaxTree):
    """Represents a variable term.

    Attributes:
        var_name: The name of the variable.
        index: An optional index expression.
    """

    var_name: str
    index: Expression | None

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("term")
        _add_child(element, "identifier", self.var_name)
        if self.index is not None:
            _add_children(element, "[", self.index.to_xml(doc), "]")
        return element


@dataclass(frozen=True)
class SubroutineCall(AbstractSyntaxTree):
    """Represents a subroutine call abstract class.

    Attributes:
        owner: The owner (a class or an object) of the subroutine.
        name: The name of the subroutine.
        arguments: The list of arguments passed to the subroutine.
    """

    owner: str | None
    name: str
    arguments: Expressions

    def _write_content(self, element: Element):
        if self.owner is not None:
            _add_children(element, ("identifier", self.owner), ".")
        _add_children(
            element,
            ("identifier", self.name),
            "(",
            self.arguments.to_xml(element.ownerDocument),
            ")",
        )

    @abc.abstractmethod
    def to_xml(self, doc: Document) -> Element:
        pass


@dataclass(frozen=True)
class SubroutineCallTerm(SubroutineCall):
    """Represents a subroutine call term."""

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("term")
        self._write_content(element)
        return element


@dataclass(frozen=True)
class ExpressionTerm(AbstractSyntaxTree):
    """Represents an expression term.

    Attributes:
        expression: The expression.
    """

    expression: Expression

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("term")
        _add_children(element, "(", self.expression.to_xml(doc), ")")
        return element


@dataclass(frozen=True)
class UnaryOpTerm(AbstractSyntaxTree):
    """Represents a unary operation term.

    Attributes:
        unaryOp: The unary operator.
        term: The term.
    """

    unaryOp: str
    term: Term

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("term")
        _add_children(element, self.unaryOp, self.term.to_xml(doc))
        return element


@dataclass(frozen=True)
class Expression(AbstractSyntaxTree):
    """Represents an expression.

    Attributes:
        first_term: The first term of the expression.
        term_list: A list of tuples containing operators and terms.
    """

    first_term: Term
    term_list: list[tuple[str, Term]]

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("expression")
        element.appendChild(self.first_term.to_xml(doc))
        for op, term in self.term_list:
            _add_children(element, ("symbol", op), term.to_xml(doc))
        return element


class Expressions(UserList[Expression], AbstractSyntaxTree):
    """Represents a list of expressions."""

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("expressionList")
        for i, expr in enumerate(self):
            element.appendChild(expr.to_xml(doc))
            if i < len(self) - 1:
                _add_child(element, "symbol", ",")
        return element


@dataclass(frozen=True)
class ReturnStatement(AbstractSyntaxTree):
    """Represents a return statement.

    Attributes:
        expression: The expression to return, or None if there is no expression.
    """

    expression: Expression | None

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("returnStatement")
        _add_child(element, "keyword", "return")
        if self.expression is not None:
            element.appendChild(self.expression.to_xml(doc))
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class DoStatement(SubroutineCall):
    """Represents a do statement."""

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("doStatement")
        _add_child(element, "keyword", "do")
        self._write_content(element)
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class LetStatement(AbstractSyntaxTree):
    """Represents a let statement.

    Attributes:
        var_name: The name of the variable.
        index: The index expression, or None if there is no index.
        expression: The expression to assign to the variable.
    """

    var_name: str
    index: Expression | None
    expression: Expression

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("letStatement")
        _add_children(element, ("keyword", "let"), ("identifier", self.var_name))
        if self.index is not None:
            _add_children(element, "[", self.index.to_xml(doc), "]")
        _add_children(element, "=", self.expression.to_xml(doc), ";")
        return element


@dataclass(frozen=True)
class IfStatement(AbstractSyntaxTree):
    """Represents an if statement.

    Attributes:
        condition: The condition of the if statement.
        if_: The statements to execute if the condition is true.
        else_: The statements to execute if the condition is false.
    """

    condition: Expression
    if_: Statements
    else_: Statements | None

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("ifStatement")
        _add_children(
            element,
            ("keyword", "if"),
            "(",
            self.condition.to_xml(doc),
            ")",
            "{",
            self.if_.to_xml(doc),
            "}",
        )
        if self.else_ is not None:
            _add_children(
                element, ("keyword", "else"), "{", self.else_.to_xml(doc), "}"
            )
        return element


@dataclass(frozen=True)
class WhileStatement(AbstractSyntaxTree):
    """Represents a while statement.

    Attributes:
        condition: The condition of the while statement.
        body: The statements to execute while the condition is true.
    """

    condition: Expression
    body: Statements

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("whileStatement")
        _add_children(
            element,
            ("keyword", "while"),
            "(",
            self.condition.to_xml(doc),
            ")",
            "{",
            self.body.to_xml(doc),
            "}",
        )
        return element


Statement: TypeAlias = (
    ReturnStatement | DoStatement | LetStatement | IfStatement | WhileStatement
)


class Statements(UserList[Statement], AbstractSyntaxTree):
    """Represents a list of statements.

    Attributes:
        data: The list of statements.
    """

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("statements")
        for statement in self:
            element.appendChild(statement.to_xml(doc))
        return element


@dataclass(frozen=True)
class VarDeclaration(AbstractSyntaxTree):
    """Represents a variable declaration.

    Attributes:
        type_: The type of the variable.
        names: The names of the variables.
    """

    type_: str
    names: list[str]

    @property
    def is_identifier(self) -> bool:
        """True if type is identifier."""
        return self.type_ not in {"int", "char", "boolean"}

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("varDec")
        tag = "identifier" if self.is_identifier else "keyword"
        _add_children(element, ("keyword", "var"), (tag, self.type_))
        for i, var_name in enumerate(self.names):
            _add_child(element, "identifier", var_name)
            if i < len(self.names) - 1:
                _add_child(element, "symbol", ",")
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class SubroutineBody(AbstractSyntaxTree):
    """Represents the body of a subroutine.

    Attributes:
        var_declarations: The list of variable declarations.
        statements: The statements inside the subroutine.
    """

    var_declarations: list[VarDeclaration]
    statements: Statements

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("subroutineBody")
        _add_children(
            element,
            "{",
            *(x.to_xml(doc) for x in self.var_declarations),
            self.statements.to_xml(doc),
            "}",
        )
        return element


@dataclass(frozen=True)
class SubroutineDeclaration(AbstractSyntaxTree):
    """Represents a subroutine declaration.

    Attributes:
        type_: The type of the subroutine.
        return_type: The return type of the subroutine.
        name: The name of the subroutine.
        parameters: The parameters of the subroutine.
        body: The body of the subroutine.
    """

    type_: str
    return_type: str
    name: str
    parameters: ParameterList
    body: SubroutineBody

    @property
    def is_identifier(self) -> bool:
        """True if return type is identifier."""
        return self.return_type not in {"int", "char", "boolean", "void"}

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("subroutineDec")
        tag = "identifier" if self.is_identifier else "keyword"
        _add_children(
            element,
            ("keyword", self.type_),
            (tag, self.return_type),
            ("identifier", self.name),
            "(",
            self.parameters.to_xml(doc),
            ")",
            self.body.to_xml(doc),
        )
        return element


@dataclass(frozen=True)
class ClassVarDeclaration(AbstractSyntaxTree):
    """Represents a class variable declaration.

    Attributes:
        modifier: The modifier of the variable declaration.
        type_: The type of the variable.
        names: The names of the variables.
    """

    modifier: str
    type_: str
    names: list[str]

    @property
    def is_identifier(self) -> bool:
        """True if type is identifier."""
        return self.type_ not in {"int", "char", "boolean"}

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("classVarDec")
        tag = "identifier" if self.is_identifier else "keyword"
        _add_children(element, ("keyword", self.modifier), (tag, self.type_))
        for i, var_name in enumerate(self.names):
            _add_child(element, "identifier", var_name)
            if i < len(self.names) - 1:
                _add_child(element, "symbol", ",")
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class Class(AbstractSyntaxTree):
    """Represents a class.

    Attributes:
        name: The name of the class.
        class_vars: The class variable declarations.
        subroutines: The subroutine declarations.
    """

    name: str
    class_vars: list[ClassVarDeclaration]
    subroutines: list[SubroutineDeclaration]

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("class")
        _add_children(
            element,
            ("keyword", "class"),
            ("identifier", self.name),
            "{",
            *(x.to_xml(doc) for x in self.class_vars),
            *(x.to_xml(doc) for x in self.subroutines),
            "}",
        )
        return element


Term: TypeAlias = (
    VarTerm | ConstantTerm | UnaryOpTerm | SubroutineCallTerm | ExpressionTerm
)
