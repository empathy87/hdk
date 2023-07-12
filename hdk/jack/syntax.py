"""Defines classes that represent different types of Jack syntax structures."""
from __future__ import annotations

import abc
from collections import UserList
from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar, NamedTuple, TypeAlias
from xml.dom.minidom import Document, Element

from hdk.jack.tokenizer import KEYWORDS


def _add_child(parent: Element, value: str, tag: str = "symbol"):
    """Builds and adds a child to the XML element.

    Args:
        parent: The XML element to add the child element to.
        value: The text value of the child element.
        tag: The tag of the child element.
    """
    doc = parent.ownerDocument
    child = doc.createElement(tag)
    child.appendChild(doc.createTextNode(value))
    parent.appendChild(child)


def _add_children(parent: Element, *children: Any):
    """Appends children to the parent XML Element.

    Args:
        parent: The parent XML element to append children to.
        *children: Any number of children that could be None, a syntax element,
            a string, a tuple of strings or a list.
    """
    for child in children:
        if child is None:
            continue
        match child:
            case AbstractSyntaxTree():
                parent.appendChild(child.to_xml(parent.ownerDocument))
            case str(value):
                _add_child(parent, value=value)
            case (str(tag), str(value)):
                _add_child(parent, value=value, tag=tag)
            case list():
                _add_children(parent, *tuple(child))


class AbstractSyntaxTree(abc.ABC):
    """Represents the abstract syntax tree (a syntax structure of Jack language)."""

    @abc.abstractmethod
    def to_xml(self, doc: Document) -> Element:
        """Builds an XML element that represents the syntax structure.

        Args:
            doc: The XML document.

        Returns:
            The constructed XML element within the document.
        """
        pass


class Parameter(NamedTuple):
    """Represents a parameter of subroutine declaration.

    Attributes:
        type_: The type of the parameter (int, char, boolean or a class name).
        var_name: The variable name defined by the parameter.
    """

    type_: str
    var_name: str

    @property
    def is_identifier(self) -> bool:
        """True if the parameter type is not one of the built-in data types."""
        return self.type_ not in {"int", "char", "boolean"}


class ParameterList(UserList[Parameter], AbstractSyntaxTree):
    """Represents a parameters list of a subroutine declaration."""

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("parameterList")
        for i, param in enumerate(self):
            _add_children(
                element,
                ("identifier" if param.is_identifier else "keyword", param.type_),
                ("identifier", param.var_name),
                "," if i < len(self) - 1 else None,
            )
        return element


class ConstantKind(Enum):
    """Represents constant types."""

    KEYWORD = 0
    INTEGER = 1
    STRING = 2


@dataclass(frozen=True)
class ConstantTerm(AbstractSyntaxTree):
    """Represents a constant term.

    Attributes:
        kind: The kind of the constant term.
        value: The value of the constant term.
    """

    kind: ConstantKind
    value: str
    _KIND_TO_STR: ClassVar[dict[ConstantKind, str]] = {
        ConstantKind.KEYWORD: "keyword",
        ConstantKind.INTEGER: "integerConstant",
        ConstantKind.STRING: "stringConstant",
    }
    _ALLOWED_KEYWORD_VALUES: ClassVar[set[str]] = {"null", "true", "false", "this"}

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("term")
        _add_child(element, self.value, ConstantTerm._KIND_TO_STR[self.kind])
        return element

    def __post_init__(self):
        if (
            self.kind is ConstantKind.KEYWORD
            and self.value not in ConstantTerm._ALLOWED_KEYWORD_VALUES
        ):
            raise ValueError(f"Invalid value {self.value!r} for keyword constant term.")
        if self.kind is ConstantKind.INTEGER and not self.value.isdigit():
            raise ValueError(f"Invalid value {self.value!r} for integer constant term.")


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
        _add_child(element, self.var_name, "identifier")
        if self.index is not None:
            _add_children(element, "[", self.index, "]")
        return element

    def __post_init__(self):
        if not _is_identifier_valid(self.var_name):
            raise ValueError(f"Invalid var name {self.var_name!r} for var term.")


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
            self.arguments,
            ")",
        )

    def __post_init__(self):
        if self.owner is not None and not _is_identifier_valid(self.owner):
            raise ValueError(f"Invalid owner name {self.owner!r} for subroutine call.")
        if not _is_identifier_valid(self.name):
            raise ValueError(f"Invalid name {self.name!r} for subroutine call.")

    @abc.abstractmethod
    def to_xml(self, doc: Document) -> Element:
        pass


@dataclass(frozen=True)
class CallTerm(SubroutineCall):
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
        _add_children(element, "(", self.expression, ")")
        return element


@dataclass(frozen=True)
class UnaryOpTerm(AbstractSyntaxTree):
    """Represents a unary operation term.

    Attributes:
        unaryOp: The unary operator.
        term: The term.
    """

    _ALLOWED_UNARY_OPS: ClassVar[set[str]] = {
        "-",
        "~",
    }

    unaryOp: str
    term: Term

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("term")
        _add_children(element, self.unaryOp, self.term)
        return element

    def __post_init__(self):
        if self.unaryOp not in self._ALLOWED_UNARY_OPS:
            raise ValueError(f"Invalid unary op {self.unaryOp!r} for unary op term.")


@dataclass(frozen=True)
class Expression(AbstractSyntaxTree):
    """Represents an expression.

    Attributes:
        first_term: The first (mandatory) term of the expression.
        term_list: A list of tuples containing operators and terms.
    """

    _ALLOWED_OPS: ClassVar[set[str]] = {"-", "+", "*", "/", "&", "|", ">", "<", "="}

    first_term: Term
    term_list: list[tuple[str, Term]]

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("expression")
        _add_children(element, self.first_term)
        for op, term in self.term_list:
            _add_children(element, ("symbol", op), term)
        return element

    def __post_init__(self):
        for op, _ in self.term_list:
            if op not in self._ALLOWED_OPS:
                raise ValueError(f"Invalid binary op {op!r} for expression.")


class Expressions(UserList[Expression], AbstractSyntaxTree):
    """Represents a list of expressions."""

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("expressionList")
        for i, expr in enumerate(self):
            _add_children(element, expr, "," if i < len(self) - 1 else None)
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
        _add_children(element, ("keyword", "return"), self.expression, ";")
        return element


@dataclass(frozen=True)
class DoStatement(SubroutineCall):
    """Represents a do statement."""

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("doStatement")
        _add_child(element, "do", "keyword")
        self._write_content(element)
        _add_child(element, ";")
        return element


@dataclass(frozen=True)
class LetStatement(AbstractSyntaxTree):
    """Represents a let statement.

    Attributes:
        var_name: The name of the variable (l-value of the let statement).
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
            _add_children(element, "[", self.index, "]")
        _add_children(element, "=", self.expression, ";")
        return element

    def __post_init__(self):
        if not _is_identifier_valid(self.var_name):
            raise ValueError(f"Invalid var_name {self.var_name!r} for let statement.")


@dataclass(frozen=True)
class IfStatement(AbstractSyntaxTree):
    """Represents an if statement.

    Attributes:
        test: The condition of the if statement.
        if_: The statements to execute if the condition is true.
        else_: The statements to execute if the condition is false.
    """

    test: Expression
    if_: Statements
    else_: Statements | None

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("ifStatement")
        _add_children(
            element,
            ("keyword", "if"),
            "(",
            self.test,
            ")",
            "{",
            self.if_,
            "}",
        )
        if self.else_ is not None:
            _add_children(element, ("keyword", "else"), "{", self.else_, "}")
        return element


@dataclass(frozen=True)
class WhileStatement(AbstractSyntaxTree):
    """Represents a while statement.

    Attributes:
        test: The condition of the while statement.
        body: The statements to execute while the condition is true.
    """

    test: Expression
    body: Statements

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("whileStatement")
        _add_children(
            element,
            ("keyword", "while"),
            "(",
            self.test,
            ")",
            "{",
            self.body,
            "}",
        )
        return element


Statement: TypeAlias = (
    ReturnStatement | DoStatement | LetStatement | IfStatement | WhileStatement
)


class Statements(UserList[Statement], AbstractSyntaxTree):
    """Represents a list of statements."""

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("statements")
        _add_children(element, self.data)
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
    _BUILT_IN_TYPES: ClassVar[set[str]] = {"int", "char", "boolean"}

    @property
    def is_identifier(self) -> bool:
        """True if type is identifier."""
        return self.type_ not in self._BUILT_IN_TYPES

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("varDec")
        tag = "identifier" if self.is_identifier else "keyword"
        _add_children(element, ("keyword", "var"), (tag, self.type_))
        for i, name in enumerate(self.names):
            _add_children(element, ("identifier", name))
            if i < len(self.names) - 1:
                _add_child(element, ",")
        _add_child(element, ";")
        return element

    def __post_init__(self):
        if self.is_identifier and not _is_identifier_valid(self.type_):
            raise ValueError(f"Invalid type {self.type_!r} for var declaration.")
        for name in self.names:
            if not _is_identifier_valid(name):
                raise ValueError(f"Invalid name {name!r} for var declaration.")


@dataclass(frozen=True)
class SubroutineBody(AbstractSyntaxTree):
    """Represents the body of a subroutine.

    Attributes:
        variables: The list of variable declarations.
        statements: The statements inside the subroutine.
    """

    variables: list[VarDeclaration]
    statements: Statements

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("subroutineBody")
        _add_children(element, "{", self.variables, self.statements, "}")
        return element


@dataclass(frozen=True)
class SubroutineDeclaration(AbstractSyntaxTree):
    """Represents a subroutine declaration.

    Attributes:
        kind: The type of the subroutine.
        returns: The return type of the subroutine.
        name: The name of the subroutine.
        parameters: The parameters of the subroutine.
        body: The body of the subroutine.
    """

    kind: str
    returns: str
    name: str
    parameters: ParameterList
    body: SubroutineBody

    _BUILT_IN_KINDS: ClassVar[set[str]] = {"constructor", "function", "method"}
    _BUILT_IN_RETURNS: ClassVar[set[str]] = {"int", "char", "boolean", "void"}

    @property
    def is_identifier(self) -> bool:
        """True if return type is identifier."""
        return self.returns not in self._BUILT_IN_RETURNS

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("subroutineDec")
        _add_children(
            element,
            ("keyword", self.kind),
            ("identifier" if self.is_identifier else "keyword", self.returns),
            ("identifier", self.name),
            "(",
            self.parameters,
            ")",
            self.body,
        )
        return element

    def __post_init__(self):
        if self.kind not in self._BUILT_IN_KINDS:
            raise ValueError(f"Invalid type {self.kind!r} for subroutine declaration.")
        if self.returns not in self._BUILT_IN_RETURNS and not _is_identifier_valid(
            self.returns
        ):
            raise ValueError(
                f"Invalid returns {self.returns!r} for subroutine declaration."
            )


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

    _BUILT_IN_MODIFIERS: ClassVar[set[str]] = {"static", "field"}
    _BUILT_IN_TYPES: ClassVar[set[str]] = {"int", "char", "boolean"}

    @property
    def is_identifier(self) -> bool:
        """True if type is identifier."""
        return self.type_ not in self._BUILT_IN_TYPES

    def to_xml(self, doc: Document) -> Element:
        element = doc.createElement("classVarDec")
        tag = "identifier" if self.is_identifier else "keyword"
        _add_children(element, ("keyword", self.modifier), (tag, self.type_))
        for i, name in enumerate(self.names):
            _add_child(element, name, "identifier")
            if i < len(self.names) - 1:
                _add_child(element, ",")
        _add_child(element, ";")
        return element

    def __post_init__(self):
        if self.type_ not in self._BUILT_IN_TYPES and not _is_identifier_valid(
            self.type_
        ):
            raise ValueError(f"Invalid type {self.type_!r} for class var declaration.")
        if self.modifier not in self._BUILT_IN_MODIFIERS:
            raise ValueError(
                f"Invalid modifier {self.modifier!r} for class var declaration."
            )
        for name in self.names:
            if not _is_identifier_valid(name):
                raise ValueError(f"Invalid name {name!r} for class var declaration.")


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
            self.class_vars,
            self.subroutines,
            "}",
        )
        return element

    def __post_init__(self):
        if not _is_identifier_valid(self.name):
            raise ValueError(f"Invalid name {self.name!r} for class.")


def _is_identifier_valid(identifier: str) -> bool:
    """Checks if an identifier is valid.

    An identifier is a sequence of letters, digits, and underscores, not starting
    with a digit. It also should not be in keywords.

    Args:
        identifier: The string representing an identifier.

    Returns:
        True if the identifier is correct, False otherwise.
    """
    if len(identifier) == 0 or identifier[0].isdigit() or identifier in KEYWORDS:
        return False
    return identifier.isalnum()


Term: TypeAlias = VarTerm | ConstantTerm | UnaryOpTerm | CallTerm | ExpressionTerm
