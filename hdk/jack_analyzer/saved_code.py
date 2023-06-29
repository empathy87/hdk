# import xml.dom.minidom
# from xml.dom.minidom import Document, Element
#
#
# def parse_class_var_dec(dom_tree: Document, tokens: list[Element]) -> Element:
#     a = dom_tree.createElement("classVarDec")
#     for token in tokens:
#         a.appendChild(token)
#     return a
#
#
# def parse_parameter_list(dom_tree: Document, tokens: list[Element]) -> Element:
#     a = dom_tree.createElement("parameterList")
#     for token in tokens:
#         a.appendChild(token)
#     return a
#
#
# def parse_var_dec(dom_tree: Document, tokens: list[Element]) -> Element:
#     a = dom_tree.createElement("varDec")
#     for token in tokens:
#         a.appendChild(token)
#     return a
#
#
# def parse_term(dom_tree: Document, tokens: list[Element]) -> Element:
#     a = dom_tree.createElement("term")
#     a.appendChild(tokens[0])
#     return a
#
#
# def parse_expression(dom_tree: Document, tokens: list[Element]) -> Element:
#     a = dom_tree.createElement("expression")
#     a.appendChild(parse_term(dom_tree, tokens))
#     return a
#
#
# def parse_expression_list(dom_tree: Document, tokens: list[Element]) -> Element:
#     a = dom_tree.createElement("expressionList")
#     return a
#
#
# def parse_return_statement(dom_tree: Document, tokens: list[Element]) -> Element:
#     a = dom_tree.createElement("returnStatement")
#     a.appendChild(tokens[0])
#     if len(tokens) > 2:
#         a.appendChild(parse_expression(dom_tree, tokens[1:-1]))
#     a.appendChild(tokens[-1])
#     return a
#
#
# def parse_do_statement(dom_tree: Document, tokens: list[Element]) -> Element:
#     a = dom_tree.createElement("doStatement")
#     a.appendChild(tokens[0])
#     cur_tok_value = tokens[2].firstChild.nodeValue.replace(" ", "").replace("\t", "")
#     i = 1
#     if cur_tok_value == ".":
#         a.appendChild(tokens[1])
#         a.appendChild(tokens[2])
#         i = 3
#     a.appendChild(tokens[i])
#     a.appendChild(tokens[i + 1])
#     a.appendChild(parse_expression_list(dom_tree, tokens[i + 2 : -2]))
#     a.appendChild(tokens[-2])
#     a.appendChild(tokens[-1])
#     return a
#
#
# def parse_let_statement(dom_tree: Document, tokens: list[Element]) -> Element:
#     a = dom_tree.createElement("letStatement")
#     a.appendChild(tokens[0])
#     a.appendChild(tokens[1])
#     n = tokens[2].firstChild.nodeValue.replace(" ", "").replace("\t", "")
#     i = 2
#     if n == "[":
#         a.appendChild(tokens[2])
#         exp = []
#         cur_tok = tokens[i]
#         cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace("\t", "")
#         while cur_tok_value != "]":
#             exp.append(cur_tok)
#             i += 1
#             cur_tok = tokens[i]
#             cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace(
#                 "\t", ""
#             )
#         a.appendChild(parse_expression(dom_tree, exp))
#         a.appendChild(tokens[i])
#         i += 1
#     a.appendChild(tokens[i])
#     i += 1
#     exp = []
#     cur_tok = tokens[i]
#     cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace("\t", "")
#     while cur_tok_value != ";":
#         exp.append(cur_tok)
#         i += 1
#         cur_tok = tokens[i]
#         cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace("\t", "")
#     a.appendChild(parse_expression(dom_tree, exp))
#     a.appendChild(tokens[i])
#     return a
#
#
# def parse_while_statement(dom_tree: Document, tokens: list[Element]) -> Element:
#     a = dom_tree.createElement("whileStatement")
#     a.appendChild(tokens[0])
#     a.appendChild(tokens[1])
#     i = 2
#     exp = []
#     cur_tok = tokens[i]
#     cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace("\t", "")
#     while cur_tok_value != ")":
#         exp.append(cur_tok)
#         i += 1
#         cur_tok = tokens[i]
#         cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace("\t", "")
#     a.appendChild(parse_expression(dom_tree, exp))
#     a.appendChild(tokens[i])
#     i += 1
#     a.appendChild(tokens[i])
#     a.appendChild(parse_statements(dom_tree, tokens[i + 1 : -1]))
#     a.appendChild(tokens[-1])
#     return a
#
#
# def parse_if_statement(dom_tree: Document, tokens: list[Element]) -> Element:
#     a = dom_tree.createElement("ifStatement")
#     a.appendChild(tokens[0])
#     a.appendChild(tokens[1])
#     i = 2
#     exp = []
#     cur_tok = tokens[i]
#     cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace("\t", "")
#     while cur_tok_value != ")":
#         exp.append(cur_tok)
#         i += 1
#         cur_tok = tokens[i]
#         cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace("\t", "")
#     a.appendChild(parse_expression(dom_tree, exp))
#     a.appendChild(tokens[i])
#     i += 1
#     a.appendChild(tokens[i])
#     i += 1
#     stm = []
#     cur_tok = tokens[i]
#     cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace("\t", "")
#     while cur_tok_value != "}":
#         stm.append(cur_tok)
#         i += 1
#         cur_tok = tokens[i]
#         cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace("\t", "")
#     a.appendChild(parse_statements(dom_tree, stm))
#     a.appendChild(tokens[i])
#     i += 1
#     if i < len(tokens):
#         a.appendChild(tokens[i])
#         a.appendChild(tokens[i + 1])
#         a.appendChild(parse_statements(dom_tree, tokens[i + 2 : -1]))
#         a.appendChild(tokens[-1])
#     return a
#
#
# def parse_statements(dom_tree: Document, tokens: list[Element]) -> Element:
#     a = dom_tree.createElement("statements")
#     i = -1
#     while i < len(tokens) - 1:
#         i += 1
#         cur_tok = tokens[i]
#         cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace("\t", "")
#         if cur_tok_value == "let":
#             cur_let = []
#             while cur_tok_value != ";":
#                 cur_let.append(cur_tok)
#                 i += 1
#                 cur_tok = tokens[i]
#                 cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace(
#                     "\t", ""
#                 )
#             cur_let.append(cur_tok)
#             a.appendChild(parse_let_statement(dom_tree, cur_let))
#         if cur_tok_value == "do":
#             cur_let = []
#             while cur_tok_value != ";":
#                 cur_let.append(cur_tok)
#                 i += 1
#                 cur_tok = tokens[i]
#                 cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace(
#                     "\t", ""
#                 )
#             cur_let.append(cur_tok)
#             a.appendChild(parse_do_statement(dom_tree, cur_let))
#         if cur_tok_value == "return":
#             cur_let = []
#             while cur_tok_value != ";":
#                 cur_let.append(cur_tok)
#                 i += 1
#                 cur_tok = tokens[i]
#                 cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace(
#                     "\t", ""
#                 )
#             cur_let.append(cur_tok)
#             a.appendChild(parse_return_statement(dom_tree, cur_let))
#         if cur_tok_value == "while":
#             cur_let = []
#             while cur_tok_value != "}":
#                 cur_let.append(cur_tok)
#                 i += 1
#                 cur_tok = tokens[i]
#                 cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace(
#                     "\t", ""
#                 )
#             cur_let.append(cur_tok)
#             a.appendChild(parse_while_statement(dom_tree, cur_let))
#         if cur_tok_value == "if":
#             cur_let = []
#             while cur_tok_value != "}" or (
#                 i < len(tokens) - 1
#                 and tokens[i + 1]
#                 .firstChild.nodeValue.replace(" ", "")
#                 .replace("\t", "")
#                 == "else"
#             ):
#                 cur_let.append(cur_tok)
#                 i += 1
#                 cur_tok = tokens[i]
#                 cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace(
#                     "\t", ""
#                 )
#             cur_let.append(cur_tok)
#             a.appendChild(parse_if_statement(dom_tree, cur_let))
#     return a
#
#
# def parse_subroutine_body(dom_tree: Document, tokens: list[Element]) -> Element:
#     a = dom_tree.createElement("subroutineBody")
#     a.appendChild(tokens[0])
#     i = 0
#     while i < len(tokens) - 2:
#         i += 1
#         cur_tok = tokens[i]
#         cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace("\t", "")
#         if cur_tok_value == "var":
#             cur_var_dec = []
#             while cur_tok_value != ";":
#                 cur_var_dec.append(cur_tok)
#                 i += 1
#                 cur_tok = tokens[i]
#                 cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace(
#                     "\t", ""
#                 )
#             cur_var_dec.append(cur_tok)
#             a.appendChild(parse_var_dec(dom_tree, cur_var_dec))
#         else:
#             break
#     a.appendChild(parse_statements(dom_tree, tokens[i:-1]))
#     a.appendChild(tokens[-1])
#     return a
#
#
# def parse_subroutine_dec(dom_tree: Document, tokens: list[Element]) -> Element:
#     a = dom_tree.createElement("subroutineDec")
#     a.appendChild(tokens[0])
#     a.appendChild(tokens[1])
#     a.appendChild(tokens[2])
#     a.appendChild(tokens[3])
#     parameter_list_tokens = []
#     i = 4
#     while True:
#         cur_tok = tokens[i]
#         cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace("\t", "")
#         i += 1
#         if cur_tok_value == ")":
#             break
#         parameter_list_tokens.append(tokens[i])
#     a.appendChild(parse_parameter_list(dom_tree, parameter_list_tokens))
#     a.appendChild(tokens[i - 1])
#     a.appendChild(parse_subroutine_body(dom_tree, tokens[i:]))
#     return a
#
#
# def parse_class(dom_tree: Document, tokens: list[Element]) -> Element:
#     a = dom_tree.createElement("class")
#     a.appendChild(tokens[0])
#     a.appendChild(tokens[1])
#     a.appendChild(tokens[2])
#     i = 2
#     while i < len(tokens) - 2:
#         i += 1
#         cur_tok = tokens[i]
#         cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace("\t", "")
#         if cur_tok_value in ["static", "field"]:
#             current_classVarDec = [cur_tok]
#             while True:
#                 i += 1
#                 cur_tok = tokens[i]
#                 cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace(
#                     "\t", ""
#                 )
#                 current_classVarDec.append(cur_tok)
#                 if cur_tok_value == ";":
#                     break
#             a.appendChild(parse_class_var_dec(dom_tree, current_classVarDec))
#         elif cur_tok_value in ["constructor", "function", "method"]:
#             current_subroutineDec = [cur_tok]
#             bo = bc = 0
#             while True:
#                 i += 1
#                 cur_tok = tokens[i]
#                 cur_tok_value = cur_tok.firstChild.nodeValue.replace(" ", "").replace(
#                     "\t", ""
#                 )
#                 current_subroutineDec.append(cur_tok)
#                 if cur_tok_value == "{":
#                     bo += 1
#                 if cur_tok_value == "}":
#                     bc += 1
#                 if bo == bc and bo != 0:
#                     break
#             a.appendChild(parse_subroutine_dec(dom_tree, current_subroutineDec))
#     a.appendChild(tokens[-1])
#     return a
#
#
# def parse_tokens(path: str) -> Document:
#     dom_tree = Document()
#     dt = xml.dom.minidom.parse(path)
#     tokens = dt.documentElement
#     ans = []
#     cl: list[Element] = []
#     for token in tokens.childNodes:
#         if len(token.childNodes) == 0:
#             continue
#         if (
#             token.firstChild.nodeValue.replace(" ", "").replace("\t", "") == "class"
#             and len(cl) != 0
#         ):
#             ans.append(cl)
#             cl = []
#         cl.append(token)
#     ans += [cl]
#     for i in ans:
#         dom_tree.appendChild(parse_class(dom_tree, i))
#     with open("test.xml", "w") as f:
#         f.write(dom_tree.childNodes[0].toprettyxml())
#     return dom_tree
#
#
# a = parse_tokens("C:\\HDK\\hdk\\tests\\test_syntax_analyzer_data\\MyTest\\MainT.xml")
# output_file = "C:\\HDK\\hdk\\tests\\test_syntax_analyzer_data\\MyTest\\Main.xml"
# with open(output_file, "w") as f:
#     f.write(a.childNodes[0].toprettyxml())
#
