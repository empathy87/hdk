from typing import Iterable, Iterator

from hdk.jack_analyzer.syntax import Expression, Term, SimpleTermType, SubroutineCall, ExpressionList, LetStatement, \
    DoStatement, ReturnStatement, WhileStatement, IfStatement, Statements, Var, ClassVar, ParameterList, SubroutineBody, \
    Subroutine, Class
from hdk.jack_analyzer.tokenizer import Token, tokenize, TokenType


class TokensIterator(Iterator[Token]):
    def __init__(self, tokens: Iterable[Token]):
        self._tokens_iterator = iter(tokens)
        self._look_ahead: Token | None = None

    def peek(self) -> Token:
        if self._look_ahead is None:
            self._look_ahead = next(self._tokens_iterator)
        return self._look_ahead

    def __next__(self) -> Token:
        if self._look_ahead:
            value = self._look_ahead
        else:
            value = next(self._tokens_iterator)
        self._look_ahead = None
        return value


def parse_var(tokens: TokensIterator) -> Var:
    """
    >>> expression_text = 'int i, j;'
    >>> expression_tokens = tokenize(expression_text)
    >>> parse_var(TokensIterator(expression_tokens))
    """
    type_ = next(tokens).value
    var_names_list = [next(tokens).value]
    while tokens.peek().value != ";":
        next(tokens)
        var_names_list.append(next(tokens).value)
    next(tokens)
    return Var(type_=type_, vars_names=var_names_list)


def parse_class_var(tokens: TokensIterator) -> ClassVar:
    """
    >>> expression_text = 'static boolean test, test2;'
    >>> expression_tokens = tokenize(expression_text)
    >>> parse_class_var(TokensIterator(expression_tokens))
    """
    type_ = (next(tokens).value, next(tokens).value)
    var_names_list = [next(tokens).value]
    while tokens.peek().value != ";":
        next(tokens)
        var_names_list.append(next(tokens).value)
    next(tokens)
    return ClassVar(type_=type_, vars_names=var_names_list)


def parse_parameter_list(tokens: TokensIterator) -> ParameterList:
    """
    >>> expression_text = 'int a, int b, boolean c)'
    >>> expression_tokens = tokenize(expression_text)
    >>> parse_parameter_list(TokensIterator(expression_tokens))
    """
    parameter_list = []
    while True:
        if tokens.peek().value == ")":
            break
        if tokens.peek().value == ",":
            next(tokens)
        parameter_list.append((next(tokens).value, next(tokens).value))
    next(tokens)
    return ParameterList(parameters=parameter_list)


def parse_subroutine_body(tokens: TokensIterator) -> SubroutineBody:
    """
    >>> expression_text = 'var SquareGame game; let game = SquareGame.new(); do game.run(); do game.dispose(); return;}'
    >>> expression_tokens = tokenize(expression_text)
    >>> parse_subroutine_body(TokensIterator(expression_tokens))
    """
    var_list = []

    while True:
        if tokens.peek().value == "var":
            next(tokens)
            var_list.append(parse_var(tokens))
        else:
            break
    statements = parse_statements(tokens)
    next(tokens)
    return SubroutineBody(var_dec_list=var_list, statements=statements)


def parse_subroutine(tokens: TokensIterator) -> Subroutine:
    """
    >>> expression_text = 'function void main() { var SquareGame game; let game = SquareGame.new(); do game.run(); do game.dispose(); return; }'
    >>> expression_tokens = tokenize(expression_text)
    >>> parse_subroutine(TokensIterator(expression_tokens))
    """
    type_ = (next(tokens).value, next(tokens).value)
    name = next(tokens).value
    next(tokens)
    parameters = parse_parameter_list(tokens)
    next(tokens)
    subroutine_body = parse_subroutine_body(tokens)
    return Subroutine(type_=type_, name=name, parameters=parameters, body=subroutine_body)


def parse_class(tokens: TokensIterator) -> Class:
    """
    >>> expression_text = "class Main {static boolean test; function void main() { var SquareGame game;let game = SquareGame.new(); do game.run(); do game.dispose(); return;}}"
    >>> expression_tokens = tokenize(expression_text)
    >>> parse_class(TokensIterator(expression_tokens))
    """
    next(tokens)
    class_name = next(tokens).value
    class_vars = []
    subroutines = []
    next(tokens)
    while True:
        if tokens.peek().value in {"static", "field"}:
            class_vars.append(parse_class_var(tokens))
        elif tokens.peek().value == "}":
            break
        else:
            subroutines.append(parse_subroutine(tokens))
    next(tokens)
    return Class(name=class_name, class_vars=class_vars, subroutines=subroutines)


def parse_expression_list(tokens: TokensIterator) -> ExpressionList:
    """
    >>> expression_text = 'a, b/d, c[0])'
    >>> expression_tokens = tokenize(expression_text)
    >>> parse_expression_list(TokensIterator(expression_tokens))
    """
    expression_list = []
    while True:
        if tokens.peek().value == ")":
            break
        if tokens.peek().value == ",":
            next(tokens)
        expression_list.append(parse_expression(tokens))
    return ExpressionList(expression_list=expression_list)


def parse_let_statement(tokens: TokensIterator) -> LetStatement:
    """
    >>> statement_text = 'game = SquareGame.new();'
    >>> statement_tokens = tokenize(statement_text)
    >>> parse_let_statement(TokensIterator(statement_tokens))
    """
    var_name = next(tokens)
    token = next(tokens)
    var_expression = None
    if token.value == "[":
        var_expression = parse_expression(tokens)
        next(tokens)
        next(tokens)
    expression = parse_expression(tokens)
    return LetStatement(var_name=var_name.value, var_expression=var_expression, expression=expression)


def parse_do_statement(tokens: TokensIterator) -> DoStatement:
    """
    >>> statement_text = 'game.run(1);'
    >>> statement_tokens = tokenize(statement_text)
    >>> parse_do_statement(TokensIterator(statement_tokens))
    """
    name = (None, next(tokens).value)
    if next(tokens).value == ".":
        name = (name[1], next(tokens).value)
        next(tokens)
    expression_list = parse_expression_list(tokens)
    next(tokens)
    next(tokens)
    return DoStatement(subroutine_call=SubroutineCall(name=name, expressions=expression_list))


def parse_return_statement(tokens: TokensIterator) -> ReturnStatement:
    """
    >>> statement_text = '2+2;'
    >>> statement_tokens = tokenize(statement_text)
    >>> parse_return_statement(TokensIterator(statement_tokens))
    """
    if tokens.peek().value == ";":
        next(tokens)
        return ReturnStatement(expression=None)
    expression = parse_expression(tokens)
    return ReturnStatement(expression=expression)


def parse_while_statement(tokens: TokensIterator) -> WhileStatement:
    """
    >>> statement_text = '(true) {let j = 10; let i = 15;}'
    >>> statement_tokens = tokenize(statement_text)
    >>> parse_while_statement(TokensIterator(statement_tokens))
    """
    next(tokens)
    expression = parse_expression(tokens)
    next(tokens)
    next(tokens)
    statements = parse_statements(tokens)
    next(tokens)
    return WhileStatement(expression=expression, statements=statements)


def parse_if_statement(tokens: TokensIterator) -> IfStatement:
    """
    >>> statement_text = '(true) {let j = 10; let i = 15;}}'
    >>> statement_tokens = tokenize(statement_text)
    >>> parse_if_statement(TokensIterator(statement_tokens))
    """
    next(tokens)
    expression = parse_expression(tokens)
    next(tokens)
    next(tokens)
    statements_if = parse_statements(tokens)
    next(tokens)
    if tokens.peek().value != "else":
        return IfStatement(expression=expression, statements_if=statements_if, statements_else=None)
    next(tokens)
    next(tokens)
    statements_else = parse_statements(tokens)
    next(tokens)
    return IfStatement(expression=expression, statements_if=statements_if, statements_else=statements_else)


def parse_statements(tokens: TokensIterator) -> Statements:
    statements_list = []
    while tokens.peek().value != "}":
        match tokens.peek().value:
            case "let":
                next(tokens)
                statements_list.append(parse_let_statement(tokens))
            case "do":
                next(tokens)
                statements_list.append(parse_do_statement(tokens))
            case "return":
                next(tokens)
                statements_list.append(parse_return_statement(tokens))
            case "while":
                next(tokens)
                statements_list.append(parse_while_statement(tokens))
            case "if":
                next(tokens)
                statements_list.append(parse_if_statement(tokens))
    return Statements(statements=statements_list)


def parse_expression(tokens: TokensIterator) -> Expression:
    """
    >>> expression_text = 'SquareGame.new();'
    >>> expression_tokens = tokenize(expression_text)
    >>> parse_expression(TokensIterator(expression_tokens))
    """

    def _parse_term() -> Term:
        token = next(tokens)
        next_token = tokens.peek()
        match token:
            case Token(token_type=TokenType.INTEGER_CONSTANT, value=value):
                return Term(unaryOp=None, type_=SimpleTermType.INTEGER_CONSTANT, value=value, expression=None)
            case Token(token_type=TokenType.STRING_CONSTANT, value=value):
                return Term(unaryOp=None, type_=SimpleTermType.STRING_CONSTANT, value=value, expression=None)
            case Token(token_type=TokenType.KEYWORD, value=value):
                return Term(unaryOp=None, type_=SimpleTermType.KEYWORD_CONSTANT, value=value, expression=None)
            case Token(token_type=TokenType.IDENTIFIER, value=value):
                if next_token.token_type == TokenType.SYMBOL and next_token.value == "[":
                    next(tokens)
                    result = Term(unaryOp=None, type_=SimpleTermType.VAR_NAME, value=value, expression=parse_expression(tokens))
                    next(tokens)
                    return result
                elif next_token.token_type == TokenType.SYMBOL and next_token.value == "(":
                    next(tokens)
                    result = Term(unaryOp=None, type_=SubroutineCall((None, token.value), expressions=parse_expression_list(tokens)), value=None, expression=None)
                    next(tokens)
                    return result
                elif next_token.token_type == TokenType.SYMBOL and next_token.value == ".":
                    next(tokens)
                    name = token.value
                    method = next(tokens).value
                    next(tokens)
                    result = Term(unaryOp=None, type_=SubroutineCall((name, method), expressions=parse_expression_list(tokens)), value=None, expression=None)
                    next(tokens)
                    return result
                else:
                    return Term(unaryOp=None, type_=SimpleTermType.VAR_NAME, value=value, expression=None)
            case Token(token_type=TokenType.SYMBOL, value="("):
                result = Term(unaryOp=None, type_=parse_expression(tokens), value=None, expression=None)
                next(tokens)
                return result
            case Token(token_type=TokenType.SYMBOL, value=value):
                return Term(unaryOp=value, type_=_parse_term(), value=None, expression=None)

    first_term = _parse_term()
    term_list = []
    while True:
        next_token = tokens.peek()
        if next_token.token_type == TokenType.SYMBOL and next_token.value in {"]", ")"}:
            return Expression(first_term=first_term, term_list=term_list)
        next_token = next(tokens)
        if next_token.value not in {"+", "-", "*", "/", "&", "|", "<", ">", "="}:
            return Expression(first_term=first_term, term_list=term_list)
        term_list.append((next_token.value, _parse_term()))
