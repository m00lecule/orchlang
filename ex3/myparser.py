import ply.yacc as yacc
from mylexer import MyLexer
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
import networkx as nx


class Expr:
    pass


class Root(Expr):
    def __init__(self, code=None):
        self.type = "root"
        self.scope = Scope()
        self.code = code
        self.scope.push_layer()

    def plot_init(self):
        G = nx.DiGraph()

        self.plot(G)

        pos = graphviz_layout(G, prog="dot")

        labels = nx.get_node_attributes(G, "desc")

        binop_nodes = [
            n for (n, ty) in nx.get_node_attributes(G, "type").items() if ty == "binop"
        ]

        nx.draw(
            G,
            pos,
            font_size=20,
            node_size=3000,
            labels=labels,
            arrows=True,
            font_family="fantasy",
            alpha=0.8,
        )

        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=binop_nodes,
            node_color="red",
            node_size=3000,
            font_family="fantasy",
            alpha=0.8,
            node_shape="s",
        )

        plt.axis("off")
        plt.savefig("labels_and_colors.png")  # save as png
        plt.show()

    def plot(self, G):
        for line in self.code:
            G.add_edge(self, line)
            line.plot(G)

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
    def __init__(self, left, op, right, op_sign):
        self.type = "binop"
        self.left = left
        self.right = right
        self.op = op
        self.op_sign = op_sign

    def plot(self, G):
        G.add_node(self, desc=self.op_sign, type=self.type)
        G.add_edge(self, self.left)
        G.add_edge(self, self.right)
        self.left.plot(G)
        self.right.plot(G)

    def eval(self, scope):
        return self.op(self.left.eval(scope), self.right.eval(scope))


class BinOpReversable(BinOp):
    pass


class Constant(Expr):
    def __init__(self, value):
        self.type = "const"
        self.value = value

    def eval(self, scope=None):
        return self.value

    def plot(self, G):
        G.add_node(self, desc=self.value)


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
    def __init__(self, variable, value, type_of):
        self.variable = variable
        self.value = value
        self.type_of = type_of

    def eval(self, scope):
        scope.put_local(self.variable, self.value.eval(scope), self.type_of)
        return ()  # Scala easter egg

    def plot(self, G):
        G.add_node(self, desc="init", type=self.type_of)
        G.add_node(self.variable, desc=self.variable)
        G.add_edge(self, self.variable)
        G.add_edge(self, self.value)
        self.value.plot(G)


class FunctionInit(Expr):
    def __init__(self, args, func_name, body):
        self.args = args
        self.func_name = func_name
        self.code = body

    def eval(self, scope):
        scope.put_func(self.func_name, self.args, self.code)
        return ()


class VariableRedef(Expr):
    def __init__(self, variable, value, type_of):
        self.variable = variable
        self.value = value
        self.type_of = type_of

    def eval(self, scope):
        return scope.redef_var(self.variable, self.value.eval(scope), self.type_of)

    def plot(self, G):
        pass


class VariableCall(Expr):
    def __init__(self, variable, type_of=None):
        self.variable = variable
        self.type_of = type_of

    def eval(self, scope):
        return scope.get(self.variable, self.type_of)

    def plot(self, G):
        G.add_node(self, desc=self.variable, type=self.type_of)


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

    def plot(self, G):
        pass


class IfElse(Expr):
    def __init__(self, cond, if_block, else_block=None):
        self.cond = cond
        self.if_block = if_block
        self.else_block = else_block

    def eval(self, scope):
        if self.cond.eval(scope):
            return self.if_block.eval(scope)

        return self.else_block.eval(scope) if self.else_block else ()

    def plot(self, G):
        pass


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

    def get(self, variable, call_type):
        for l in self.stack:
            if variable in l:
                value, typed = l[variable]
                if call_type is not None and typed != call_type:
                    raise Exception(
                        f"Variable {variable} of type {typed} can not be assigned to {call_type} typed value!"
                    )
                return value

        raise Exception(f"Variable {variable} has not been initialized!")

    def put_local(self, variable, value, type_of):
        self.stack[-1][variable] = (value, type_of)

    def redef_var(self, variable, value, type_of):
        for l in self.stack:
            if variable in l:
                _, temptype = l[variable]
                if temptype != type_of:
                    raise Exception(
                        f"Variable {variable} of type {temptype} can not be assigned to {type_of} typed value!"
                    )

                l[variable] = (value, type_of)
                return ()

        raise Exception(f"Variable {variable} has not been initialized!")

    def _print(self):
        for l in self.stack:
            print(l)


NumberOps = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "/": lambda x, y: x / y,
    "%": lambda x, y: x % y,
    "*": lambda x, y: x * y,
    "**": lambda x, y: x ** y,
}

CondOps = {
    ">": lambda x, y: x > y,
    "<": lambda x, y: x < y,
    ">=": lambda x, y: x >= y,
    "<=": lambda x, y: x <= y,
    "==": lambda x, y: x == y,
}

LopOp = {"&&": lambda x, y: x and y, "||": lambda x, y: x or y}


class MyParser(object):

    tokens = MyLexer.tokens

    precedence = (
        ("left", "BIN_OP_2", "LOG_OP"),
        ("left", "BIN_OP_1", "SEMI"),
        ("right", "POWER"),
    )

    def p_error(self, p):
        raise Exception("Syntax error")

    def p_root_block(self, p):
        """root : LCPAREN block RCPAREN
        """
        p[0] = p[2]

    def p_block_line(self, p):
        """block : block SEMI line
        """
        p[0] = p[1] + p[3]

    def p_block_is_line(self, p):
        """block : line
        """
        p[0] = p[1]

    def p_line_name(self, p):
        """line : NAME
        """
        p[0] = [VariableCall(p[1])]

    def p_line_is(self, p):
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

    def p_for_loop(self, p):
        """for : FOR LPAREN assign SEMI cond SEMI assign RPAREN LCPAREN block RCPAREN
        """
        p[0] = ForLoop(p[3], p[5], p[7], Root(p[10]))

    def p_expr_name_call(self, p):
        """expr : NAME          
        """
        p[0] = VariableCall(p[1], type_of=MyLexer.reserved["DOUBLE"])

    def p_if_block(self, p):
        """ ifelse : IF LPAREN cond RPAREN LCPAREN block RCPAREN
        """
        p[0] = IfElse(p[3], Root(p[6]))

    def p_if_else_block(self, p):
        """ ifelse : IF LPAREN cond RPAREN LCPAREN block RCPAREN ELSE LCPAREN block RCPAREN 
        """
        p[0] = IfElse(p[3], Root(p[6]), Root(p[10]))

    def p_if_line(self, p):
        """ ifelse : IF LPAREN cond RPAREN line
        """
        p[0] = IfElse(p[3], Root(p[5]))

    def p_func(self, p):
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

    def p_arg_list_end(self, p):
        """ arg_list : expr
        """
        p[0] = [p[1]]

    def p_var_list(self, p):
        """ var_list : var_list COMA NAME
        """
        p[0] = p[1] + [p[3]]

    def p_var_list_end(self, p):
        """ var_list : NAME
        """
        p[0] = [p[1]]

    def p_if_else_line(self, p):
        """ ifelse : IF LPAREN cond RPAREN line ELSE line 
        """
        p[0] = IfElse(p[3], Root(p[5]), Root(p[7]))

    def p_assign_expr(self, p):
        """assign : NUMBER NAME IS expr
        """
        p[0] = VariableInit(p[2], p[4], MyLexer.reserved[p[1]])

    def p_override_expr(self, p):
        """assign : NAME IS expr
        """
        p[0] = VariableRedef(p[1], p[3], MyLexer.reserved["DOUBLE"])

    def p_override_cond(self, p):
        """assign : NAME IS cond
        """
        p[0] = VariableRedef(p[1], p[3], MyLexer.reserved["BOOL"])

    def p_override_str(self, p):
        """assign : NAME IS stream
        """
        p[0] = VariableRedef(p[1], p[3], MyLexer.reserved["STRING"])

    def p_set_bool(self, p):
        """assign : BOOL NAME IS cond
        """
        p[0] = VariableInit(p[2], p[4], MyLexer.reserved[p[1]])

    def p_set_str(self, p):
        """assign : STRING_T NAME IS stream
        """
        p[0] = VariableInit(p[2], p[4], MyLexer.reserved[p[1]])

    def p_str_binop(self, p):
        """stream : stream BIN_OP_2 stream  
        """
        if p[2] == "+":
            p[0] = BinOp(p[1], lambda x, y: x + y, p[3], p[2])

    def p_str_name(self, p):
        """stream : NAME  
        """
        p[0] = VariableCall(p[1], type_of=MyLexer.reserved["STRING"])

    def p_str_2_str(self, p):
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
        p[0] = BinOpReversable(p[1], LopOp[p[2]], p[3], p[2])

    def p_cond_rel(self, p):
        """ cond : expr COND_OP expr   
        """
        if p[2] in ["=="]:
            p[0] = BinOpReversable(p[1], CondOps[p[2]], p[3], p[2])
        else:
            p[0] = BinOp(p[1], CondOps[p[2]], p[3], p[2])

    def p_root_line(self, p):
        """root : line     
        """
        p[0] = p[1]

    def p_expr_paren(self, p):
        """expr : LPAREN expr RPAREN          
        """
        p[0] = p[2]

    def p_expr_binop(self, p):
        """expr : expr BIN_OP_1 expr
                | expr BIN_OP_2 expr
                | expr POWER expr           
        """

        if p[2] in ["+", "*"]:
            p[0] = BinOpReversable(p[1], NumberOps[p[2]], p[3], p[2])
        else:
            p[0] = BinOp(p[1], NumberOps[p[2]], p[3], p[2])

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

    # context.plot_init()

    print(context.eval_in_scope())
