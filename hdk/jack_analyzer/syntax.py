"""Defines dataclasses that represent different types of vm commands."""
# import re
# from collections import Counter
# from collections.abc import Iterable, Iterator
# from dataclasses import dataclass
# from io import TextIOWrapper
# from typing import ClassVar, TypeAlias
#
# ALLOWED_TYPES: set[str] = {
#     "keyword",
#     "symbol",
#     "integerConstant",
#     "stringConstant",
#     "identifier",
# }
#
# ALLOWED_KEYWORDS: set[str] = {
#     "class",
#     "method",
#     "function",
#     "constructor",
#     "int",
#     "boolean",
#     "char",
#     "var",
#     "static",
#     "field",
#     "let",
#     "do",
#     "if",
#     "else",
#     "while",
#     "return",
#     "true",
#     "false",
#     "null",
#     "this",
# }
#
# ALLOWED_SYMBOLS: set[str] = {
#     "{",
#     "}",
#     "(",
#     ")",
#     "[",
#     "]",
#     ".",
#     ",",
#     ";",
#     "+",
#     "-",
#     "*",
#     "/",
#     "&",
#     "|",
#     "~",
#     "<",
#     ">",
#     "=",
# }
#
#
# class Token:
#     _type: str
#     value: str
#
#     def print(self, tab_cnt: int = 0) -> str:
#         yield "    " * tab_cnt + f"<{self._type}> {self.value} </{self._type}>\n"
#
#     def build(self, file: TextIOWrapper):
#         s = file.readline().split()
#         self._type = s[0][1:-1]
#         self.value = s[1]
#
#     def __init__(self, tp="None", vl="None"):
#         self.value = vl
#         self._type = tp
#
#
# class Term:
#     value: Token
#
#     def print(self, tab_cnt: int = 0) -> Iterator[str]:
#         yield from [
#             "    " * tab_cnt + "<term>",
#             self.value.print(tab_cnt + 1),
#             "    " * tab_cnt + "</term>",
#         ]
#
#     def build(self, file: TextIOWrapper):
#         tk = Token()
#         tk.build(file)
#         self.value = tk
#
#
# class Expression:
#     term1: Term
#     t = []
#
#     def print(self, tab_cnt: int = 0):
#         yield "    " * tab_cnt + "<expression>"
#         yield from self.term1.print(tab_cnt + 1)
#         for op, term in self.t:
#             yield from op.print(tab_cnt + 1)
#             yield from term.print(tab_cnt + 1)
#         yield "    " * tab_cnt + "</expression>"
#
#     def build(self, file: TextIOWrapper) -> Token:
#         self.term1.build(file)
#         op = Token()
#         while op.value in "+-*/<>|&=":
#             term = Term()
#             term.build(file)
#             self.t.append((op, term))
#             op.build(file)
#         return op
#
#
# class ExpressionList:
#     expression1: Expression
#     _list = []
#
#     def print(self, tab_cnt: int = 0):
#         yield "    " * tab_cnt + "<expressionList>"
#         yield from self.expression1.print(tab_cnt + 1)
#         for z, expression in self._list:
#             yield from z.print(tab_cnt + 1)
#             yield from expression.print(tab_cnt + 1)
#         yield "    " * tab_cnt + "</expressionList>"
#
#     def build(self, file: TextIOWrapper) -> Token:
#         bp = self.expression1.build(file)
#         while bp.value == ",":
#             n_exp = Expression()
#             n_bp = n_exp.build(file)
#             self._list.append((bp, n_exp))
#             bp = n_bp
#         return bp
#
#
# class SubroutineCall:
#     cv_name: Token | None
#     _p: Token | None
#     subroutine_name: Token
#     _bo: Token
#     expression_list: ExpressionList
#     _bc: Token
#
#     def print(self, tab_cnt: int = 0):
#         yield "    " * tab_cnt + "<subroutineCall>"
#         if self.cv_name is not None and self._p is not None:
#             yield from self.cv_name.print(tab_cnt + 1)
#             yield from self._p.print(tab_cnt + 1)
#         yield from self.subroutine_name.print(tab_cnt + 1)
#         yield from self._bo.print(tab_cnt + 1)
#         yield from self.expression_list.print(tab_cnt + 1)
#         yield from self._bc.print(tab_cnt + 1)
#         yield "    " * tab_cnt + "</subroutineCall>"
#
#     def build(self, file: TextIOWrapper):
#         s1 = Token()
#         s2 = Token()
#         s1.build(file)
#         s2.build(file)
#         if s2.value == ".":
#             self.cv_name = s1
#             self._p = s2
#             s1 = Token()
#             s2 = Token()
#             s1.build(file)
#             s2.build(file)
#         else:
#             self.cv_name = None
#             self._p = None
#         self.subroutine_name = s1
#         self._bo = s2
#         self._bc = self.expression_list.build(file)
#
#
# class LetStatement:
#     _let: Token
#     varName: Token
#     op: Token
#     expression: Expression
#     pz: Token
#
#     def print(self, tab_cnt: int = 0):
#         yield "    " * tab_cnt + "<letStatement>"
#         yield from self._let.print(tab_cnt + 1)
#         yield from self.varName.print(tab_cnt + 1)
#         yield from self.op.print(tab_cnt + 1)
#         yield from self.expression.print(tab_cnt + 1)
#         yield "    " * tab_cnt + "</letStatement>"
#
#     def build(self, file: TextIOWrapper):
#         self._let.build(file)
#         self.varName.build(file)
#         self.op
#
#
# class IfStatement:
#     _if: Token
#     _bo: Token
#     expression: Expression
#     _bc: Token
#     statements = []
#
#     def print(self, tab_cnt: int = 0):
#         yield "    " * tab_cnt + "<ifStatement>"
#         yield from self._if.print(tab_cnt + 1)
#         yield from self._bo.print(tab_cnt + 1)
#         yield from self.expression.print(tab_cnt + 1)
#         yield from self._bc.print(tab_cnt + 1)
#         for st in self.statements:
#             yield from st.print(tab_cnt + 1)
#         yield "    " * tab_cnt + "</ifStatement>"
#
#
# class WhileStatement:
#     _while: Token
#     _bo: Token
#     expression: Expression
#     _bc: Token
#     statements = []
#
#     def print(self, tab_cnt: int = 0):
#         yield "    " * tab_cnt + "<whileStatement>"
#         yield from self._while.print(tab_cnt + 1)
#         yield from self._bo.print(tab_cnt + 1)
#         yield from self.expression.print(tab_cnt + 1)
#         yield from self._bc.print(tab_cnt + 1)
#         for st in self.statements:
#             yield from st.print(tab_cnt + 1)
#         yield "    " * tab_cnt + "</whileStatement>"
#
#
# class ReturnStatement:
#     _return: Token
#     expression: Expression | None
#
#     def print(self, tab_cnt: int = 0):
#         yield "    " * tab_cnt + "<returnStatement>"
#         yield from self._return.print(tab_cnt + 1)
#         if self.expression is not None:
#             yield from self.expression.print(tab_cnt + 1)
#         yield "    " * tab_cnt + "</returnStatement>"
#
#
# class DoStatement:
#     _do: Token
#     subroutine_call: SubroutineCall
#
#     def print(self, tab_cnt: int = 0):
#         yield "    " * tab_cnt + "<doStatement>"
#         yield from self._do.print(tab_cnt + 1)
#         yield from self.subroutine_call.print(tab_cnt + 1)
#         yield "    " * tab_cnt + "</doStatement>"
#
#
# Statement: TypeAlias = (
#     LetStatement | IfStatement | WhileStatement | ReturnStatement | DoStatement
# )
#
#
# class Statements:
#     _list = []
#
#     def print(self, tab_cnt: int = 0):
#         yield "    " * tab_cnt + "<statements>"
#         for statement in self._list:
#             yield from statement.print(tab_cnt + 1)
#         yield "    " * tab_cnt + "</statements>"
#
#
# class VarDec:
#     _var: Token
#     _type: Token
#     varName: Token
#     _list = []
#
#     def print(self, tab_cnt: int = 0):
#         yield "    " * tab_cnt + "<varDec>"
#         yield from self._var.print(tab_cnt + 1)
#         yield from self._type.print(tab_cnt + 1)
#         yield from self.varName.print(tab_cnt + 1)
#         for z, vName in self._list:
#             yield from z.print(tab_cnt + 1)
#             yield from vName.print(tab_cnt + 1)
#         yield "    " * tab_cnt + "/<varDec>"
#
#
# class SubroutineBody:
#     _bo: Token
#     varDec_list = []
#     _bc: Token
#     statements: Statements
#
#     def print(self, tab_cnt: int = 0):
#         yield "    " * tab_cnt + "<subroutineBody>"
#         yield from self._bo.print(tab_cnt + 1)
#         for var_dec in self.varDec_list:
#             var_dec.print(tab_cnt + 1)
#         yield from self._bc.print(tab_cnt + 1)
#         yield from self.statements.print(tab_cnt + 1)
#         yield "    " * tab_cnt + "</subroutineBody>"
#
#
# class ParameterList:
#     _type: Token
#     varName: Token
#     _list = []
#
#     def print(self, tab_cnt: int = 0):
#         yield "    " * tab_cnt + "<parameterList>"
#         yield from self._type.print(tab_cnt + 1)
#         yield from self.varName.print(tab_cnt + 1)
#         for z, vName in self._list:
#             yield from z.print(tab_cnt + 1)
#             yield from vName.print(tab_cnt + 1)
#         yield "    " * tab_cnt + "</parameterList>"
#
#
# class SubroutineDec:
#     _cmf: Token
#     _tp: Token
#     subroutine_Name: Token
#
#     def print(self, tab_cnt: int = 0):
#         yield "    " * tab_cnt + "<subroutineDec>"
#         yield from self._cmf.print(tab_cnt + 1)
#         yield from self._tp.print(tab_cnt + 1)
#         yield from self.subroutine_Name.print(tab_cnt + 1)
#         yield "    " * tab_cnt + "</subroutineDec>"
#
#
# class ClassVarDec:
#     _sf: Token
#     _var: Token
#     _type: Token
#     varName: Token
#     _list = []
#
#     def print(self, tab_cnt: int = 0):
#         yield "    " * tab_cnt + "<classVarDec>"
#         yield from self._sf.print(tab_cnt + 1)
#         yield from self._var.print(tab_cnt + 1)
#         yield from self._type.print(tab_cnt + 1)
#         yield from self.varName.print(tab_cnt + 1)
#         for z, vName in self._list:
#             yield from z.print(tab_cnt + 1)
#             yield from vName.print(tab_cnt + 1)
#         yield "    " * tab_cnt + "/<classVarDec>"
#
#
# class Class:
#     _class: Token
#     class_name: Token
#     _bo: Token
#     classVarDec_list = []
#     subroutineDec_list = []
#     _bc: Token
#
#     def print(self, tab_cnt: int = 0):
#         yield "    " * tab_cnt + "<class>"
#         yield from self._class.print(tab_cnt + 1)
#         yield from self.class_name.print(tab_cnt + 1)
#         yield from self._bo.print(tab_cnt + 1)
#         for cvd in self.classVarDec_list:
#             cvd.print(tab_cnt + 1)
#         for sd in self.classVarDec_list:
#             sd.print(tab_cnt + 1)
#         yield from self._bc.print(tab_cnt + 1)
#         yield "    " * tab_cnt + "/<class>"
#
#
# def _is_symbol_valid(symbol: str) -> bool:
#     """Checks if a symbol is valid.
#
#     A symbol can be any sequence of letters, digits, underscores (_), dot (.),
#     dollar sign ($), and colon (:) that does not begin with a digit.
#
#     Args:
#         symbol: A string representing the symbol.
#
#     Returns:
#         True if the symbol is correct, False otherwise.
#
#     Typical usage example:
#         >>> _is_symbol_valid('_R0$:56.')
#         True
#         >>> _is_symbol_valid('5A')
#         False
#         >>> _is_symbol_valid('A97^')
#         False
#     """
#     if len(symbol) == 0 or symbol[0].isdigit():
#         return False
#     return re.fullmatch(r"[_$\\.:]+", symbol) is not None
