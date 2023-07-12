"""Functions for parsing tokens into Jack structures."""
from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping

from hdk.jack import syntax as s
from hdk.jack.tokenizer import Token, TokenType


class TokensIterator(Iterator[Token]):
    """An iterator that could return the next token without moving forward.

    It is useful because in LL(1) syntax grammar you need to look forward one token
    to decide what kind of syntax structure you need to construct.
    """

    def __init__(self, tokens: Iterable[Token]):
        """Initializes the TokensIterator.

        Args:
            tokens: The iterable collection of tokens.
        """
        self._tokens = iter(tokens)
        self._next: Token | None = None

    def peek(self) -> Token:
        """Returns a token without moving the iterator forward.

        Returns:
            The next token.
        """
        if self._next is None:
            self._next = next(self._tokens)
        return self._next

    def __next__(self) -> Token:
        """Returns the next token in the iteration with moving the iterator forward.

        Returns:
            The next token.
        """
        value = self._next or next(self._tokens)
        self._next = None
        return value

    def skip(self, *args: str):
        """Skips tokens asserting that their values equals to strings in args.

        Args:
            *args: String values that should be equal to the skipped tokens.
        """
        for arg in args:
            token = next(self)
            if token.value != arg:
                raise ValueError(f"Expected {arg} token but got {token.value}.")


def parse_var_declaration(tokens: TokensIterator) -> s.VarDeclaration:
    """Parses a variable declaration from the given tokens.

    varDec = 'var' type varName (',' varName) ';'

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed variable declaration.
    """
    type_ = next(tokens).value
    names = [next(tokens).value]
    while next(tokens).value == ",":  # if it's not a "," then it is a ";"
        names.append(next(tokens).value)
    return s.VarDeclaration(type_=type_, names=names)


def parse_class_var_declaration(tokens: TokensIterator) -> s.ClassVarDeclaration:
    """Parses a class variable declaration from the given tokens.

    classVarDec = ('static' | 'field') type varName(',' varName)* ';'

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed class variable declaration.
    """
    modifier, type_ = next(tokens).value, next(tokens).value
    names = [next(tokens).value]
    while next(tokens).value == ",":  # if it's not a "," then it is a ";"
        names.append(next(tokens).value)
    return s.ClassVarDeclaration(modifier=modifier, type_=type_, names=names)


def parse_parameter_list(tokens: TokensIterator) -> s.ParameterList:
    """Parses a parameter list from the given tokens.

    parameterList = ((type varName)(',' type varName)*)?

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed parameter list.
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

    subroutineBody = '{' varDec* statements '}'

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed subroutine body.
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

    subroutineDec = ('constructor'|'function'|'method') ('void'|type) subroutineName

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed subroutine declaration.
    """
    kind, returns, name = next(tokens).value, next(tokens).value, next(tokens).value
    parameters = parse_parameter_list(tokens)
    return s.SubroutineDeclaration(
        kind=kind,
        returns=returns,
        name=name,
        parameters=parameters,
        body=parse_subroutine_body(tokens),
    )


def parse_class(tokens: TokensIterator) -> s.Class:
    """Parses a class from the given tokens.

    class = 'class' className '{' classVarDec* subroutineDec* '}'

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed class.
    """
    tokens.skip("class")
    name, class_vars, subroutines = next(tokens).value, [], []
    tokens.skip("{")
    while tokens.peek().value != "}":
        if tokens.peek().value in {"static", "field"}:
            class_vars.append(parse_class_var_declaration(tokens))
        else:
            subroutines.append(parse_subroutine_declaration(tokens))
    tokens.skip("}")
    return s.Class(name=name, class_vars=class_vars, subroutines=subroutines)


def parse_expressions(tokens: TokensIterator) -> s.Expressions:
    """Parses a list of expressions from the given tokens.

    expression = term (op term)*

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed expressions.
    """
    tokens.skip("(")
    expression_list = s.Expressions([])
    while tokens.peek().value != ")":
        if tokens.peek().value == ",":
            tokens.skip(",")
        expression_list.append(parse_expression(tokens))
    tokens.skip(")")
    return expression_list


def parse_index(tokens: TokensIterator) -> s.Expression | None:
    """Parses an index of variable.

    index = (expression)?

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed index.
    """
    if tokens.peek().value != "[":
        return None
    tokens.skip("[")
    index = parse_expression(tokens)
    tokens.skip("]")
    return index


def parse_let_statement(tokens: TokensIterator) -> s.LetStatement:
    """Parses a let statement from the given tokens.

    letStatement = 'let' varName(index) '=' expression ';'

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed let statement.
    """
    var_name = next(tokens).value
    index = parse_index(tokens)
    tokens.skip("=")
    return s.LetStatement(
        var_name=var_name,
        index=index,
        expression=parse_expression(tokens),
    )


def parse_subroutine_call(cls, tokens: TokensIterator, name=None):
    """Parses a subroutine call from the given tokens.

    subroutineCall = subroutineName '(' expressionList ')' |
                     (className|varname) '.' subroutineName '(' expressionList ')'

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed let statement.
    """
    name, owner = name or next(tokens).value, None
    if tokens.peek().value == ".":
        tokens.skip(".")
        owner, name = name, next(tokens).value
    expressions = parse_expressions(tokens)
    return cls(owner=owner, name=name, arguments=expressions)


def parse_do_statement(tokens: TokensIterator) -> s.DoStatement:
    """Parses a do statement from the given tokens.

    doStatement = 'do' subroutineCall ';'

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed do statement.
    """
    return parse_subroutine_call(s.DoStatement, tokens)


def parse_return_statement(tokens: TokensIterator) -> s.ReturnStatement:
    """Parses a return statement from the given tokens.

    returnStatement = 'return' expression? ';'

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed return statement.
    """
    if tokens.peek().value == ";":
        return s.ReturnStatement(expression=None)
    return s.ReturnStatement(expression=parse_expression(tokens))


def parse_while_statement(tokens: TokensIterator) -> s.WhileStatement:
    """Parses a while statement from the given tokens.

    whileStatement = 'while' '(' expression ')' '{' statements '}'

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed while statement.
    """
    tokens.skip("(")
    test = parse_expression(tokens)
    tokens.skip(")", "{")
    body = parse_statements(tokens)
    tokens.skip("}")
    return s.WhileStatement(test=test, body=body)


def parse_if_statement(tokens: TokensIterator) -> s.IfStatement:
    """Parses an if statement from the given tokens.

    ifStatement = 'if' '('expression')''{'statements'}' ('else' '{'statements '}')?

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed if statement.
    """
    tokens.skip("(")
    test = parse_expression(tokens)
    tokens.skip(")", "{")
    if_ = parse_statements(tokens)
    tokens.skip("}")
    if tokens.peek().value != "else":
        return s.IfStatement(test=test, if_=if_, else_=None)
    tokens.skip("else", "{")
    else_ = parse_statements(tokens)
    tokens.skip("}")
    return s.IfStatement(test=test, if_=if_, else_=else_)


def parse_statements(tokens: TokensIterator) -> s.Statements:
    """Parses a list of statements from the given tokens.

    statements = statement*

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed statements.
    """
    statements = s.Statements([])
    builders: Mapping[str, Callable[[TokensIterator], s.Statement]] = {
        "let": parse_let_statement,
        "do": parse_do_statement,
        "return": parse_return_statement,
        "while": parse_while_statement,
        "if": parse_if_statement,
    }
    while tokens.peek().value != "}":
        if (token_value := next(tokens).value) != ";":
            statements.append(builders[token_value](tokens))
    return statements


def parse_term(tokens: TokensIterator) -> s.Term:
    """Parses a term from the given tokens.

    term = integerConstant|
           stringConstant|
           keywordConstant|
           varName(index)|
           subroutineCall|
           '('expression')'|
           unaryOp term

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed term.
    """
    token, next_token_value = next(tokens), tokens.peek().value
    match token:
        case Token(token_type=TokenType.INTEGER_CONSTANT, value=value):
            return s.ConstantTerm(kind=s.ConstantKind.INTEGER, value=value)
        case Token(token_type=TokenType.STRING_CONSTANT, value=value):
            return s.ConstantTerm(kind=s.ConstantKind.STRING, value=value)
        case Token(token_type=TokenType.KEYWORD, value=value):
            return s.ConstantTerm(kind=s.ConstantKind.KEYWORD, value=value)
        case Token(token_type=TokenType.IDENTIFIER, value=value):
            if next_token_value in {"(", "."}:
                return parse_subroutine_call(s.CallTerm, tokens, token.value)
            return s.VarTerm(var_name=value, index=parse_index(tokens))
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

    expression = term (op term)*

    Args:
        tokens: The iterator of tokens.

    Returns:
        The parsed expression.
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
