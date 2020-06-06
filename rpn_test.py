import unittest
from myparser import RPNParser, Root, Constant, BinOp, BinOpReversable, VariableCall
from mylexer import MyLexer


class TestRPNParser(unittest.TestCase):
    def setUp(self):
        self.parser = RPNParser()
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
            "1 1 +": ("NUMBER", 2),
            "1 1 -": ("NUMBER", 0),
            "1 -1 +": ("NUMBER", 0),
            "123 321 +": ("NUMBER", 444),
            "0.5 0.5 -": ("NUMBER", 0),
            "1.67 4 +": ("NUMBER", 5.67),
            "10 1 /": ("NUMBER", 10),
            "10 10 /": ("NUMBER", 1),
            "1 10 /": ("NUMBER", 0.1),
            "151 2 /": ("NUMBER", 75.5),
            "3 2 *": ("NUMBER", 6),
            "0 5 *": ("NUMBER", 0),
            "-5 * 0 ": ("NUMBER", 0),
            "1 1 1 + +": ("NUMBER", 3),
            "1 1 1 - +": ("NUMBER", 1),
            "2 2 / 1 +": ("NUMBER", 2),
            "5 -2 *": ("NUMBER", -10),
            "13 -2 *": ("NUMBER", -26),
            "2 2 **": ("NUMBER", 4),
            "10 -1 **": ("NUMBER", 0.1),
        }

        self.run_tests_is(tests)

    def test_special_func(self):
        tests = {
            "0 cos": ("NUMBER", 1),
            "0 sin": ("NUMBER", 0),
            "3.141592653589 cos": ("NUMBER", -1),
            "3.141592653589 sin ": ("NUMBER", 0),
            "2 3.141592653589 * sin": ("NUMBER", 0),
            "2 3.141592653589 * cos": ("NUMBER", 1),
            "3.141592653589 6 / sin": ("NUMBER", 0.5),
            "3.141592653589 2 / sin": ("NUMBER", 1),
            "3.141592653589 3 / cos": ("NUMBER", 0.5),
            "3.141592653589 2 / cos": ("NUMBER", 0),
        }

        self.run_tests_almost(tests)

    def test_log(self):
        tests = {
            "True True &&": ("BOOL", True),
            "True False &&": ("BOOL", False),
            "False False &&": ("BOOL", False),
            "True True ||": ("BOOL", True),
            "True False ||": ("BOOL", True),
            "False False ||": ("BOOL", False),
        }

        self.run_tests_is(tests)

    def test_rel(self):
        tests = {
            "10 10 >": ("BOOL", False),
            "10 1 >=": ("BOOL", True),
            "10 1 <=": ("BOOL", False),
            "0.5 1 <": ("BOOL", True),
            "0.5 0.25 >": ("BOOL", True),
        }

        self.run_tests_is(tests)

    def test_conversion(self):
        tests = {
            '"michal" 12 +': ("STRING_T", "michal12"),
            '12 "2" +': ("NUMBER", 14),
            "1 True + ": ("NUMBER", 2),
            "True 0 &&": ("BOOL", False),
        }

        self.run_tests_is(tests)


    def test_multiple_lines(self):
        tests = {
            "10 12 +; 10 1 -": ("NUMBER", 9),
            "{10 12 +; 10 1 -}": ("NUMBER", 9),
        }

        self.run_tests_is(tests)

    def test_if_else(self):
        tests = {
            "IF (True) { 10 } ELSE { 11 }": ("NUMBER", 10),
            "IF (False) { 10 } ELSE { 11 } ": ("NUMBER", 11),
        }

        self.run_tests_is(tests)

    def test_for(self):

        text = "INT a = 0 ; FOR (INT i = 0 ; i 4 < ; i = i 1 +) { a = a i + }"

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

    def test_type_control(self):

        text = 'INT a = 0 ; STRING b = "test" ; DOUBLE c = a b +'

        scope = Root()
        scope.code = self.parser.parse(text)

        self.assertRaises(Exception, scope.eval_in_scope)

    def test_overload_ops(self):
        tests = {
            '"123" "1" +': ("STRING_T", "1231"),
            '"test" " " "test1" " 1231" + + +': ("STRING_T", "test test1 1231"),
        }

        self.run_tests_is(tests)

    def test_variable_assign(self):

        text = 'INT a = 123123 ; a = 123 123 + ; STRING s = "" ; s = "sweetnight" " " "to znaczy slodka noc" + +'

        scope = Root()
        scope.code = self.parser.parse(text)
        scope.eval_in_scope()

        self.eval_in_scope(scope, "a", ("NUMBER", 246))
        self.eval_in_scope(scope, "s", ("STRING_T", "sweetnight to znaczy slodka noc"))

    def test_global(self):

        text = "INT i = 0 ; FOR (INT i = 0 ; i 4 < ; i = i 1 +) { i = i i +}"

        scope = Root(code=self.parser.parse(text))
        scope.eval_in_scope()

        scope.code = self.parser.parse("i")
        evaluated = scope.eval_in_scope()

        self.assertEqual(evaluated, ("NUMBER", 0))

        text = "{ GLOBAL INT x = 2138 }"

        scope = Root(code=self.parser.parse(text))
        scope.eval_in_scope()

        scope.code = self.parser.parse("x")
        evaluated = scope.eval_in_scope()

        self.assertEqual(evaluated, ("NUMBER", 2138))

        text = "DEF STRING fun1( INT i , STRING s ) { s i + }"

        scope = Root()
        scope.code = self.parser.parse(text)
        scope.eval_in_scope()

        scope.code = self.parser.parse('fun1(1 , "halo" )')

        evaluated = scope.eval_in_scope()

        self.assertEqual(evaluated, ("STRING_T", "halo1"))

    def parse_2(self, text_dict):

        for k, v in text_dict.items():
            code1 = self.parser.parse(k)
            code2 = self.parser.parse(v)
            self.assertEqual(code1, code2)

    def test_algebra_opt(self):

        test = {
            "x 0 +": "x",
            "0 x +": "x",
            "x 2 **": "x x *",
            "x 1 /": "x",
            "x 2 /": "x 0.5 *",
            "x 2 *": "x x +",
        }

        self.parse_2(test)

    def test_reverse_opt(self):

        test = {"a b *": "b a *", "a b +": "b a +"}

        self.parse_2(test)

    def test_constant_opt(self):

        test = {
            "2 3 *": "6",
            "1 2 3 + +": "6",
            "2 3 4 * +": "14",
            "12 5 -  2 * 3 +": "17",
            '"michal " "dygas" +': '"michal dygas"',
        }

        self.parse_2(test)

    def test_nested(self):

        text = "DEF INT fun1(INT i) { i }; DEF INT fun2(INT i ) { 1 fun1(1) + }; DEF INT fun3(INT i) { i 1 - }"

        scope = Root()
        scope.code = self.parser.parse(text)
        scope.eval_in_scope()

        self.eval_in_scope(scope, "fun1(1)", ("NUMBER", 1))
        self.eval_in_scope(scope, "fun2(1)", ("NUMBER", 2))
        self.eval_in_scope(scope, "fun3(fun1(2))", ("NUMBER", 1))

    def test_hoist(self):
        text1 = "INT x = 12; INT z = 0; INT y = 1; FOR(INT i = 0 ; i 2 < ; i = i 1 + ) { z = x y + } "
        text2 = "x y +"

        for_loop = self.parser.parse(text1)
        expr = self.parser.parse(text2)

        self.assertTrue(expr[0] in for_loop[-1].before.values())

        scope = Root(code=for_loop)
        scope.eval_in_scope()
        self.eval_in_scope(scope, "z", ("NUMBER", 13))


    def test_expilcit_conversion(self):
        tests = {
            "1 toStr": ("STRING_T", "1"),
            '15 toStr "michal" +': ("STRING_T", "15michal"),
            "True toNumb 21 +": ("NUMBER", 22),
            "23 5 * 2 + toStr": ("STRING_T", "117")
        }

        self.run_tests_is(tests)


if __name__ == "__main__":
    unittest.main()
