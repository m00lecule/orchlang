import ply.yacc as yacc
from mylexer import MyLexer
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
import networkx as nx
import math


class Expr:
    pass


class Root(Expr):
    def __init__(self, code=None):
        self.type = "root"
        self.scope = Scope()
        self.code = self.trim(code)
        self.scope.push_layer()
        self.variables_changed = self.redefines_value() if code is not None else {}

    def redefines_value(self):
        return {
            c.variable
            for c in self.code
            if isinstance(c, VariableRedef) or isinstance(c, VariableInit)
        }

    def trim(self, code):
        if code == None:
            return code

        counter = 0
        for l in code:
            counter += 1
            if isinstance(l, tuple):
                t, _ = l
                if t == MyLexer.reserved["RETURN"]:
                    break

        return code[:counter]

    def plot_init(self):
        G = nx.MultiDiGraph()

        self.plot(G)

        pos = graphviz_layout(G, prog="dot")

        labels = nx.get_node_attributes(G, "desc")

        print(nx.get_edge_attributes(G, "desc"))

        edge_labels = {
            (u, v): d for (u, v, _), d in nx.get_edge_attributes(G, "desc").items()
        }

        binop_nodes = [
            n for (n, ty) in nx.get_node_attributes(G, "type").items() if ty == "binop"
        ]

        nx.draw(
            G, pos, font_size=20, node_size=3000, labels=labels, arrows=True, alpha=0.8,
        )

        nx.draw_networkx_nodes(
            G,
            pos,
            nodelist=binop_nodes,
            node_color="red",
            node_size=3000,
            alpha=0.8,
            node_shape="s",
        )
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        plt.axis("off")
        plt.savefig("labels_and_colors.png")
        plt.show()

    def init_opt(self):
        self.opt()

    def opt(self):
        # scope.push_layer()
        self.code = [task.opt() for task in self.code]
        # scope.pop_layer()
        return self

    def plot(self, G):
        G.add_node(self, desc="scope")
        for counter, line in enumerate(self.code):
            G.add_edge(self, line, desc=counter)
            line.plot(G)

    def eval(self, scope=None):
        scp = self.scope if scope == None else scope
        scp.push_layer()
        ret = self.eval_in_scope(scp)
        scp.pop_layer()
        return ret

    def eval_in_scope(self, scope=None):
        scp = self.scope if scope == None else scope

        ret = ()

        for task in self.code:
            if isinstance(task, tuple):
                ret_type, task = task
                ret = task.eval(scp)
                if ret_type == MyLexer.reserved["RETURN"]:
                    ret = (ret_type, ret)
                    break
            else:
                ret = task.eval(scp)

                if ret != ():
                    type_of, _ = ret

                    if type_of == MyLexer.reserved["RETURN"]:
                        break
        return ret


class UnaryOp(Expr):
    @staticmethod
    def clean_up():
        UnaryOp.pool = {}

    def opt_const(self):
        op = UnaryOps[self.op_sign]
        arg = self.arg
        op_sign = self.op_sign
        
        type_of = None

        if op_sign == "tostr":
            type_of = MyLexer.reserved["STRING"]
        elif op_sign == "tonumb":
            type_of = MyLexer.reserved["DOUBLE"]
        elif op_sign == "tobool":
            type_of = MyLexer.reserved["BOOL"]
        else:
            type_of = arg.type

        if type(arg) is Constant:
            return Constant.acquire(op(arg.value), type_of)

        return self

    @staticmethod
    def define_operation(arg, op_sign):
        operation = None
        
        if op_sign == "tostr":
            operation = ToString(arg)
        elif op_sign == "tonumb":
            operation = ToNumber(arg)
        elif op_sign == "tobool":
            operation = ToBool(arg)
        else:
            operation = UnaryOp(arg, op_sign)
        return operation

    @staticmethod
    def acquire(arg, op_sign):
        t = (arg, op_sign)

        if t not in UnaryOp.pool.keys():
            operation = UnaryOp.define_operation(arg, op_sign)
            operation = operation.opt()
            UnaryOp.pool[t] = operation

        return UnaryOp.pool[t]

    pool = {}

    def __init__(self, arg, op_sign):
        self.type = "unop"
        self.arg = arg
        self.op_sign = op_sign
        self.op = UnaryOps[self.op_sign]

    def opt(self):
        self.arg = self.arg.opt()
        return self.opt_const()

    def plot(self, G):
        G.add_node(self, desc=self.op_sign, type=self.type)
        G.add_edge(self, self.arg, desc="arg")
        self.arg.plot(G)

    def eval(self, scope):
        (l_type, l_val) = self.arg.eval(scope)

    
        if l_type is not MyLexer.reserved["DOUBLE"]:
            raise Exception(
                f"Unary operation - {self.op_sign} is not defined for {l_type}"
            )

        return (l_type, self.op(l_val))

    def __hash__(self):
        return hash(self.arg)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.arg == other.arg
    
    def depends_on(self):
        return self.arg.depends_on()



class ToString(UnaryOp):
    def __init__(self, arg):
        self.sign = "tostr"
        super(ToString, self).__init__(arg, self.sign)
        self.op = UnaryOps[self.sign]

    def opt(self):
        self.arg = self.arg.opt()

        if type(self.arg) is Constant:
            return Constant.acquire(self.op(self.arg.value), MyLexer.reserved["STRING"])
        return self

    def eval(self, scope):
        l_type, l_val = self.arg.eval(scope)

        return (MyLexer.reserved["STRING"], self.op((l_val)))


class ToNumber(UnaryOp):
    def __init__(self, arg):
        self.sign = "tonumb"
        super(ToNumber, self).__init__(arg, self.sign)
        self.op = UnaryOps[self.sign]

    def eval(self, scope):
        (l_type, l_val) = self.arg.eval(scope)
        return (MyLexer.reserved["DOUBLE"], self.op(l_val))

class ToBool(UnaryOp):
    def __init__(self, arg):
        self.sign = "tobool"
        super(ToBool, self).__init__(arg, self.sign)
        self.op = UnaryOps[self.sign]

    def eval(self, scope):
        (l_type, l_val) = self.arg.eval(scope)
        return (MyLexer.reserved["BOOL"], self.op(l_val))


class BinOp(Expr):

    pool = {}

    @staticmethod
    def clean_up():
        BinOp.pool = {}

    def __init__(self, left, right, op, op_sign):
        self.type = "binop"
        self.left = left
        self.right = right
        self.op_sign = op_sign
        self.op = op

    @staticmethod
    def define_operation(left, right, op_sign):
        operation = None

        if op_sign == "+":
            operation = Addition(left, right)
        elif op_sign == "-":
            operation = Subtract(left, right)
        elif op_sign == "/":
            operation = Divide(left, right)
        elif op_sign == "**":
            operation = Power(left, right)
        elif op_sign == "*":
            operation = Mult(left, right)
        elif op_sign == ">":
            operation = GT(left, right)
        elif op_sign == "<":
            operation = LT(left, right)
        elif op_sign == ">=":
            operation = GE(left, right)
        elif op_sign == "<=":
            operation = LE(left, right)
        elif op_sign == "&&":
            operation = AND(left, right)
        elif op_sign == "||":
            operation = OR(left, right)

        return operation

    @staticmethod
    def acquire(left, right, op_sign):
        t = (left, right, op_sign)

        if t not in BinOp.pool.keys():

            operation = BinOp.define_operation(left, right, op_sign)

            operation = operation.opt()

            BinOp.pool[t] = operation

        return BinOp.pool[t]

    def opt_const(self):
        left = self.left
        right = self.right
        op_sign = self.op_sign
        op = self.op

        if type(left) is Constant and type(right) is Constant:
            if left.type != right.type:
                if left.type == MyLexer.reserved["STRING"]:
                    right = right.to_string()
                if left.type == MyLexer.reserved["DOUBLE"]:
                    right = right.to_float()

            rel_type = left.type
            if op_sign in [">", "<", "<=", ">=", "=="]:
                rel_type = MyLexer.reserved["BOOL"]

            return Constant.acquire(op(left.value, right.value), rel_type)
        return self

    def opt(self):
        self.left = self.left.opt()
        self.right = self.right.opt()
        return self.opt_const()

    def depends_on(self):
        return self.left.depends_on().union(self.right.depends_on())

    def plot(self, G):
        G.add_node(self, desc=self.op_sign, type=self.type)

        if self.right == self.left:
            G.add_edge(self, self.left, desc="both")
        else:
            G.add_edge(self, self.left, desc="1")
            G.add_edge(self, self.right, desc="2")

        self.left.plot(G)

        if self.left != self.right:
            self.right.plot(G)

    def eval(self, scope):
        l_type, l_value = self.left.eval(scope)
        r_type, r_value = self.right.eval(scope)

        if l_type == MyLexer.reserved["DOUBLE"]:
            r_value = float(r_value)
            ret_type = MyLexer.reserved["DOUBLE"]
        elif l_type == MyLexer.reserved["STRING"]:
            r_value = str(r_value)
            ret_type = MyLexer.reserved["STRING"]
        elif l_type == MyLexer.reserved["BOOL"]:
            r_value = bool(r_value)
            ret_type = MyLexer.reserved["BOOL"]

        if self.op_sign in [">", "<", "<=", ">=", "=="]:
            ret_type = MyLexer.reserved["BOOL"]

        return (ret_type, self.op(l_value, r_value))

    def __hash__(self):
        return hash(self.left) + hash(self.right)

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__
            and self.left == other.left
            and self.right == other.right
            and self.op_sign == other.op_sign
        )


class Subtract(BinOp):
    def __init__(self, left, right):
        self.sign = "-"
        super(Subtract, self).__init__(left, right, NumberOps[self.sign], self.sign)

    def opt(self):
        left = self.left.opt()
        right = self.right.opt()
        if type(right) is Constant and right.value == 0:
            return left
        return self.opt_const()

    def typed(self):
        return "NUMBER"


class GT(BinOp):
    def __init__(self, left, right):
        self.sign = ">"
        super(GT, self).__init__(left, right, NumberOps[self.sign], self.sign)

    def typed(self):
        return "BOOL"


class LT(BinOp):
    def __init__(self, left, right):
        self.sign = "<"
        super(LT, self).__init__(left, right, NumberOps[self.sign], self.sign)


    def typed(self):
        return "BOOL"


class GE(BinOp):
    def __init__(self, left, right):
        self.sign = ">="
        super(GE, self).__init__(left, right, NumberOps[self.sign], self.sign)

    def typed(self):
        return "BOOL"


class LE(BinOp):
    def __init__(self, left, right):
        self.sign = "<="
        super(LE, self).__init__(left, right, NumberOps[self.sign], self.sign)

    def typed(self):
        return "BOOL"


class IS(BinOp):
    def __init__(self, left, right):
        self.sign = "=="
        super(IS, self).__init__(left, right, NumberOps[self.sign], self.sign)

    def typed(self):
        return "BOOL"


class AND(BinOp):
    def __init__(self, left, right):
        self.sign = "&&"
        super(AND, self).__init__(left, right, LopOp[self.sign], self.sign)

    def typed(self):
        return "BOOL"


class OR(BinOp):
    def __init__(self, left, right):
        self.sign = "||"
        super(OR, self).__init__(left, right, LopOp[self.sign], self.sign)

    def typed(self):
        return "BOOL"


class Divide(BinOp):
    def __init__(self, left, right):
        self.sign = "/"
        super(Divide, self).__init__(left, right, NumberOps[self.sign], self.sign)

    def opt(self):
        left = self.left.opt()
        right = self.right.opt()
        if type(right) is Constant:
            if right.value == 1:
                return left
            elif right.value == 2:
                sign = "*"
                const = Constant.acquire(0.5, MyLexer.reserved["DOUBLE"])
                return BinOpReversable.acquire(left, const, sign)
        return self.opt_const()

    def typed(self):
        return "NUMBER"


class Power(BinOp):
    def __init__(self, left, right):
        self.sign = "**"
        super(Power, self).__init__(left, right, NumberOps[self.sign], self.sign)

    def opt(self):
        left = self.left.opt()
        right = self.right.opt()
        if type(right) is Constant:
            if right.value == 2:
                sign = "*"
                return BinOpReversable.acquire(left, left, sign)
        return self.opt_const()

    def typed(self):
        return "NUMBER"


class BinOpReversable(BinOp):

    pool = {}

    @staticmethod
    def clean_up():
        BinOpReversable.pool = {}

    def __init__(self, left, right, op, op_sign):
        super(BinOpReversable, self).__init__(left, right, op, op_sign)

    def __hash__(self):
        return hash(self.left) + hash(self.right)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and (
            (self.left == other.left and self.right == other.right)
            or (self.left == other.right and self.right == other.left)
        )

    @staticmethod
    def acquire(left, right, op_sign):
        t = (left, right, op_sign)
        tr = (right, left, op_sign)

        if t not in BinOp.pool.keys():
            if tr in BinOp.pool.keys():
                return BinOp.pool[tr]

            operation = BinOp.define_operation(left, right, op_sign)

            operation = operation.opt()

            BinOp.pool[t] = operation

        return BinOp.pool[t]


class Addition(BinOpReversable):
    def __init__(self, left, right):
        self.sign = "+"
        super(Addition, self).__init__(left, right, NumberOps[self.sign], self.sign)

    def opt(self):
        left = self.left.opt()
        right = self.right.opt()
        if type(left) is Constant and left.value == 0:
            return right
        elif type(right) is Constant and right.value == 0:
            return left
        return self.opt_const()


class Mult(BinOpReversable):
    def __init__(self, left, right):
        self.sign = "*"
        super(Mult, self).__init__(left, right, NumberOps[self.sign], self.sign)

    def opt(self):
        left = self.left.opt()
        right = self.right.opt()
        if type(left) is Constant:
            if left.value == 1:
                return right
            elif left.value == 2:
                sign = "+"
                return BinOpReversable.acquire(right, right, sign)
        elif type(right) is Constant:
            if right.value == 1:
                return left
            elif right.value == 2:
                sign = "+"
                return BinOpReversable.acquire(left, left, sign)
        return self.opt_const()

    def typed(self):
        return "NUMBER"


class Constant(Expr):

    pool = {}

    @staticmethod
    def clean_up():
        Constant.pool = {}

    def __init__(self, value, type_of):
        # self.type = "const"
        self.value = value
        self.type = type_of

    def eval(self, scope=None):
        return (self.type, self.value)

    def plot(self, G):
        G.add_node(self, desc=self.value, type_of=self.type)

    def to_string(self):
        return Constant.acquire(str(self.value), MyLexer.reserved["STRING"])

    def to_bool(self):
        return Constant.acquire(bool(self.value), MyLexer.reserved["BOOL"])

    def to_float(self):
        return Constant.acquire(float(self.value), MyLexer.reserved["DOUBLE"])

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.value == other.value

    @staticmethod
    def acquire(value, type_of):
        t = (type_of, value)
        if t not in Constant.pool.keys():
            Constant.pool[t] = Constant(value, type_of)
        return Constant.pool[t]

    def opt(self):
        return self

    def depends_on(self):
        return set()

    def typed(self):
        return self.type


class ForLoop(Expr):
    def __init__(self, set_var, cond, expr, code):
        self.type = "loop"
        self.set = set_var
        self.cond = cond
        self.expr = expr
        self.body = code
        self.before = {}
        self.variables_changed = self.body.variables_changed.union(
            self.set.depends_on()
        )
        self.hoist_code()

    def hoist_code(self):
        seed = "sweetnight"
        counter = 0
        for line in self.body.code:
            if (
                isinstance(line, VariableInit) or isinstance(line, VariableRedef)
            ) and self.variables_changed.isdisjoint(line.depends_on()):
                expr = line.value
                var_name = seed + str(counter)
                self.before[var_name] = expr
                line.value = VariableCall.acquire(var_name)
                counter += 1

    def init_hoisted(self, scope):
        for k, v in self.before.items():
            typed, value = v.eval(scope)
            const = Constant.acquire(value, typed)
            VariableInit(k, const, typed).eval(scope)

    def plot(self, G):
        G.add_node(self, type=self.type)
        self.set.plot(G)
        self.cond.plot(G)
        self.expr.plot(G)
        self.body.plot(G)
        G.add_edge(self, self.set, desc="set")
        G.add_edge(self, self.cond, desc="cond")
        G.add_edge(self, self.expr, desc="expr")
        G.add_edge(self, self.body, desc="code")

    def eval(self, scope=None):
        scope.push_layer()
        self.init_hoisted(scope)
        scope.push_layer()
        self.set.eval(scope)
        ret = ()

        while self.cond.eval(scope) == ("BOOL", True):
            ret = self.body.eval_in_scope(scope)

            if ret != ():
                type_of, _ = ret

                if type_of == MyLexer.reserved["RETURN"]:
                    break
                else:
                    ret = ()
            self.expr.eval(scope)

        scope.pop_layer()
        scope.pop_layer()

        return ret

    def opt(self):
        return self


class VariableInit(Expr):
    def __init__(self, variable, value, type_of):
        self.variable = variable
        self.value = value
        self.type_of = type_of

    def eval(self, scope):

        (v_type, v_value) = self.value.eval(scope)

        if v_type != self.type_of:
            if self.type_of == MyLexer.reserved["DOUBLE"]:
                v_value = float(v_value)
            elif self.type_of == MyLexer.reserved["STRING"]:
                v_value = str(v_value)
            elif self.type_of == MyLexer.reserved["BOOL"]:
                v_value = bool(v_value)

        scope.put_local(self.variable, v_value, self.type_of)
        return ()  # Scala easter egg

    def plot(self, G):
        G.add_node(self, desc="init", type=self.type_of)
        G.add_node(self.variable, desc=self.variable)
        G.add_edge(self, self.variable)
        G.add_edge(self, self.value)
        self.value.plot(G)

    def __hash__(self):
        return hash(self.value) + hash(self.variable) + hash(self.type_of)

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__
            and self.value == other.value
            and self.type_of == self.type_of
        )

    def opt(self):
        #scope.put_local(self.variable, self.value, self.type_of)
        return self

    def depends_on(self):
        return self.value.depends_on()


class GlobVariableInit(VariableInit):
    def __init__(self, variable, value, type_of):
        super(GlobVariableInit, self).__init__(variable, value, type_of)

    def eval(self, scope):
        (v_type, v_value) = self.value.eval(scope)

        if v_type != self.type_of:
            if self.type_of == MyLexer.reserved["DOUBLE"]:
                v_value = float(v_value)
            elif self.type_of == MyLexer.reserved["STRING"]:
                v_value = str(v_value)
            elif self.type_of == MyLexer.reserved["BOOL"]:
                v_value = bool(v_value)

        scope.put_global(self.variable, v_value, self.type_of)
        return ()  # Scala easter egg


class FunctionInit(Expr):
    def __init__(self, f_type, args, func_name, body):
        self.args = args
        self.func_name = func_name
        self.code = body
        self.type = f_type

    def plot(self, G):
        G.add_node(
            self, desc="func_init", name=self.func_name, type=self.type, args=self.args
        )
        # G.add_edge(self, self.args)
        G.add_edge(self, self.code)
        self.code.plot(G)

    def eval(self, scope):
        scope.put_func(self.type, self.func_name, self.args, self.code)
        return ()

    def opt(self):
        return self


class VariableRedef(Expr):
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value

    def eval(self, scope):
        return scope.redef_var(self.variable, self.value.eval(scope))

    def opt(self):
        # scope.put_local(self.variable, self.value, self.type_of)
        return self

    def plot(self, G):
        G.add_node(self, desc="redef")
        G.add_edge(self, self.variable)
        G.add_edge(self, self.value)
        self.value.plot(G)

    def depends_on(self):
        return self.value.depends_on()

    def typed(self):
        return self.value.typed()


class VariableCall(Expr):

    pool = {}

    def __init__(self, variable, type_of=None):
        self.variable = variable
        self.type_of = type_of

    def eval(self, scope):
        return scope.get(self.variable, self.type_of)

    def plot(self, G):
        G.add_node(self, desc=self.variable, type=self.type_of)

    def __hash__(self):
        return hash(self.variable) + hash(self.type_of)

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__
            and self.variable == other.variable
            and self.type_of == self.type_of
        )

    @staticmethod
    def acquire(variable, type_of=None):
        t = (variable, type_of)

        if t not in VariableCall.pool.keys():
            VariableCall.pool[t] = VariableCall(variable, type_of=type_of)

        return VariableCall.pool[t]

    def opt(self):
        return self

    def depends_on(self):
        return {self.variable}

    def typed(self):
        return None


class FunctionCall(Expr):
    def __init__(self, fun_name, args):
        self.fun_name = fun_name
        self.args = args

    def eval(self, scope):
        f_type, args, fun = scope.get_func(self.fun_name)

        if len(args) != len(self.args):
            raise Exception(
                f"Invalid args [{len(self.args)}] in {self.fun_name} invocation. Expected [{len(args)}] arguments"
            )

        scope.push_layer()

        for (n, v) in zip(args, self.args):
            (v_type, v_name) = n
            (vv_type, vv_value) = v.eval(scope)

            if v_type != vv_type:
                raise Exception(
                    f"Function {self.fun_name} arg {v_name} wrong type. Expected {v_type}, got {vv_type}"
                )

            scope.put_local(v_name, vv_value, v_type)

        ret = fun.eval_in_scope(scope)

        type_of, _ = ret
        if type_of == MyLexer.reserved["RETURN"]:
            _, ret = ret
        scope.pop_layer()
        ret_type, ret_value = ret


        if ret_type != f_type:
            raise Exception(
                f"Function {self.fun_name} has been implemented wrong. Should return {f_type} instead of {ret_type}"
            )
        return (ret_type, ret_value)

    def plot(self, G):
        pass

    def opt(self):
        return self

    def depends_on(self):
        return {v.depends_on() for v in self.args}


class IfElse(Expr):
    def __init__(self, cond, if_block, else_block=None):
        self.cond = cond
        self.if_block = if_block
        self.else_block = else_block

    def eval(self, scope):

        ret_type, ret_val = self.cond.eval(scope)

        if ret_type != MyLexer.reserved["BOOL"]:
            raise Exception("xddddddddd12")

        if ret_val:
            return self.if_block.eval(scope)

        return self.else_block.eval(scope) if self.else_block else ()

    def plot(self, G):
        G.add_node(self, desc="ifelse")
        G.add_edge(self, self.cond, desc="cond")
        G.add_edge(self, self.if_block, desc="if_block")
        self.cond.plot(G)
        self.if_block.plot(G)

        if self.else_block != None:
            G.add_edge(self, self.else_block, desc="else_block")
            self.else_block.plot(G)

    def opt(self):
        if type(self.cond) is Constant:
            if self.cond.value is True:
                self.if_block = self.if_block.opt()
                return self.if_block
            elif self.cond.value is False:
                self.else_block = self.else_block.opt()
                return self.else_block
        return self


class Scope(object):
    def __init__(self):
        self.stack = []
        self.func_scope = {}

    def push_layer(self):
        self.stack.append({})

    def pop_layer(self):
        self.stack.pop()

    def put_func(self, f_type, func_name, args, func_body):
        for l in self.stack:
            for variable in l:
                if func_name == variable:
                    raise Exception(f"Function name {func_name} is taken by variable")
        for fun_n in self.func_scope:
            if fun_n == func_name:
                raise Exception(
                    f"Function name {func_name} is taken by another function"
                )

        print(f"created function {func_name} typed {f_type}")

        self.func_scope[func_name] = (f_type, args, func_body)

    def get_func(self, func_name):
        return self.func_scope[func_name]

    def get(self, variable, call_type):
        for l in reversed(self.stack):
            if variable in l:
                value, typed = l[variable]
                if call_type is not None and typed != call_type:
                    raise Exception(
                        f"Variable {variable} of type {typed} can not be assigned to {call_type} typed value!"
                    )
                return (typed, value)

        raise Exception(f"Variable {variable} has not been initialized!")

    def put_local(self, variable, value, type_of):
        if variable in self.stack[-1]:
            raise Exception(f"Variable {variable} has already been initialized!")
        self.stack[-1][variable] = (value, type_of)

    def put_global(self, variable, value, type_of):
        if variable in self.stack[0]:
            raise Exception(f"Variable {variable} has already been initialized!")
        self.stack[0][variable] = (value, type_of)

    def redef_var(self, variable, value):
        (v_type, v_value) = value
        for l in reversed(self.stack):
            if variable in l:
                _, temptype = l[variable]
                if temptype != v_type:
                    raise Exception(
                        f"Variable {variable} of type {temptype} can not be assigned to {v_type} typed value!"
                    )

                l[variable] = (v_value, v_type)
                return ()

        raise Exception(f"Variable {variable} has not been initialized!")

    def _print(self):
        for l in self.stack:
            print(l)


UnaryOps = {
    "cos": lambda x: math.cos(x),
    "sin": lambda x: math.sin(x),
    "tg": lambda x: math.tan(x),
    "ctg": lambda x: 1 / math.tan(x),
    "exp": lambda x: math.exp(x),
    "log": lambda x: math.log(x),
    "abs": lambda x: math.fabs(x),
    "-": lambda x: -x,
    "tostr": lambda x: str(x),
    "tonumb": lambda x: float(x),
    "tobool": lambda x: bool(x)
}

NumberOps = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "/": lambda x, y: x / y,
    "%": lambda x, y: x % y,
    "*": lambda x, y: x * y,
    "**": lambda x, y: x ** y,
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
        ("left", "BIN_OP_1", "SEMI", "MINUS"),
        ("right", "POWER"),
        ("right", "UMINUS"),
    )

    def p_error(self, p):
        print(f"Syntax error: {p.value}")

    def p_root_block(self, p):
        """root : LCPAREN block RCPAREN
        """
        p[0] = p[2]

    def p_block_line(self, p):
        """block : block SEMI line
        """
        p[0] = p[1] + p[3]

    def p_expr_binop(self, p):
        """expr : expr BIN_OP_1 expr
                | expr BIN_OP_2 expr
                | expr POWER expr
                | expr MINUS expr
        """

        if p[2] in ["+", "*"]:
            p[0] = BinOpReversable.acquire(p[1], p[3], p[2])
        else:
            p[0] = BinOp.acquire(p[1], p[3], p[2])

    def p_block_is_line(self, p):
        """block : line
        """
        p[0] = p[1]

    def p_line_name(self, p):
        """line : NAME
        """
        p[0] = [VariableCall.acquire(p[1])]

    def p_line_is(self, p):
        """line : call_fun
                | expr
                | assign
                | for
                | ifelse
                | def_fun
        """
        p[0] = [p[1]]

    def p_line_return(self, p):
        """line : RETURN call_fun
                | RETURN expr
        """
        p[0] = [(MyLexer.reserved["RETURN"], p[2])]

    def p_func_call(self, p):
        """ call_fun : NAME LPAREN arg_list RPAREN  
        """

        p[0] = FunctionCall(p[1], p[3])

    def p_func_call_empty(self, p):
        """ call_fun : NAME LPAREN RPAREN  
        """

        p[0] = FunctionCall(p[1], [])

    def p_for_loop(self, p):
        """for : FOR LPAREN assign SEMI expr SEMI assign RPAREN LCPAREN block RCPAREN
        """
        p[0] = ForLoop(p[3], p[5], p[7], Root(p[10]))

    def p_expr_name_call(self, p):
        """expr : NAME          
        """
        p[0] = VariableCall.acquire(p[1])

    def p_expr_func_call(self, p):
        """ expr : NAME LPAREN arg_list RPAREN  
                 | NAME LPAREN RPAREN
        """
        args = []

        if isinstance(p[3], list):
            args = p[3]

        p[0] = FunctionCall(p[1], args)

    def p_if_block(self, p):
        """ ifelse : IF LPAREN expr RPAREN LCPAREN block RCPAREN
        """
        p[0] = IfElse(p[3], Root(p[6]))

    def p_if_else_block(self, p):
        """ ifelse : IF LPAREN expr RPAREN LCPAREN block RCPAREN ELSE LCPAREN block RCPAREN 
        """
        p[0] = IfElse(p[3], Root(p[6]), Root(p[10]))

    def p_if_line(self, p):
        """ ifelse : IF LPAREN expr RPAREN line
        """
        p[0] = IfElse(p[3], Root(p[5]))

    def p_type(self, p):
        """ type : BOOL
                 | STRING_T
                 | NUMBER
        """
        p[0] = p[1]

    def p_func(self, p):
        """ def_fun : DEF type NAME LPAREN var_list RPAREN LCPAREN block RCPAREN
                    | DEF type NAME LPAREN RPAREN LCPAREN block RCPAREN                   
        """

        f_type = MyLexer.reserved[p[2]]

        args = []

        if isinstance(p[5], list):
            args = p[5]

        block = []

        if isinstance(p[7], list):
            block = p[7]
        else:
            block = p[8]

        p[0] = FunctionInit(f_type, args, p[3], Root(block))

    def p_arg_list(self, p):
        """ arg_list : arg_list COMA expr
        """
        p[0] = p[1] + [p[3]]

    def p_arg_list_end(self, p):
        """ arg_list : expr
        """
        p[0] = [p[1]]

    def p_var_list(self, p):
        """ var_list : var_list COMA type NAME
        """
        p[0] = p[1] + [(MyLexer.reserved[p[3]], p[4])]

    def p_var_list_end(self, p):
        """ var_list : type NAME
        """
        p[0] = [(MyLexer.reserved[p[1]], p[2])]

    def p_if_else_line(self, p):
        """ ifelse : IF LPAREN expr RPAREN line ELSE line 
        """
        p[0] = IfElse(p[3], Root(p[5]), Root(p[7]))

    def p_assign_expr(self, p):
        """assign : type NAME IS expr
                  | GLOBAL type NAME IS expr
        """

        if p[1] == MyLexer.reserved["GLOBAL"]:
            p[0] = GlobVariableInit(p[3], p[5], MyLexer.reserved[p[2]])
        else:
            p[0] = VariableInit(p[2], p[4], MyLexer.reserved[p[1]])

    def p_override_expr(self, p):
        """assign : NAME IS expr
        """
        p[0] = VariableRedef(p[1], p[3])

    def p_expr_2_str(self, p):
        """expr : STRING  
        """
        p[0] = Constant.acquire(p[1][1:-1], MyLexer.reserved["STRING"])

    def p_cond_2_bool(self, p):
        """ expr : BOOL    
        """
        p[0] = Constant.acquire(p[1], MyLexer.reserved["BOOL"])

    def p_cond_binop(self, p):
        """ expr : expr LOG_OP expr   
        """
        p[0] = BinOpReversable.acquire(p[1], p[3], p[2])

    def p_cond_rel(self, p):
        """ expr : expr COND_OP expr   
        """
        if p[2] in ["=="]:
            p[0] = BinOpReversable.acquire(p[1], p[3], p[2])
        else:
            p[0] = BinOp.acquire(p[1], p[3], p[2])

    def p_root_line(self, p):
        """root : line     
        """
        p[0] = p[1]

    def p_root_block_non(self, p):
        """root : block     
        """
        p[0] = p[1]

    def p_expr_paren(self, p):
        """expr : LPAREN expr RPAREN          
        """
        p[0] = p[2]

    def p_expr_unary(self, p):
        """expr : UNARY expr 
        """
        sign = p[1]
        p[0] = UnaryOp.acquire(p[2], sign)

    def p_expr_unary_paren(self, p):
        """expr : MINUS LPAREN expr RPAREN
        """
        sign = p[1]
        p[0] = UnaryOp(p[3], sign)

    def p_expr_2_numb(self, p):
        """expr : numb
        """
        p[0] = p[1]

    def p_expr_unary_minus(self, p):
        """expr : MINUS FLOAT %prec UMINUS
                | MINUS INT %prec UMINUS
        """
        p[0] = Constant.acquire(-p[2], MyLexer.reserved["DOUBLE"])

    def p_expr_unary_minus_name(self, p):
        """expr : MINUS NAME %prec UMINUS
        """
        p[0] = UnaryOp.acquire(VariableCall.acquire(p[2]), p[1])

    def p_numb_2_float_int(self, p):
        """numb : INT
                | FLOAT           
        """
        p[0] = Constant.acquire(p[1], MyLexer.reserved["DOUBLE"])

    def parse(self, text):
        return self.parser.parse(text)

    def __init__(self):
        self.lexer = MyLexer()
        self.parser = yacc.yacc(module=self)



class RPNParser(MyParser):
    def p_expr_binop(self, p):
        """expr : expr expr BIN_OP_1
                | expr expr BIN_OP_2
                | expr expr POWER
                | expr expr MINUS
        """

        if p[3] in ["+", "*"]:
            p[0] = BinOpReversable.acquire(p[1], p[2], p[3])
        else:
            p[0] = BinOp.acquire(p[1], p[2], p[3])

    def p_expr_unary(self, p):
        """expr : expr UNARY 
        """
        sign = p[2]
        p[0] = UnaryOp.acquire(p[1], sign)


    def p_cond_binop(self, p):
        """ expr : expr expr LOG_OP   
        """
        p[0] = BinOpReversable.acquire(p[1], p[2], p[3])

    def p_cond_rel(self, p):
        """ expr : expr expr COND_OP   
        """
        if p[2] in ["=="]:
            p[0] = BinOpReversable.acquire(p[1], p[2], p[3])
        else:
            p[0] = BinOp.acquire(p[1], p[2], p[3])


if __name__ == "__main__":
    parser = MyParser()
    rpn = RPNParser()
    current = parser
    context = Root()
    plot = False

    def getline(prompt):
        return input(prompt)

    while True:
        code = ""
        lastchar = "/"

        line = getline(">> ")

        while line[-1] == "/":
            code += line[:-1] + "; "
            line = getline("> ")

        if line == "PLOT ON":
            plot = True
        elif line == "PLOT OFF":
            plot = False
        elif line == "SWITCH RPN":
            current = rpn
        elif line == "SWITCH NORMAL":
            current = parser
        else:
            code += line
            context.code = current.parse(code)

            if plot:
                context.plot_init()

            print(context.eval_in_scope())
