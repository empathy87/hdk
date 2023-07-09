"""Functions for parsing tokens into Jack structures."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping

from hdk.jack import syntax as s
from hdk.jack.tokenizer import Token, TokenType


class TokensIterator(Iterator[Token]):
    """Iterator for tokens.

    Args:
        tokens: The iterable collection of tokens.

    Attributes:
        _tokens_iterator: The iterator for the tokens.
        _look_ahead: The next token that is being looked ahead.
    """

    def __init__(self, tokens: Iterable[Token]):
        """Initializes the TokensIterator.

        Args:
            tokens: The iterable collection of tokens.

        """
        self._tokens_iterator = iter(tokens)
        self._look_ahead: Token | None = None

    def peek(self) -> Token:
        """Peeks at the next token.

        Returns:
            Token: The next token.
        """
        if self._look_ahead is None:
            self._look_ahead = next(self._tokens_iterator)
        return self._look_ahead

    def __next__(self) -> Token:
        """Returns the next token in the iteration.

        Returns:
            Token: The next token.
        """
        if self._look_ahead:
            value = self._look_ahead
        else:
            value = next(self._tokens_iterator)
        self._look_ahead = None
        return value

    def skip(self, *args: str):
        for arg in args:
            token = next(self)
            if token.value != arg:
                raise ValueError(f"Expected {arg} token but got {token.value}.")


def parse_var_declaration(tokens: TokensIterator) -> s.VarDeclaration:
    """Parses a variable declaration from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        VarDeclaration: The parsed variable declaration.
    """
    type_ = next(tokens).value
    names = [next(tokens).value]
    while next(tokens).value == ",":  # if it's not a "," then it is a ";"
        names.append(next(tokens).value)
    return s.VarDeclaration(type_=type_, names=names)


def parse_class_var_declaration(tokens: TokensIterator) -> s.ClassVarDeclaration:
    """Parses a class variable declaration from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        ClassVarDeclaration: The parsed class variable declaration.
    """
    modifier, type_ = next(tokens).value, next(tokens).value
    names = [next(tokens).value]
    while next(tokens).value == ",":  # if it's not a "," then it is a ";"
        names.append(next(tokens).value)
    return s.ClassVarDeclaration(modifier=modifier, type_=type_, names=names)


def parse_parameter_list(tokens: TokensIterator) -> s.ParameterList:
    """Parses a parameter list from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        ParameterList: The parsed parameter list.
    """
    parameters = s.ParameterList([])
    tokens.skip("(")
    while (token := next(tokens)).value != ")":
        if token.value == ",":
            token = next(tokens)
        parameters.append(s.Parameter(type_=token.value, var_name=next(tokens).value))
    return parameters


def parse_subroutine_body(tokens: TokensIterator) -> s.SubroutineBody:
    """Parses a subroutine body from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        SubroutineBody: The parsed subroutine body.
    """
    variables = []
    tokens.skip("{")
    while tokens.peek().value == "var":
        tokens.skip("var")
        variables.append(parse_var_declaration(tokens))
    statements = parse_statements(tokens)
    tokens.skip("}")
    return s.SubroutineBody(variables=variables, statements=statements)


def parse_subroutine_declaration(tokens: TokensIterator) -> s.SubroutineDeclaration:
    """Parses a subroutine declaration from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        SubroutineDeclaration: The parsed subroutine declaration.
    """
    type_, returns, name = next(tokens).value, next(tokens).value, next(tokens).value
    parameters = parse_parameter_list(tokens)
    return s.SubroutineDeclaration(
        type_=type_,
        returns=returns,
        name=name,
        parameters=parameters,
        body=parse_subroutine_body(tokens),
    )


def parse_class(tokens: TokensIterator) -> s.Class:
    """Parses a class from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        Class: The parsed class.
    """
    tokens.skip("class")
    class_name, class_vars, subroutines = next(tokens).value, [], []
    tokens.skip("{")
    while tokens.peek().value != "}":
        if tokens.peek().value in {"static", "field"}:
            class_vars.append(parse_class_var_declaration(tokens))
        else:
            subroutines.append(parse_subroutine_declaration(tokens))
    tokens.skip("}")
    return s.Class(name=class_name, class_vars=class_vars, subroutines=subroutines)


def parse_expressions(tokens: TokensIterator) -> s.Expressions:
    """Parses a list of expressions from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        Expressions: The parsed expressions.
    """
    tokens.skip("(")
    expression_list = s.Expressions([])
    while tokens.peek().value != ")":
        if tokens.peek().value == ",":
            tokens.skip(",")
        expression_list.append(parse_expression(tokens))
    tokens.skip(")")
    return expression_list


def parse_let_statement(tokens: TokensIterator) -> s.LetStatement:
    """Parses a let statement from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        LetStatement: The parsed let statement.
    """
    var_name, token, var_expression = next(tokens), next(tokens), None
    if token.value == "[":
        var_expression = parse_expression(tokens)
        tokens.skip("]", "=")
    return s.LetStatement(
        var_name=var_name.value,
        index=var_expression,
        expression=parse_expression(tokens),
    )


def parse_subroutine_call(cls, tokens):
    name, owner = next(tokens).value, None
    if tokens.peek().value == ".":
        tokens.skip(".")
        owner, name = name, next(tokens).value
    expressions = parse_expressions(tokens)
    return cls(owner=owner, name=name, arguments=expressions)


def parse_do_statement(tokens: TokensIterator) -> s.DoStatement:
    """Parses a do statement from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        DoStatement: The parsed do statement.
    """
    return parse_subroutine_call(s.DoStatement, tokens)
    # name, owner = next(tokens).value, None
    # if tokens.peek().value == ".":
    #     tokens.skip(".")
    #     owner, name = name, next(tokens).value
    # expressions = parse_expressions(tokens)
    # return s.DoStatement(owner=owner, name=name, arguments=expressions)


def parse_return_statement(tokens: TokensIterator) -> s.ReturnStatement:
    """Parses a return statement from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        ReturnStatement: The parsed return statement.
    """
    if tokens.peek().value == ";":
        return s.ReturnStatement(expression=None)
    return s.ReturnStatement(expression=parse_expression(tokens))


def parse_while_statement(tokens: TokensIterator) -> s.WhileStatement:
    """Parses a while statement from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        WhileStatement: The parsed while statement.
    """
    tokens.skip("(")
    expression = parse_expression(tokens)
    tokens.skip(")", "{")
    statements = parse_statements(tokens)
    tokens.skip("}")
    return s.WhileStatement(test=expression, body=statements)


def parse_if_statement(tokens: TokensIterator) -> s.IfStatement:
    """Parses an if statement from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        IfStatement: The parsed if statement.
    """
    tokens.skip("(")
    expression = parse_expression(tokens)
    tokens.skip(")", "{")
    statements_if = parse_statements(tokens)
    tokens.skip("}")
    if tokens.peek().value != "else":
        return s.IfStatement(test=expression, if_=statements_if, else_=None)
    tokens.skip("else", "{")
    statements_else = parse_statements(tokens)
    tokens.skip("}")
    return s.IfStatement(test=expression, if_=statements_if, else_=statements_else)


def parse_statements(tokens: TokensIterator) -> s.Statements:
    """Parses a list of statements from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        Statements: The parsed statements.
    """
    statements_list = s.Statements([])
    builders: Mapping[str, Callable[[TokensIterator], s.Statement]] = {
        "let": parse_let_statement,
        "do": parse_do_statement,
        "return": parse_return_statement,
        "while": parse_while_statement,
        "if": parse_if_statement,
    }
    while tokens.peek().value != "}":
        if (token_value := next(tokens).value) != ";":
            statements_list.append(builders[token_value](tokens))
    return statements_list


def parse_term(tokens: TokensIterator) -> s.Term:
    """Parses a term from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        Term: The parsed term.
    """
    token, next_token_value = next(tokens), tokens.peek().value
    match token:
        case Token(token_type=TokenType.INTEGER_CONSTANT, value=value):
            return s.ConstantTerm(type_=s.ConstantType.INTEGER, value=value)
        case Token(token_type=TokenType.STRING_CONSTANT, value=value):
            return s.ConstantTerm(type_=s.ConstantType.STRING, value=value)
        case Token(token_type=TokenType.KEYWORD, value=value):
            return s.ConstantTerm(type_=s.ConstantType.KEYWORD, value=value)
        case Token(token_type=TokenType.IDENTIFIER, value=value):
            if next_token_value == "[":
                tokens.skip("[")
                var_term = s.VarTerm(var_name=value, index=parse_expression(tokens))
                tokens.skip("]")
                return var_term
            elif next_token_value == "(":
                return s.CallTerm(
                    owner=None, name=value, arguments=parse_expressions(tokens)
                )
            elif next_token_value == ".":
                tokens.skip(".")
                owner, name = token.value, next(tokens).value
                return s.CallTerm(
                    owner=owner, name=name, arguments=parse_expressions(tokens)
                )
            return s.VarTerm(var_name=value, index=None)
        case Token(token_type=TokenType.SYMBOL, value="("):
            expression_term = s.ExpressionTerm(expression=parse_expression(tokens))
            tokens.skip(")")
            return expression_term
        case Token(token_type=TokenType.SYMBOL, value=value):
            return s.UnaryOpTerm(unaryOp=value, term=parse_term(tokens))
        case token:
            raise ValueError(f"Incorrect token {token!r}.")


def parse_expression(tokens: TokensIterator) -> s.Expression:
    """Parses an expression from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        Expression: The parsed expression.
    """
    first_term = parse_term(tokens)
    term_list: list[tuple[str, s.Term]] = []
    while True:
        next_token = tokens.peek()
        if next_token.token_type == TokenType.SYMBOL and next_token.value in {"]", ")"}:
            return s.Expression(first_term=first_term, term_list=term_list)
        next_token = next(tokens)
        if next_token.value not in {"+", "-", "*", "/", "&", "|", "<", ">", "="}:
            return s.Expression(first_term=first_term, term_list=term_list)
        term_list.append((next_token.value, parse_term(tokens)))
