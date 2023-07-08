"""Functions for parsing tokens into Jack structures."""
from typing import Iterable, Iterator

from hdk.jack_analyzer.syntax import Expression, UnaryOpTerm, ConstantType, SubroutineCall, Expressions, \
    LetStatement, \
    DoStatement, ReturnStatement, WhileStatement, IfStatement, Statements, VarDeclaration, ClassVarDeclaration, ParameterList, SubroutineBody, \
    SubroutineDeclaration, Class, ConstantTerm, SubroutineCallTerm, ExpressionTerm, Parameter, VarTerm, Term
from hdk.jack_analyzer.tokenizer import Token, TokenType


class TokensIterator(Iterator[Token]):
    """Iterator for tokens.

    This iterator provides methods for peeking at the next token and iterating through tokens.

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

        If the next token is not already looked ahead, it fetches the next token from the iterator.

        Returns:
            Token: The next token.
        """
        if self._look_ahead is None:
            self._look_ahead = next(self._tokens_iterator)
        return self._look_ahead

    def __next__(self) -> Token:
        """Returns the next token in the iteration.

        If the next token has been looked ahead, it returns the looked ahead token.
        Otherwise, it fetches the next token from the iterator.

        Returns:
            Token: The next token.
        """
        if self._look_ahead:
            value = self._look_ahead
        else:
            value = next(self._tokens_iterator)
        self._look_ahead = None
        return value


def parse_var(tokens: TokensIterator) -> VarDeclaration:
    """Parses a variable declaration from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        VarDeclaration: The parsed variable declaration.
    """
    type_ = next(tokens).value
    names = [next(tokens).value]
    while next(tokens).value != ";":
        names.append(next(tokens).value)
    return VarDeclaration(type_=type_, names=names)


def parse_class_var(tokens: TokensIterator) -> ClassVarDeclaration:
    """Parses a class variable declaration from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        ClassVarDeclaration: The parsed class variable declaration.
    """
    modifier, type_ = next(tokens).value, next(tokens).value
    names = [next(tokens).value]
    while next(tokens).value != ";":
        names.append(next(tokens).value)
    return ClassVarDeclaration(modifier=modifier, type_=type_, names=names)


def parse_parameter_list(tokens: TokensIterator) -> ParameterList:
    """Parses a parameter list from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        ParameterList: The parsed parameter list.
    """
    parameters = ParameterList([])
    while (token := next(tokens)).value != ")":
        if token.value == ",":
            token = next(tokens)
        parameters.append(Parameter(type_=token.value, var_name=next(tokens).value))
    return parameters


def parse_subroutine_body(tokens: TokensIterator) -> SubroutineBody:
    """Parses a subroutine body from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        SubroutineBody: The parsed subroutine body.
    """
    var_list = []
    while tokens.peek().value == "var":
        next(tokens)
        var_list.append(parse_var(tokens))
    statements = parse_statements(tokens)
    next(tokens)
    return SubroutineBody(var_declarations=var_list, statements=statements)


def parse_subroutine(tokens: TokensIterator) -> SubroutineDeclaration:
    """Parses a subroutine declaration from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        SubroutineDeclaration: The parsed subroutine declaration.
    """
    type_, return_type = next(tokens).value, next(tokens).value
    name = next(tokens).value
    next(tokens)
    parameters = parse_parameter_list(tokens)
    next(tokens)
    return SubroutineDeclaration(
        type_=type_,
        return_type=return_type,
        name=name,
        parameters=parameters,
        body=parse_subroutine_body(tokens)
    )


def parse_class(tokens: TokensIterator) -> Class:
    """Parses a class from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        Class: The parsed class.
    """
    next(tokens)
    class_name, class_vars, subroutines = next(tokens).value, [], []
    next(tokens)
    while tokens.peek().value != "}":
        if tokens.peek().value in {"static", "field"}:
            class_vars.append(parse_class_var(tokens))
        else:
            subroutines.append(parse_subroutine(tokens))
    next(tokens)
    return Class(name=class_name, class_vars=class_vars, subroutines=subroutines)


def parse_expressions(tokens: TokensIterator) -> Expressions:
    """Parses a list of expressions from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        Expressions: The parsed expressions.
    """
    expression_list = Expressions([])
    while tokens.peek().value != ")":
        if tokens.peek().value == ",":
            next(tokens)
        expression_list.append(parse_expression(tokens))
    return expression_list


def parse_let_statement(tokens: TokensIterator) -> LetStatement:
    """Parses a let statement from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        LetStatement: The parsed let statement.
    """
    var_name, token, var_expression = next(tokens), next(tokens), None
    if token.value == "[":
        var_expression = parse_expression(tokens)
        next(tokens), next(tokens)
    return LetStatement(var_name=var_name.value, index=var_expression, expression=parse_expression(tokens))


def parse_do_statement(tokens: TokensIterator) -> DoStatement:
    """Parses a do statement from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        DoStatement: The parsed do statement.
    """
    name, owner = next(tokens).value, None
    if next(tokens).value == ".":
        owner, name = name, next(tokens).value
        next(tokens)
    expressions = parse_expressions(tokens)
    next(tokens), next(tokens)
    return DoStatement(call=SubroutineCall(owner=owner, name=name, arguments=expressions))


def parse_return_statement(tokens: TokensIterator) -> ReturnStatement:
    """Parses a return statement from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        ReturnStatement: The parsed return statement.
    """
    if tokens.peek().value == ";":
        next(tokens)
        return ReturnStatement(expression=None)
    return ReturnStatement(expression=parse_expression(tokens))


def parse_while_statement(tokens: TokensIterator) -> WhileStatement:
    """Parses a while statement from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        WhileStatement: The parsed while statement.
    """
    next(tokens)
    expression = parse_expression(tokens)
    next(tokens), next(tokens)
    statements = parse_statements(tokens)
    next(tokens)
    return WhileStatement(condition=expression, body=statements)


def parse_if_statement(tokens: TokensIterator) -> IfStatement:
    """Parses an if statement from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        IfStatement: The parsed if statement.
    """
    next(tokens)
    expression = parse_expression(tokens)
    next(tokens), next(tokens)
    statements_if = parse_statements(tokens)
    next(tokens)
    if tokens.peek().value != "else":
        return IfStatement(condition=expression, if_=statements_if, else_=None)
    next(tokens), next(tokens)
    statements_else = parse_statements(tokens)
    next(tokens)
    return IfStatement(condition=expression, if_=statements_if, else_=statements_else)


def parse_statements(tokens: TokensIterator) -> Statements:
    """Parses a list of statements from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        Statements: The parsed statements.
    """
    statements_list = Statements([])
    while tokens.peek().value != "}":
        match next(tokens).value:
            case "let":
                statements_list.append(parse_let_statement(tokens))
            case "do":
                statements_list.append(parse_do_statement(tokens))
            case "return":
                statements_list.append(parse_return_statement(tokens))
            case "while":
                statements_list.append(parse_while_statement(tokens))
            case "if":
                statements_list.append(parse_if_statement(tokens))
    return statements_list


def parse_term(tokens: TokensIterator) -> Term:
    """Parses a term from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        Term: The parsed term.
    """
    token, next_term_token = next(tokens), tokens.peek()
    match token:
        case Token(token_type=TokenType.INTEGER_CONSTANT, value=value):
            return ConstantTerm(type_=ConstantType.INTEGER, value=value)
        case Token(token_type=TokenType.STRING_CONSTANT, value=value):
            return ConstantTerm(type_=ConstantType.STRING, value=value)
        case Token(token_type=TokenType.KEYWORD, value=value):
            return ConstantTerm(type_=ConstantType.KEYWORD, value=value)
        case Token(token_type=TokenType.IDENTIFIER, value=value):
            if next_term_token.value == "[":
                next(tokens)
                result = VarTerm(var_name=value, index=parse_expression(tokens))
                next(tokens)
                return result
            elif next_term_token.value == "(":
                next(tokens)
                result = SubroutineCallTerm(
                    call=SubroutineCall(owner=None, name=value, arguments=parse_expressions(tokens))
                )
                next(tokens)
                return result
            elif next_term_token.value == ".":
                next(tokens)
                owner, name = token.value, next(tokens).value
                next(tokens)
                result = SubroutineCallTerm(
                    call=SubroutineCall(owner=owner, name=name, arguments=parse_expressions(tokens))
                )
                next(tokens)
                return result
            return VarTerm(var_name=value, index=None)
        case Token(token_type=TokenType.SYMBOL, value="("):
            result = ExpressionTerm(expression=parse_expression(tokens))
            next(tokens)
            return result
        case Token(token_type=TokenType.SYMBOL, value=value):
            return UnaryOpTerm(unaryOp=value, term=parse_term(tokens))


def parse_expression(tokens: TokensIterator) -> Expression:
    """Parses an expression from the given tokens.

    Args:
        tokens: The iterator of tokens.

    Returns:
        Expression: The parsed expression.
    """
    first_term = parse_term(tokens)
    term_list = []
    while True:
        next_token = tokens.peek()
        if next_token.token_type == TokenType.SYMBOL and next_token.value in {"]", ")"}:
            return Expression(first_term=first_term, term_list=term_list)
        next_token = next(tokens)
        if next_token.value not in {"+", "-", "*", "/", "&", "|", "<", ">", "="}:
            return Expression(first_term=first_term, term_list=term_list)
        term_list.append((next_token.value, parse_term(tokens)))
