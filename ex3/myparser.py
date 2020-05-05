import ply.yacc as yacc
from mylexer import MyLexer


class Expr:
    pass


class Root(Expr):
    def __init__(self, code=None):
        self.type = "root"
        self.scope = Scope()
        self.code = code
        self.scope.push_layer()

    def eval(self, scope=None):
        scp = self.scope if scope == None else scope
        scp.push_layer()
        ret = [task.eval(scp) for task in self.code]
        scp.pop_layer()
        return ret  # self.code.eval(self.scope)

    def eval_in_scope(self, scope=None):
        scp = self.scope if scope == None else scope
        return [task.eval(scp) for task in self.code]


class BinOp(Expr):
    def __init__(self, left, op, right):
        self.type = "binop"
        self.left = left
        self.right = right
        self.op = op

    def eval(self, scope):
        return self.op(self.left.eval(scope), self.right.eval(scope))


class Constant(Expr):
    def __init__(self, value):
        self.type = "const"
        self.value = value

    def eval(self, scope=None):
        return self.value


class ForLoop(Expr):
    def __init__(self, set_var, cond, expr, code):
        self.type = "loop"
        self.set = set_var
        self.cond = cond
        self.expr = expr
        self.body = code

    def eval(self, scope=None):
        scope.push_layer()
        self.set.eval(scope)

        while self.cond.eval(scope):
            print(self.body.eval_in_scope(scope))
            self.expr.eval(scope)

        scope.pop_layer()
        return ()


class VariableInit(Expr):
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value

    def eval(self, scope):
        scope.put_local(self.variable, self.value.eval(scope))
        return ()  # Scala easter egg


class FunctionInit(Expr):
    def __init__(self, args, func_name, body):
        self.args = args
        self.func_name = func_name
        self.code = body

    def eval(self, scope):
        scope.put_func(self.func_name, self.args, self.code)
        return ()


class VariableRedef(Expr):
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value

    def eval(self, scope):
        return scope.redef_var(self.variable, self.value.eval(scope))


class VariableCall(Expr):
    def __init__(self, variable):
        self.variable = variable

    def eval(self, scope):
        return scope.get(self.variable)


class FunctionCall(Expr):
    def __init__(self, fun_name, args):
        self.fun_name = fun_name
        self.args = args

    def eval(self, scope):
        args, fun = scope.get_func(self.fun_name)

        if len(args) != len(self.args):
            raise Exception(
                f"Invalid args [{len(self.args)}] in {self.fun_name} invocation. Expected [{len(args)}] arguments"
            )

        scope.push_layer()

        for (n, v) in zip(args, self.args):
            scope.put_local(n, v.eval(scope))

        ret = fun.eval_in_scope(scope)
        print(ret)
        scope.pop_layer()
        return ret


class IfElse(Expr):
    def __init__(self, cond, if_block, else_block=None):
        self.cond = cond
        self.if_block = if_block
        self.else_block = else_block

    def eval(self, scope):
        if self.cond.eval(scope):
            return self.if_block.eval(scope)

        return self.else_block.eval(scope) if self.else_block else ()


class Scope(object):
    def __init__(self):
        self.stack = []
        self.func_scope = {}

    def push_layer(self):
        self.stack.append({})

    def pop_layer(self):
        self._print()
        self.stack.pop()
        self._print()

    def put_func(self, func_name, args, func_body):
        for l in self.stack:
            for variable in l:
                if func_name == variable:
                    raise Exception(f"Function name {func_name} is taken by variable")
        for fun_n in self.func_scope:
            if fun_n == func_name:
                raise Exception(
                    f"Function name {func_name} is taken by another function"
                )
        self.func_scope[func_name] = (args, func_body)

    def get_func(self, func_name):
        return self.func_scope[func_name]

    def get(self, variable):
        for l in self.stack:
            if variable in l:
                return l[variable]

        raise Exception(f"Variable {variable} has not been initialized!")

    def put_local(self, variable, value):
        self.stack[-1][variable] = value

    def redef_var(self, variable, value):
        for l in self.stack:
            if variable in l:
                l[variable] = value
                return ()

        raise Exception(f"Variable {variable} has not been initialized!")

    def _print(self):
        for l in self.stack:
            print(l)


class MyParser(object):

    tokens = MyLexer.tokens

    precedence = (
        ("left", "BIN_OP_2", "LOG_OP"),
        ("left", "BIN_OP_1", "SEMI"),
        ("right", "POWER"),
    )

    def p_error(self, p):
        print("Syntax error")

    def p_block(self, p):
        """root : LCPAREN block RCPAREN
        """
        p[0] = p[2]

    def p_blockty(self, p):
        """block : block SEMI line
        """
        p[0] = p[1] + p[3]

    def p_blockty2(self, p):
        """block : line
        """
        p[0] = p[1]

    def p_rootl(self, p):
        """line : expr
                | cond
                | stream
                | assign
                | for
                | ifelse
                | def_fun
                | call_fun
        """
        p[0] = [p[1]]

    def p_for(self, p):
        """for : FOR LPAREN assign SEMI cond SEMI assign RPAREN LCPAREN block RCPAREN
        """
        p[0] = ForLoop(p[3], p[5], p[7], Root(p[10]))

    def p_get_var(self, p):
        """expr : NAME          
        """
        p[0] = VariableCall(p[1])

    def p_root_if(self, p):
        """ ifelse : IF LPAREN cond RPAREN LCPAREN block RCPAREN
        """
        p[0] = IfElse(p[3], Root(p[6]))

    def p_root_if_else(self, p):
        """ ifelse : IF LPAREN cond RPAREN LCPAREN block RCPAREN ELSE LCPAREN block RCPAREN 
        """
        p[0] = IfElse(p[3], Root(p[6]), Root(p[10]))

    def p_root_if_l(self, p):
        """ ifelse : IF LPAREN cond RPAREN line
        """
        p[0] = IfElse(p[3], Root(p[5]))

    def p_func_def(self, p):
        """ def_fun : DEF NAME LPAREN var_list RPAREN LCPAREN block RCPAREN 
        """
        p[0] = FunctionInit(p[4], p[2], Root(p[7]))

    def p_func_call(self, p):
        """ call_fun : NAME LPAREN arg_list RPAREN  
        """
        p[0] = FunctionCall(p[1], p[3])

    def p_arg_list(self, p):
        """ arg_list : arg_list COMA expr
        """
        p[0] = p[1] + [p[3]]

    def p_arg_list1(self, p):
        """ arg_list : expr
        """
        p[0] = [p[1]]

    def p_var_list(self, p):
        """ var_list : var_list COMA NAME
        """
        p[0] = p[1] + [p[3]]

    def p_var_list1(self, p):
        """ var_list : NAME
        """
        p[0] = [p[1]]

    def p_root_if_else_l(self, p):
        """ ifelse : IF LPAREN cond RPAREN line ELSE line 
        """
        p[0] = IfElse(p[3], Root(p[5]), Root(p[7]))

    def p_root_set_numb(self, p):
        """assign : NUMBER NAME IS expr
        """
        p[0] = VariableInit(p[2], p[4])

    def p_root_override_numb(self, p):
        """assign : NAME IS expr
        """
        p[0] = VariableRedef(p[1], p[3])

    def p_root_override_bool(self, p):
        """assign : NAME IS cond
        """
        p[0] = VariableRedef(p[1], p[3])

    def p_root_override_str(self, p):
        """assign : NAME IS stream
        """
        p[0] = VariableRedef(p[1], p[3])

    def p_root_set_bool(self, p):
        """assign : BOOL NAME IS cond
        """
        p[0] = VariableInit(p[2], p[4])

    def p_root_set_str(self, p):
        """assign : STRING_T NAME IS stream
        """
        p[0] = VariableInit(p[2], p[4])

    def p_stream_binop(self, p):
        """stream : stream BIN_OP_2 stream  
        """
        if p[2] == "+":
            p[0] = BinOp(p[1], lambda x, y: x + y, p[3])

    def p_stream_2_var(self, p):
        """stream : NAME  
        """
        p[0] = VariableCall(p[1])

    def p_stream_2_str(self, p):
        """stream : STRING  
        """
        p[0] = Constant(p[1][1:-1])

    def p_cond_2_bool(self, p):
        """ cond : TRUE
                 | FALSE    
        """
        p[0] = Constant(p[1])

    def p_cond_binop(self, p):
        """ cond : cond LOG_OP cond   
        """
        func = None

        if p[2] == "&&":
            func = lambda x, y: x and y
        elif p[2] == "||":
            func = lambda x, y: x or y

        p[0] = BinOp(p[1], func, p[3])

    def p_cond_rel(self, p):
        """ cond : expr COND_OP expr   
        """

        func = None
        if p[2] == ">":
            func = lambda x, y: x > y
        elif p[2] == "<":
            func = lambda x, y: x < y
        elif p[2] == ">=":
            func = lambda x, y: x >= y
        elif p[2] == "<=":
            func = lambda x, y: x <= y
        elif p[2] == "==":
            func = lambda x, y: x == y

        p[0] = BinOp(p[1], func, p[3])

    def p_root(self, p):
        """root : line     
        """
        p[0] = p[1]

    # def p_rootl(self, p):
    #     """line : expr
    #             | cond
    #             | stream
    #     """
    #     p[0] = p[1]

    def p_parenth(self, p):
        """expr : LPAREN expr RPAREN          
        """
        p[0] = p[2]

    def p_expr_binop(self, p):
        """expr : expr BIN_OP_1 expr
                | expr BIN_OP_2 expr
                | expr POWER expr           
        """
        func = None

        if p[2] == "+":
            func = lambda x, y: x + y
        elif p[2] == "-":
            func = lambda x, y: x - y
        elif p[2] == "/":
            func = lambda x, y: x / y
        elif p[2] == "%":
            func = lambda x, y: x % y
        elif p[2] == "*":
            func = lambda x, y: x * y
        elif p[2] == "**":
            func = lambda x, y: x ** y

        p[0] = BinOp(p[1], func, p[3])

    def p_expr_2_numb(self, p):
        """expr : INT
                | FLOAT           
        """
        p[0] = Constant(p[1])

    def __init__(self):
        self.lexer = MyLexer()
        self.parser = yacc.yacc(module=self)


parser = MyParser()

context = Root()


def getline(prompt):
    return input(prompt)


while True:
    code = ""
    lastchar = "/"

    line = getline(">> ")

    while line[-1] == "/":
        code += line[:-1] + "; "
        line = getline("> ")

    code += line

    print(code)

    print(parser.parser.parse(code))
    context.code = parser.parser.parse(code)

    print(context.eval_in_scope())
