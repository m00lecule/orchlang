import ply.yacc as yacc
from mylexer import MyLexer


class MyParser(object):

    tokens = MyLexer.tokens

    numbers = {}

    strings = {}

    boolean = {}

    precedence = (
        ("left", "BIN_OP_2", "LOG_OP"),
        ("left", "BIN_OP_1", "SEMI"),
        ("right", "POWER"),
    )

    def _variable_existis(self, name):
        return (
            name in MyParser.strings.keys()
            or name in MyParser.boolean.keys()
            or name in MyParser.numbers.keys()
        )

    def p_error(self, p):
        print("Syntax error")

    def p_root_rec(self, p):
        """root : root SEMI root
                | root SEMI          
        """

    def p_root_get(self, p):
        """expression : NAME          
        """
        if p[1] in MyParser.boolean.keys():
            p[0] = MyParser.boolean[p[1]]
        elif p[1] in MyParser.strings.keys():
            p[0] = MyParser.strings[p[1]]
        elif p[1] in MyParser.numbers.keys():
            p[0] = MyParser.numbers[p[1]]
        else:
            print("VARIABLE DOES NOT EXIST")

    def p_root_if(self, p):
        """ root : IF LPAREN condition RPAREN expression 
        """
        if p[3] == True:
            print(f"Result {p[5]}")

    def p_root_if_2(self, p):
        """ root : IF LPAREN condition RPAREN expression ELSE expression 
        """
        if p[3] == False:
            print(f"Result {p[7]}")
        else:
            print(f"Result {p[5]}")

    def p_root_set_number(self, p):
        """root : NUMBER NAME IS expression
        """

        if self._variable_existis(p[2]):
            print("Variable already exists")
        else:
            MyParser.numbers[p[2]] = p[4]

    def p_root_override_number(self, p):
        """root : NAME IS expression
        """

        if p[1] not in MyParser.numbers.keys():
            print(f" {p[1]} variable of type numeric does not exist")
        else:
            MyParser.numbers[p[1]] = p[3]

    def p_root_override_bool(self, p):
        """root : NAME IS condition
        """

        if p[1] not in MyParser.boolean.keys():
            print(f" {p[1]} variable of type boolean does not exist")
        else:
            MyParser.boolean[p[1]] = p[3]

    def p_root_override_string(self, p):
        """root : NAME IS stream
        """

        if p[1] not in MyParser.strings.keys():
            print(f" {p[1]} variable of type boolean does not exist")
        else:
            MyParser.strings[p[1]] = p[3]

    def p_root_set_boolean(self, p):
        """root : BOOL NAME IS condition
        """
        if self._variable_existis(p[2]):
            print("VARIABLE ALREADY EXISTS")
        else:
            MyParser.boolean[p[2]] = p[4]

    def p_root_set_string_stream(self, p):
        """root : STRING_T NAME IS stream
        """

        if self._variable_existis(p[2]):
            print("VARIABLE ALREADY EXISTS")
        else:
            print(f"Name {p[2]} - {p[4]}")
            MyParser.strings[p[2]] = p[4]

    def p_string_stream(self, p):
        """stream : stream BIN_OP_2 stream  
        """
        if p[2] == "+":
            p[0] = p[1] + p[3]

    def p_string_variale(self, p):
        """stream : NAME  
        """
        p[0] = MyParser.strings[p[1]]

    def p_string_stream_name(self, p):
        """stream : STRING  
        """
        p[0] = p[1][1:-1]

    def p_set_boolean(self, p):
        """ condition : BOOL    
        """
        p[0] = p[1]

    def p_condition(self, p):
        """ condition : condition LOG_OP condition   
        """
        if p[2] == "&&":
            p[0] = p[1] and p[3]
        elif p[2] == "||":
            p[0] = p[1] or p[3]

        print(f"{p[1]} {p[2]} {p[3]}")
        print(" |/")
        print(p[0])

    def p_relations(self, p):
        """ condition : expression COND_OP expression   
        """
        if p[2] == ">":
            p[0] = p[1] > p[3]
            print(f"{p[1]} > {p[3]}")
        elif p[2] == "<":
            p[0] = p[1] < p[3]
            print(f"{p[1]} < {p[3]}")
        elif p[2] == ">=":
            print(f"{p[1]} >= {p[3]}")
            p[0] = p[1] >= p[3]
        elif p[2] == "<=":
            print(f"{p[1]} <= {p[3]}")
            p[0] = p[1] <= p[3]
        elif p[2] == "==":
            p[0] = p[1] == p[3]
            print(f"{p[1]} == {p[3]}")

        print(" |/")
        print(p[0])

    def p_root(self, p):
        """root : expression 
                | condition 
                | stream     
        """
        p[0] = p[1]
        print(f"Evaluated value: {p[1]}")

    def p_parenthesis(self, p):
        """expression : LPAREN expression RPAREN          
        """
        p[0] = p[2]
        print(f"Evaluated value: {p[0]}")

    def p_expression_binop(self, p):
        """expression : expression BIN_OP_1 expression
                      | expression BIN_OP_2 expression
                      | expression POWER expression           
        """
        if p[2] == "+":
            p[0] = p[1] + p[3]
            print(f"{p[1]} + {p[3]}")
        elif p[2] == "-":
            p[0] = p[1] - p[3]
            print(f"{p[1]} - {p[3]}")
        elif p[2] == "/":
            p[0] = p[1] / p[3]
            print(f"{p[1]} / {p[3]}")
        elif p[2] == "%":
            p[0] = p[1] % p[3]
            print(f"{p[1]} % {p[3]}")
        elif p[2] == "*":
            p[0] = p[1] * p[3]
            print(f"{p[1]} * {p[3]}")
        elif p[2] == "**":
            p[0] = p[1] ** p[3]
            print(f"{p[1]} ** {p[3]}")

        print(" |/")
        print(p[0])

    def p_expression_numb(self, p):
        """expression : INT
                      | FLOAT           
        """
        p[0] = p[1]

    def __init__(self):
        self.lexer = MyLexer()
        self.parser = yacc.yacc(module=self)


parser = MyParser()

while True:
    try:
        s = input(">>")
    except EOFError:
        break
    parser.parser.parse(s)
