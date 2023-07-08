"""Defines dataclasses that represent different types of Jack structures."""
from __future__ import annotations

import abc
from collections import UserList
from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias
from xml.dom.minidom import Document, Element


def _add_child(element: Element, tag_name: str, value: str):
    """Adds a child element with the given name and value to the XML element.

    Args:
        element: The XML element to add the child element to.
        tag_name: The tag name of the child element.
        value: The text value of the child element.
    """
    dom_tree = element.ownerDocument
    child = dom_tree.createElement(tag_name)
    child.appendChild(dom_tree.createTextNode(value))
    element.appendChild(child)


class AbstractSyntaxTree(abc.ABC):
    @abc.abstractmethod
    def to_xml(self, dom_tree: Document) -> Element:
        pass


@dataclass(frozen=True)
class Parameter:
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

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("parameterList")
        for i, parameter in enumerate(self):
            _add_child(
                element,
                "identifier" if parameter.is_identifier else "keyword",
                parameter.type_,
            )
            _add_child(element, "identifier", parameter.var_name)
            if i < len(self) - 1:
                _add_child(element, "symbol", ",")
        return element


class ConstantType(Enum):
    """Represents a constant types."""

    KEYWORD = 0
    INTEGER = 1
    STRING = 2


@dataclass(frozen=True)
class ConstantTerm(AbstractSyntaxTree):
    """Represents a constant term with a type and value.

    Attributes:
        type_: The type of the constant term.
        value: The value of the constant term.
    """

    type_: ConstantType
    value: str

    def to_xml(self, dom_tree: Document) -> Element:
        type_to_str: dict[ConstantType, str] = {
            ConstantType.KEYWORD: "keyword",
            ConstantType.INTEGER: "integerConstant",
            ConstantType.STRING: "stringConstant",
        }
        element = dom_tree.createElement("term")
        _add_child(element, type_to_str[self.type_], self.value)
        return element


@dataclass(frozen=True)
class VarTerm(AbstractSyntaxTree):
    """Represents a variable term with a variable name and an optional index expression.

    Attributes:
        var_name: The name of the variable.
        index: An optional index expression.
    """

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
class SubroutineCall(AbstractSyntaxTree):
    """Represents a subroutine call abstract class.

    Attributes:
        owner: The owner of the subroutine, or None if there is no owner.
        name: The name of the subroutine.
        arguments: The list of arguments passed to the subroutine.
    """

    owner: str | None
    name: str
    arguments: Expressions

    def _write_content(self, element: Element):
        if self.owner is not None:
            _add_child(element, "identifier", self.owner)
            _add_child(element, "symbol", ".")
        _add_child(element, "identifier", self.name)
        _add_child(element, "symbol", "(")
        element.appendChild(self.arguments.to_xml(element.ownerDocument))
        _add_child(element, "symbol", ")")

    @abc.abstractmethod
    def to_xml(self, dom_tree: Document) -> Element:
        pass


@dataclass(frozen=True)
class SubroutineCallTerm(SubroutineCall):
    """Represents a subroutine call term with a subroutine call."""

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("term")
        self._write_content(element)
        return element


@dataclass(frozen=True)
class ExpressionTerm(AbstractSyntaxTree):
    """Represents an expression term with an expression.

    Attributes:
        expression: The expression.
    """

    expression: Expression

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("term")
        _add_child(element, "symbol", "(")
        element.appendChild(self.expression.to_xml(dom_tree))
        _add_child(element, "symbol", ")")
        return element


@dataclass(frozen=True)
class UnaryOpTerm(AbstractSyntaxTree):
    """Represents a unary operation term with a unary operator and a term.

    Attributes:
        unaryOp: The unary operator.
        term: The term.
    """

    unaryOp: str
    term: Term

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("term")
        _add_child(element, "symbol", self.unaryOp)
        element.appendChild(self.term.to_xml(dom_tree))
        return element


@dataclass(frozen=True)
class Expression(AbstractSyntaxTree):
    """Represents an expression with a first term and a list of additional terms.

    Attributes:
        first_term: The first term of the expression.
        term_list: A list of tuples containing operators and terms.
    """

    first_term: Term
    term_list: list[tuple[str, Term]]

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("expression")
        element.appendChild(self.first_term.to_xml(dom_tree))
        for op, term in self.term_list:
            _add_child(element, "symbol", op)
            element.appendChild(term.to_xml(dom_tree))
        return element


class Expressions(UserList[Expression], AbstractSyntaxTree):
    """Represents a list of expressions."""

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("expressionList")
        for i, expr in enumerate(self):
            element.appendChild(expr.to_xml(dom_tree))
            if i < len(self) - 1:
                _add_child(element, "symbol", ",")
        return element


@dataclass(frozen=True)
class ReturnStatement(AbstractSyntaxTree):
    """Represents a return statement with an optional expression.

    Attributes:
        expression: The expression to return, or None if there is no expression.
    """

    expression: Expression | None

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("returnStatement")
        _add_child(element, "keyword", "return")
        if self.expression is not None:
            element.appendChild(self.expression.to_xml(dom_tree))
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class DoStatement(SubroutineCall):
    """Represents a do statement with a subroutine call."""

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("doStatement")
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
class IfStatement(AbstractSyntaxTree):
    """Represents an if statement in the programming language.

    Attributes:
        condition: The condition of the if statement.
        if_: The statements to execute if the condition is true.
        else_: The statements to execute if the condition is false.
    """

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
class WhileStatement(AbstractSyntaxTree):
    """Represents a while statement in the programming language.

    Attributes:
        condition: The condition of the while statement.
        body: The statements to execute while the condition is true.
    """

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


Statement: TypeAlias = (
    ReturnStatement | DoStatement | LetStatement | IfStatement | WhileStatement
)


class Statements(UserList[Statement], AbstractSyntaxTree):
    """Represents a list of statements.

    Attributes:
        data: The list of statements.
    """

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("statements")
        for statement in self:
            element.appendChild(statement.to_xml(dom_tree))
        return element


@dataclass(frozen=True)
class VarDeclaration(AbstractSyntaxTree):
    """Represents a variable declaration in the programming language.

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

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("varDec")
        _add_child(element, "keyword", "var")
        _add_child(
            element, "identifier" if self.is_identifier else "keyword", self.type_
        )
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

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("subroutineBody")
        _add_child(element, "symbol", "{")
        for var_dec in self.var_declarations:
            element.appendChild(var_dec.to_xml(dom_tree))
        element.appendChild(self.statements.to_xml(dom_tree))
        _add_child(element, "symbol", "}")
        return element


@dataclass(frozen=True)
class SubroutineDeclaration(AbstractSyntaxTree):
    """Represents a subroutine declaration in the programming language.

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

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("subroutineDec")
        _add_child(element, "keyword", self.type_)
        _add_child(
            element, "identifier" if self.is_identifier else "keyword", self.return_type
        )
        _add_child(element, "identifier", self.name)
        _add_child(element, "symbol", "(")
        element.appendChild(self.parameters.to_xml(dom_tree))
        _add_child(element, "symbol", ")")
        element.appendChild(self.body.to_xml(dom_tree))
        return element


@dataclass(frozen=True)
class ClassVarDeclaration(AbstractSyntaxTree):
    """Represents a class variable declaration in the programming language.

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

    def to_xml(self, dom_tree: Document) -> Element:
        element = dom_tree.createElement("classVarDec")
        _add_child(element, "keyword", self.modifier)
        _add_child(
            element, "identifier" if self.is_identifier else "keyword", self.type_
        )
        for i, var_name in enumerate(self.names):
            _add_child(element, "identifier", var_name)
            if i < len(self.names) - 1:
                _add_child(element, "symbol", ",")
        _add_child(element, "symbol", ";")
        return element


@dataclass(frozen=True)
class Class(AbstractSyntaxTree):
    """Represents a class in the programming language.

    Attributes:
        name: The name of the class.
        class_vars: The class variable declarations.
        subroutines: The subroutine declarations.
    """

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


Term: TypeAlias = (
    VarTerm | ConstantTerm | UnaryOpTerm | SubroutineCallTerm | ExpressionTerm
)
