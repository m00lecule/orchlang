import sys
import ply.lex as lex

sys.path.insert(0, "../..")


class MyLexer(object):

    reserved = {
        "IF": "IF",
        "ELSE": "ELSE",
        "WHILE": "WHILE",
        "FOR": "FOR",
        "SET": "SET",
        "INT": "NUMBER",
        "DOUBLE": "NUMBER",
        "BOOL": "BOOL",
        "STRING": "STRING_T",
        "True": "TRUE",
        "False": "FALSE",
        "def": "DEF",
    }

    tokens = list(reserved.values()) + [
        "LOG_OP",
        "IS",
        "LCPAREN",
        "RCPAREN",
        "STRING",
        "NAME",
        "FLOAT",
        "INT",
        "BIN_OP_1",
        "BIN_OP_2",
        "POWER",
        "LPAREN",
        "RPAREN",
        "COND_OP",
        "SEMI",
        "COMA",
    ]

    t_LOG_OP = r"\&\&|\|\|"
    t_POWER = r"\*\*"
    t_BIN_OP_1 = r"/|\*|\%"
    t_BIN_OP_2 = r"\+|\-"
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LCPAREN = r"\{"
    t_RCPAREN = r"\}"
    t_IS = r"\="
    t_COND_OP = r"\=\=|\>\=|\<\=|\>|\<"
    t_SEMI = r"\;"
    t_COMA = r"\,"

    def t_STRING(self, t):
        '"[ a-zA-Z0-9_]*"'
        return t

    def t_NAME(self, t):
        "[a-zA-Z_][a-zA-Z0-9_]*"

        if t.value == "true" or t.value == "false":
            t.type = "BOOL"
        else:
            t.type = MyLexer.reserved.get(t.value, "NAME")
        return t

    def t_FLOAT(self, t):
        r"\-?\d*\.\d*"
        t.value = float(t.value)
        return t

    def t_INT(self, t):
        r"\-?\d+"
        t.value = int(t.value)
        return t

    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    t_ignore = " \t"

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)


x = MyLexer()

x.test("x >= 125")
