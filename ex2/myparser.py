import ply.yacc as yacc
from mylexer import MyLexer

class MyParser(object):

    tokens = MyLexer.tokens

    variables = {}

    precedence = (
        ('left', 'BIN_OP_2', 'LOG_OP'),
        ('left', 'BIN_OP_1', 'SEMI'),
        ('right', 'POWER'),
    )

    def p_error(self, p):
        print("Syntax error")

    def p_root_rec(self, p):
        '''root : root SEMI root
                | root SEMI          
        '''

    def p_root_if(self, p):
        ''' root : IF LPAREN condition RPAREN expression 
        '''
        if p[3] == True:
            print(f"Result {p[5]}")

    def p_root_if_2(self, p):
        ''' root : IF LPAREN condition RPAREN expression ELSE expression 
        '''
        if p[3] == False:
            print(f"Result {p[7]}")

    def p_root_set(self, p):
        '''root : NAME IS expression
        '''
        
        MyParser.variables[p[1]] = p[3]
        print(f"Added {MyParser.variables[p[1]]}")


    def p_condition(self, p):
        ''' condition : condition LOG_OP condition   
        '''
        if p[2] == '&&':
            p[0] = p[1] and p[3]
        elif p[2] == '||':
            p[0] = p[1] or p[3]    
        
    def p_relations(self, p):
        ''' condition : expression COND_OP expression   
        '''
        if p[2] == '>':
            p[0] = p[1] > p[3]
        elif p[2] == '<':
            p[0] = p[1] < p[3]    
        elif p[2] == '>=':
            p[0] = p[1] >= p[3]
        elif p[2] == '<=':
            p[0] = p[1] <= p[3]
        elif p[2] == '==':
            p[0] = p[1] == p[3]


    def p_root(self, p):
        '''root : expression 
                | condition      
        '''
        p[0] = p[1]
        print(f"Evaluated value: {p[1]}")


    def p_parenthesis(self, p):
        '''expression : LPAREN expression RPAREN          
        '''
        p[0] = p[2]
        print(f"Evaluated value: {p[0]}")

    def p_expression_binop(self, p):
        '''expression : expression BIN_OP_1 expression
                      | expression BIN_OP_2 expression
                      | expression POWER expression           
        '''
        if p[2] == '+':
            p[0] = p[1] + p[3]
        elif p[2] == '-':
            p[0] = p[1] - p[3]
        elif p[2] == '/':
            p[0] = p[1] / p[3]
        elif p[2] == '%':
            p[0] = p[1] % p[3]    
        elif p[2] == '*':
            p[0] = p[1] * p[3]
        elif p[2] == '**':
            p[0] = p[1] ** p[3]
    

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