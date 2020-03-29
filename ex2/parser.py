from mylexer import MyLexer

lexer = MyLexer().lexer

while True:
    try:
        s = input('calc > ')
    except EOFError:
        break
    if not s:
        continue
        
    lexer.input(s)    
    while True:    
        tok = lexer.token()
        if not tok: 
         break      # No more input
        print(tok)
