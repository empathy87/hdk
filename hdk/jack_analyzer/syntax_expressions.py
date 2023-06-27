# from syntax_tokens import (
#     Identifier,
#     IntegerConstant,
#     Keyword,
#     StringConstant,
#     Symbol,
#     Token,
# )
#
#
# class Op:
#     value: Symbol
#
#     def print(self, tab_cnt: int = 0) -> str:
#         return self.value.print(tab_cnt)
#
#     def build(self, line: str):
#         token = Token()
#         token.build(line)
#         if isinstance(token.token, Symbol) and token.token.value in "+-*/=<>&|":
#             self.value = token.token
#         else:
#             raise ValueError("Given line is not op.")
#
#     def __init__(self, value: Symbol = Symbol()):
#         self.value = value
#
#
# class UnaryOp:
#     value: Symbol
#
#     def print(self, tab_cnt: int = 0) -> str:
#         return self.value.print(tab_cnt)
#
#     def build(self, line: str):
#         token = Token()
#         token.build(line)
#         if isinstance(token.token, Symbol) and token.token.value in "-~":
#             self.value = token.token
#         else:
#             raise ValueError("Given line is not unary op.")
#
#     def __init__(self, value: Symbol = Symbol()):
#         self.value = value
#
#
# class KeywordConstant:
#     value: Keyword
#
#     def print(self, tab_cnt: int = 0) -> str:
#         return self.value.print(tab_cnt)
#
#     def build(self, line: str):
#         token = Token()
#         token.build(line)
#         if isinstance(token.token, Keyword) and token.token.value in [
#             "true",
#             "false",
#             "null",
#             "this",
#         ]:
#             self.value = token.token
#         raise ValueError("Given line is not keyword constant.")
#
#     def __init__(self, value: Keyword = Keyword()):
#         self.value = value
