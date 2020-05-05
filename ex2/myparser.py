import ply.yacc as yacc
from mylexer import MyLexer


class MyParser(object):

    tokens = MyLexer.tokens

    precedence = (
        ("left", "BIN_OP_2", "LOG_OP"),
        ("left", "BIN_OP_1", "SEMI"),
        ("right", "POWER"),
    )

    def _is_initialized(self, name):
        return (
            name in self.strings.keys()
            or name in self.boolean.keys()
            or name in self.numbers.keys()
        )

    def p_error(self, p):
        print("Syntax error")

    def p_root_semi(self, p):
        """root : root SEMI root
                | root SEMI          
        """

    def p_get_var(self, p):
        """expr : NAME          
        """
        if p[1] in self.boolean.keys():
            p[0] = self.boolean[p[1]]
        elif p[1] in self.strings.keys():
            p[0] = self.strings[p[1]]
        elif p[1] in self.numbers.keys():
            p[0] = self.numbers[p[1]]
        else:
            print("VARIABLE DOES NOT EXIST")

    def p_root_if(self, p):
        """ root : IF LPAREN cond RPAREN expr 
        """
        if p[3] == True:
            print(f"Result {p[5]}")

    def p_root_if_else(self, p):
        """ root : IF LPAREN cond RPAREN expr ELSE expr 
        """
        if p[3] == False:
            print(f"Result {p[7]}")
        else:
            print(f"Result {p[5]}")

    def p_root_set_numb(self, p):
        """root : NUMBER NAME IS expr
        """

        if self._is_initialized(p[2]):
            print("Variable already exists")
        else:
            self.numbers[p[2]] = p[4]

    def p_root_override_numb(self, p):
        """root : NAME IS expr
        """

        if p[1] not in self.numbers.keys():
            print(f" {p[1]} variable of type numeric does not exist")
        else:
            self.numbers[p[1]] = p[3]

    def p_root_override_bool(self, p):
        """root : NAME IS cond
        """

        if p[1] not in self.boolean.keys():
            print(f" {p[1]} variable of type boolean does not exist")
        else:
            self.boolean[p[1]] = p[3]

    def p_root_override_str(self, p):
        """root : NAME IS stream
        """

        if p[1] not in self.strings.keys():
            print(f" {p[1]} variable of type boolean does not exist")
        else:
            self.strings[p[1]] = p[3]

    def p_root_set_bool(self, p):
        """root : BOOL NAME IS cond
        """
        if self._is_initialized(p[2]):
            print("VARIABLE ALREADY EXISTS")
        else:
            self.boolean[p[2]] = p[4]

    def p_root_set_str(self, p):
        """root : STRING_T NAME IS stream
        """

        if self._is_initialized(p[2]):
            print("VARIABLE ALREADY EXISTS")
        else:
            print(f"Name {p[2]} - {p[4]}")
            self.strings[p[2]] = p[4]

    def p_stream_binop(self, p):
        """stream : stream BIN_OP_2 stream  
        """
        if p[2] == "+":
            p[0] = p[1] + p[3]

    def p_stream_2_var(self, p):
        """stream : NAME  
        """

        if p[1] in self.strings.keys():
            p[0] = self.strings[p[1]]

    def p_stream_2_str(self, p):
        """stream : STRING  
        """
        p[0] = p[1][1:-1]

    def p_cond_2_bool(self, p):
        """ cond : BOOL    
        """
        p[0] = p[1]

    def p_cond_binop(self, p):
        """ cond : cond LOG_OP cond   
        """
        if p[2] == "&&":
            p[0] = p[1] and p[3]
        elif p[2] == "||":
            p[0] = p[1] or p[3]

        print(f"{p[1]} {p[2]} {p[3]}")
        print(" |/")
        print(p[0])

    def p_cond_rel(self, p):
        """ cond : expr COND_OP expr   
        """
        if p[2] == ">":
            p[0] = p[1] > p[3]
        elif p[2] == "<":
            p[0] = p[1] < p[3]
        elif p[2] == ">=":
            p[0] = p[1] >= p[3]
        elif p[2] == "<=":
            p[0] = p[1] <= p[3]
        elif p[2] == "==":
            p[0] = p[1] == p[3]

        print(f"{p[1]} {p[2]} {p[3]}")
        print(" |/")
        print(p[0])

    def p_root(self, p):
        """root : expr 
                | cond 
                | stream     
        """
        p[0] = p[1]
        print(f"Evaluated value: {p[1]}")

    def p_parenth(self, p):
        """expr : LPAREN expr RPAREN          
        """
        p[0] = p[2]
        print(f"Evaluated value: {p[0]}")

    def p_expr_binop(self, p):
        """expr : expr BIN_OP_1 expr
                | expr BIN_OP_2 expr
                | expr POWER expr           
        """
        if p[2] == "+":
            p[0] = p[1] + p[3]
        elif p[2] == "-":
            p[0] = p[1] - p[3]
        elif p[2] == "/":
            p[0] = p[1] / p[3]
        elif p[2] == "%":
            p[0] = p[1] % p[3]
        elif p[2] == "*":
            p[0] = p[1] * p[3]
        elif p[2] == "**":
            p[0] = p[1] ** p[3]

        print(f"{p[1]} {p[2]} {p[3]}")
        print(" |/")
        print(p[0])

    def p_expr_2_numb(self, p):
        """expr : INT
                | FLOAT           
        """
        p[0] = p[1]

    def __init__(self):
        self.lexer = MyLexer()
        self.parser = yacc.yacc(module=self)
        self.numbers = {}
        self.strings = {}
        self.boolean = {}


parser = MyParser()

while True:
    try:
        s = input(">>")
    except EOFError:
        break
    result = parser.parser.parse(s)
    print(result)
