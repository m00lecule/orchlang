import unittest
from myparser import MyParser, Root, Constant, BinOp, BinOpReversable, VariableCall
from mylexer import MyLexer


parser = MyParser()

scope = Root()
scope.code = parser.parse("-5")

# scope.plot_init()
print(scope.eval_in_scope()[-1])

# context = Root()


# # print(parser.parse(code))
#         context.code = parser.parse(code)

#         context.init_opt()
#         context.plot_init()

#         print(context.eval_in_scope())


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = MyParser()
        Constant.clean_up()
        BinOp.clean_up()
        BinOpReversable.clean_up()

    def run_tests_almost(self, tests):
        [self.check_in_scope_f(k, v) for k, v in tests.items()]

    def run_tests_is(self, tests):
        [self.check_in_scope_i(k, v) for k, v in tests.items()]

    def check_in_scope_f(self, text, value):

        error = 1e-5

        scope = Root()
        scope.code = self.parser.parse(text)

        ret_type, ret_val = scope.eval_in_scope()

        v_type, v_val = value

        self.assertEqual(ret_type, v_type)
        self.assertTrue(abs(ret_val - v_val) < error)

    def check_in_scope_i(self, text, value):
        scope = Root()
        scope.code = self.parser.parse(text)

        evaluated = scope.eval_in_scope()

        if not isinstance(value, list):
            evaluated = evaluated

        self.assertEqual(evaluated, value)

    def test_binop_number(self):
        tests = {
            "1 + 1": ("NUMBER", 2),
            "1 - 1": ("NUMBER", 0),
            "-1 + 1": ("NUMBER", 0),
            "123 + 321": ("NUMBER", 444),
            "0.5 - 0.5": ("NUMBER", 0),
            "1.67 + 4": ("NUMBER", 5.67),
            "10 / 1": ("NUMBER", 10),
            "10 / 10": ("NUMBER", 1),
            "1 / 10": ("NUMBER", 0.1),
            "151 / 2": ("NUMBER", 75.5),
            "3 * 2": ("NUMBER", 6),
            "0 * 5": ("NUMBER", 0),
            "-5 * 0 ": ("NUMBER", 0),
            "1 + 1 + 1": ("NUMBER", 3),
            "1 - 1 + 1": ("NUMBER", 1),
            "2 * 3 + 2": ("NUMBER", 8),
            "2 / 2 + 1": ("NUMBER", 2),
            "2 + 2 * 3": ("NUMBER", 8),
            "-5 * 2": ("NUMBER", -10),
            "-5 * -2": ("NUMBER", 10),
            "-(5 * 2)": ("NUMBER", -10),
            "5 * (-10)": ("NUMBER", -50),
            "13 * -2": ("NUMBER", -26),
            "2 ** 2": ("NUMBER", 4),
            "10 ** -1": ("NUMBER", 0.1),
        }

        self.run_tests_is(tests)

    def test_special_func(self):
        tests = {
            "cos 0": ("NUMBER", 1),
            "sin 0": ("NUMBER", 0),
            "cos 3.141592653589": ("NUMBER", -1),
            "sin 3.141592653589": ("NUMBER", 0),
            "sin 2*3.141592653589": ("NUMBER", 0),
            "cos 2*3.141592653589": ("NUMBER", 1),
            "sin 3.141592653589/6": ("NUMBER", 0.5),
            "sin 3.141592653589/2": ("NUMBER", 1),
            "cos 3.141592653589/3": ("NUMBER", 0.5),
            "cos 3.141592653589/2": ("NUMBER", 0),
        }

        self.run_tests_almost(tests)

    def test_log(self):
        tests = {
            "True && True": ("BOOL", True),
            "True && False": ("BOOL", False),
            "False && False": ("BOOL", False),
            "True || True": ("BOOL", True),
            "True || False": ("BOOL", True),
            "False || False": ("BOOL", False),
        }

        self.run_tests_is(tests)

    def test_rel(self):
        tests = {
            "10 > 10": ("BOOL", False),
            "-10 > -10": ("BOOL", False),
            "10 >= 1": ("BOOL", True),
            "10 <= 1": ("BOOL", False),
            "0.5 < 1": ("BOOL", True),
            "0.5 > 0.25": ("BOOL", True),
        }

        self.run_tests_is(tests)

    def test_conversion(self):
        tests = {
            '"michal" + 12': ("STRING_T", "michal12"),
            '12 + "2"': ("NUMBER", 14),
            "1 + True": ("NUMBER", 2),
            "True && 0": ("BOOL", False),
        }

        self.run_tests_is(tests)

    def test_unary_minus(self):
        tests = {
            "-(-10)": ("NUMBER", 10),
            "-10": ("NUMBER", -10),
            "-0": ("NUMBER", 0),
            "-(10)": ("NUMBER", -10),
            "12 + (-2)": ("NUMBER", 10),
        }

        self.run_tests_is(tests)

    def test_multiple_lines(self):
        tests = {
            "10 + 12; 10 - 1": ("NUMBER", 9),
            "{10 + 12; 10 - 1}": ("NUMBER", 9),
        }

        self.run_tests_is(tests)

    def test_if_else(self):
        tests = {
            "IF (True) { 10 } ELSE { 11 }": ("NUMBER", 10),
            "IF (False) { 10 } ELSE { 11 } ": ("NUMBER", 11),
        }

        self.run_tests_is(tests)

    def test_for(self):

        text = "INT a = 0 ; FOR (INT i = 0 ; i < 4 ; i = i + 1) { a = a + i }"

        scope = Root()
        scope.code = self.parser.parse(text)
        scope.eval_in_scope()

        scope.code = self.parser.parse("a")

        evaluated = scope.eval_in_scope()

        self.assertEqual(evaluated, ("NUMBER", 6))

    def eval_in_scope(self, scope, text, value):
        scope.code = self.parser.parse(text)
        evaluated = scope.eval_in_scope()
        self.assertEqual(evaluated, value)

    def test_variable_init(self):

        text = 'INT a = 0 ; STRING b = "test" ; DOUBLE c = 0.15 ; BOOL d = True'

        scope = Root()
        scope.code = self.parser.parse(text)
        scope.eval_in_scope()

        self.eval_in_scope(scope, "a", ("NUMBER", 0))
        self.eval_in_scope(scope, "b", ("STRING_T", "test"))
        self.eval_in_scope(scope, "c", ("NUMBER", 0.15))
        self.eval_in_scope(scope, "d", ("BOOL", True))

    def test_type_control(self):

        text = 'INT a = 0 ; STRING b = "test" ; DOUBLE c = a + b'

        scope = Root()
        scope.code = self.parser.parse(text)

        self.assertRaises(Exception, scope.eval_in_scope)

    def test_overload_ops(self):
        tests = {
            '"123" + "1"': ("STRING_T", "1231"),
            '"test" + " " + "test1" + " 1231"': ("STRING_T", "test test1 1231"),
        }

        self.run_tests_is(tests)

    def test_variable_assign(self):

        text = 'INT a = 123123 ; a = 123 + 123 ; STRING s = "" ; s = "sweetnight" + " " + "to znaczy slodka noc"'

        scope = Root()
        scope.code = self.parser.parse(text)
        scope.eval_in_scope()

        self.eval_in_scope(scope, "a", ("NUMBER", 246))
        self.eval_in_scope(scope, "s", ("STRING_T", "sweetnight to znaczy slodka noc"))

    def test_global(self):

        text = "INT i = 0 ; FOR (INT i = 0 ; i < 4 ; i = i + 1) { i = i + i }"

        scope = Root()
        scope.code = self.parser.parse(text)
        scope.eval_in_scope()

        scope.code = self.parser.parse("i")

        evaluated = scope.eval_in_scope()

        self.assertEqual(evaluated, ("NUMBER", 0))

        text = "{ GLOBAL INT x = 2138 }"

        scope = Root()
        scope.code = self.parser.parse(text)
        scope.eval_in_scope()

        scope.code = self.parser.parse("x")

        evaluated = scope.eval_in_scope()

        self.assertEqual(evaluated, ("NUMBER", 2138))

    def test_fn_definition(self):

        text = "DEF INT fun( INT i ) { i }"

        scope = Root()
        scope.code = self.parser.parse(text)
        scope.eval_in_scope()

        scope.code = self.parser.parse("fun(10)")

        evaluated = scope.eval_in_scope()

        self.assertEqual(evaluated, ("NUMBER", 10))

        text = "DEF STRING fun1( INT i , STRING s ) { s + i }"

        scope = Root()
        scope.code = self.parser.parse(text)
        scope.eval_in_scope()

        scope.code = self.parser.parse('fun1(1 , "halo" )')

        evaluated = scope.eval_in_scope()

        self.assertEqual(evaluated, ("STRING_T", "halo1"))

    def test_unnecessary(self):
        text1 = "{1; 2; 3; RETURN 4; 5}"
        text2 = "{1; 2; 3; RETURN 4}"

        scope1 = Root(code=self.parser.parse(text1))

        scope2 = Root(code=self.parser.parse(text2))

        self.assertEqual(scope1.code, scope2.code)

    def parse_2(self, text_dict):

        for k, v in text_dict.items():
            code1 = self.parser.parse(k)
            code2 = self.parser.parse(v)
            self.assertEqual(code1, code2)

    def test_algebra_opt(self):

        test = {
            "x + 0": "x",
            "0 + x": "x",
            "x ** 2": "x * x",
            "x / 1": "x",
            "x / 2": "x * 0.5",
            "x * 2": "x + x",
        }

        self.parse_2(test)

    def test_reverse_opt(self):

        test = {"a * b": "b * a", "a + b": "b + a"}

        self.parse_2(test)

    def test_constant_opt(self):

        test = {
            "2 * 3": "6",
            "1 + 2 + 3": "6",
            "2 + 3 * 4": "14",
            "(12 - 5) * 2 + 3": "17",
            '"michal " + "dygas"': '"michal dygas"',
        }

        self.parse_2(test)

    def test_nested(self):

        text = "DEF INT fun1(INT i) { i }; DEF INT fun2(INT i ) { 1 + fun1(1)}; DEF INT fun3(INT i) { i - 1 }"

        scope = Root()
        scope.code = self.parser.parse(text)
        scope.eval_in_scope()

        self.eval_in_scope(scope, "fun1(1)", ("NUMBER", 1))
        self.eval_in_scope(scope, "fun2(1)", ("NUMBER", 2))
        self.eval_in_scope(scope, "fun3(fun1(2))", ("NUMBER", 1))

    # var_call = VariableCall("x")
    # zero = Constant(0, MyLexer.reserved["DOUBLE"])
    # two = Constant(2, MyLexer.reserved["DOUBLE"])

    # text = "x + 0"
    # text_1 = "x"
    # code = self.parser.parse(text)
    # code1 = self.parser.parse(text_1)

    # self.assertEqual(code, code1)

    # test = {
    #     BinOpReversable.acquire(var_call, zero, "+"): var_call,
    #     BinOpReversable.acquire(zero, var_call, "+"): var_call,
    #     BinOp.acquire(var_call, zero, "-"): var_call,
    #     BinOpReversable.acquire(var_call, two, "**"): BinOpReversable.acquire(
    #         var_call, var_call, "*"
    #     ),
    # }

    # for k, v in test.items():
    #     self.assertEqual(k, v)

    # test = "{1; 2; 3; RETURN 4; 5}"

    # scope = Root(code=self.parser.parse(text))

    # numb_t = MyLexer.reserved["DOUBLE"]
    # self.assertEqual(
    #     scope.code,
    #     [
    #         Constant.acquire(1, numb_t),
    #         Constant.acquire(2, numb_t),
    #         Constant.acquire(3, numb_t),
    #         (MyLexer.reserved["RETURN"], Constant.acquire(4, numb_t)),
    #     ],
    # )
    # text = "{ GLOBAL INT x = 2138 }"

    # scope = Root()
    # scope.code = self.parser.parse(text)
    # scope.eval_in_scope()

    # scope.code = self.parser.parse("x")

    # evaluated = scope.eval_in_scope()

    # self.assertEqual(evaluated[0], ("NUMBER", 2138))

    # def test_rpn(self):
    #     tests = {"2 2 –": 0, "3 4 + 5 2 – *": 21}

    #     self.run_tests_is(tests)

    # self.assertEqual(self.lexer.parse_text("-3.1415 "), [("FLOAT", -3.1415)])
    # self.assertEqual(self.lexer.parse_text(" -3.1415"), [("FLOAT", -3.1415)])
    # self.assertEqual(self.lexer.parse_text("-3.1415"), [("FLOAT", -3.1415)])
    # self.assertEqual(self.lexer.parse_text(".00001"), [("FLOAT", 1e-05)])
    # self.assertEqual(self.lexer.parse_text("0.00001"), [("FLOAT", 1e-05)])

    # def test_int(self):
    #     self.assertEqual(self.lexer.parse_text(" 1"), [("INT", 1)])
    #     self.assertEqual(self.lexer.parse_text(" 1 "), [("INT", 1)])
    #     self.assertEqual(self.lexer.parse_text("1 "), [("INT", 1)])
    #     self.assertEqual(self.lexer.parse_text("1"), [("INT", 1)])
    #     self.assertEqual(self.lexer.parse_text("-5"), [("INT", -5)])
    #     self.assertEqual(self.lexer.parse_text("2137"), [("INT", 2137)])

    # def test_power(self):
    #     self.assertEqual(self.lexer.parse_text("1"), [("INT", 1)])
    #     self.assertEqual(self.lexer.parse_text("-5"), [("INT", -5)])
    #     self.assertEqual(self.lexer.parse_text("2137"), [("INT", 2137)])

    # def test_special_functions(self):
    #     self.assertEqual(self.lexer.parse_text("cos"), [("UNARY", "cos")])
    #     self.assertEqual(self.lexer.parse_text("Cos"), [("UNARY", "cos")])
    #     self.assertEqual(self.lexer.parse_text("Sin"), [("UNARY", "sin")])
    #     self.assertEqual(self.lexer.parse_text("tg"), [("UNARY", "tg")])
    #     self.assertEqual(self.lexer.parse_text("Ctg"), [("UNARY", "ctg")])
    #     self.assertEqual(self.lexer.parse_text("exp"), [("UNARY", "exp")])


if __name__ == "__main__":
    unittest.main()
