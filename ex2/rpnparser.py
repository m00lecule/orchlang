import ply.yacc as yacc
from mylexer import MyLexer

class MyParser(object):

    tokens = MyLexer.tokens

    variables = {}

    precedence = (
        ('left', 'BIN_OP_2'),
        ('left', 'BIN_OP_1', 'SEMI'),
        ('right', 'POWER'),
    )

    def p_error(self, p):
        print("Syntax error")

    def p_root_rec(self, p):
        '''root : root SEMI root
                | root SEMI          
        '''

    def p_relations(self, p):
        ''' root : expression expression COND_OP   
        '''
        if p[3] == '>':
            p[0] = p[1] > p[2]
        elif p[3] == '<':
            p[0] = p[1] < p[2]    
        elif p[3] == '>=':
            p[0] = p[1] >= p[2]
        elif p[3] == '<=':
            p[0] = p[1] <= p[2]
        elif p[3] == '==':
            p[0] = p[1] == p[2]

        print(f"Evaluated value: {p[0]}")

    def p_root(self, p):
        '''root : expression       
        '''
        p[0] = p[1]
        print(f"Evaluated value: {p[1]}")


    def p_parenthesis(self, p):
        '''expression : LPAREN expression RPAREN          
        '''
        p[0] = p[2]
        print(f"Evaluated value: {p[0]}")

    def p_expression_binop(self, p):
        '''expression : expression expression BIN_OP_1
                    | expression expression BIN_OP_2
                    | expression expression POWER       
        '''
        if p[3] == '+':
            p[0] = p[1] + p[2]
        elif p[3] == '-':
            p[0] = p[1] - p[2]
        elif p[3] == '/':
            p[0] = p[1] / p[2]
        elif p[3] == '%':
            p[0] = p[1] % p[2]    
        elif p[3] == '*':
            p[0] = p[1] * p[2]
        elif p[3] == '**':
            p[0] = p[1] ** p[2]
    

    def p_expression_numb(self, p):
        '''expression : INT
                      | FLOAT           
        '''
        p[0] = p[1]


    def __init__(self):
        self.lexer = MyLexer()
        self.parser = yacc.yacc(module=self)

parser = MyParser()

while True:
    try:
        s = input('>>')
    except EOFError:
        break
    parser.parser.parse(s)