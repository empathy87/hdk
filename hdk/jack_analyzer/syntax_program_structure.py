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
# class ClassName:
#     value: Identifier
#
#     def print(self, tab_cnt: int = 0):
#         self.value.print(tab_cnt)
#
#     def build(self, line: str):
#         token = Token()
#         token.build(line)
#         if isinstance(token.token, Identifier):
#             self.value = token.token
#         else:
#             raise ValueError("Given line is not className.")
