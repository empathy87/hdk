from hdk.assembly import parser, translator


def test_parse_add_program():
    lines = [
        "// Computes R0 = 2 + 3  (R0 refers to RAM[0])",
        "",
        "@2",
        "D=A",
        "@3",
        "D=D+A",
        "@0",
        "M=D",
    ]
    instructions = list(translator.translate(parser.parse_code(lines)))
    print(instructions)
