from typing import Iterable, Iterator

from hdk.jack_analyzer.syntax import Expression, UnaryOpTerm, ConstantType, SubroutineCall, Expressions, \
    LetStatement, \
    DoStatement, ReturnStatement, WhileStatement, IfStatement, Statements, VarDeclaration, ClassVarDeclaration, ParameterList, SubroutineBody, \
    SubroutineDeclaration, Class, ConstantTerm, SubroutineCallTerm, ExpressionTerm, Parameter, VarTerm, Term
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


def parse_var(tokens: TokensIterator) -> VarDeclaration:
    type_ = next(tokens).value
    names = [next(tokens).value]
    while next(tokens).value != ";":
        names.append(next(tokens).value)
    return VarDeclaration(type_=type_, names=names)


def parse_class_var(tokens: TokensIterator) -> ClassVarDeclaration:
    modifier, type_ = next(tokens).value, next(tokens).value
    names = [next(tokens).value]
    while next(tokens).value != ";":
        names.append(next(tokens).value)
    return ClassVarDeclaration(modifier=modifier, type_=type_, names=names)


def parse_parameter_list(tokens: TokensIterator) -> ParameterList:
    parameters = ParameterList([])
    while (token := next(tokens)).value != ")":
        if token.value == ",":
            token = next(tokens)
        type_, var_name = token.value, next(tokens).value
        parameters.append(Parameter(type_=type_, var_name=var_name))
    return parameters


def parse_subroutine_body(tokens: TokensIterator) -> SubroutineBody:
    var_list = []
    while tokens.peek().value == "var":
        next(tokens)
        var_list.append(parse_var(tokens))
    statements = parse_statements(tokens)
    next(tokens)
    return SubroutineBody(var_declarations=var_list, statements=statements)


def parse_subroutine(tokens: TokensIterator) -> SubroutineDeclaration:
    type_, return_type = next(tokens).value, next(tokens).value
    name = next(tokens).value
    next(tokens)
    parameters = parse_parameter_list(tokens)
    next(tokens)
    subroutine_body = parse_subroutine_body(tokens)
    return SubroutineDeclaration(
        type_=type_,
        return_type=return_type,
        name=name,
        parameters=parameters,
        body=subroutine_body
    )


def parse_class(tokens: TokensIterator) -> Class:
    next(tokens)
    class_name = next(tokens).value
    class_vars = []
    subroutines = []
    next(tokens)
    while tokens.peek().value != "}":
        if tokens.peek().value in {"static", "field"}:
            class_vars.append(parse_class_var(tokens))
        else:
            subroutines.append(parse_subroutine(tokens))
    next(tokens)
    return Class(name=class_name, class_vars=class_vars, subroutines=subroutines)


def parse_expressions(tokens: TokensIterator) -> Expressions:
    expression_list = Expressions([])
    while tokens.peek().value != ")":
        if tokens.peek().value == ",":
            next(tokens)
        expression_list.append(parse_expression(tokens))
    return expression_list


def parse_let_statement(tokens: TokensIterator) -> LetStatement:
    var_name = next(tokens)
    token = next(tokens)
    var_expression = None
    if token.value == "[":
        var_expression = parse_expression(tokens)
        next(tokens)
        next(tokens)
    expression = parse_expression(tokens)
    return LetStatement(var_name=var_name.value, index=var_expression, expression=expression)


def parse_do_statement(tokens: TokensIterator) -> DoStatement:
    name = next(tokens).value
    owner = None
    if next(tokens).value == ".":
        owner, name = name, next(tokens).value
        next(tokens)
    expressions = parse_expressions(tokens)
    next(tokens)
    next(tokens)
    return DoStatement(call=SubroutineCall(owner=owner, name=name, arguments=expressions))


def parse_return_statement(tokens: TokensIterator) -> ReturnStatement:
    if tokens.peek().value == ";":
        next(tokens)
        return ReturnStatement(expression=None)
    expression = parse_expression(tokens)
    return ReturnStatement(expression=expression)


def parse_while_statement(tokens: TokensIterator) -> WhileStatement:
    next(tokens)
    expression = parse_expression(tokens)
    next(tokens)
    next(tokens)
    statements = parse_statements(tokens)
    next(tokens)
    return WhileStatement(condition=expression, body=statements)


def parse_if_statement(tokens: TokensIterator) -> IfStatement:
    next(tokens)
    expression = parse_expression(tokens)
    next(tokens)
    next(tokens)
    statements_if = parse_statements(tokens)
    next(tokens)
    if tokens.peek().value != "else":
        return IfStatement(condition=expression, if_=statements_if, else_=None)
    next(tokens)
    next(tokens)
    statements_else = parse_statements(tokens)
    next(tokens)
    return IfStatement(condition=expression, if_=statements_if, else_=statements_else)


def parse_statements(tokens: TokensIterator) -> Statements:
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
    token = next(tokens)
    next_term_token = tokens.peek()
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
                owner = token.value
                name = next(tokens).value
                next(tokens)
                result = SubroutineCallTerm(
                    call=SubroutineCall(owner=owner, name=name, arguments=parse_expressions(tokens))
                )
                next(tokens)
                return result
            else:
                return VarTerm(var_name=value, index=None)
        case Token(token_type=TokenType.SYMBOL, value="("):
            result = ExpressionTerm(expression=parse_expression(tokens))
            next(tokens)
            return result
        case Token(token_type=TokenType.SYMBOL, value=value):
            return UnaryOpTerm(unaryOp=value, term=parse_term(tokens))


def parse_expression(tokens: TokensIterator) -> Expression:
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
