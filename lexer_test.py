import unittest
from mylexer import MyLexer


class TestLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = MyLexer()

    def run_tests(self, tests):
        [self.check(k, v) for k, v in tests.items()]

    def check(self, text, tokens):
        self.assertEqual(self.lexer.parse_text(text), tokens)

    def test_float(self):
        tests = {
            "-3.1415 ": [ ("FLOAT", -3.1415)],
            " -3.1415": [ ("FLOAT", -3.1415)],
            "-3.1415": [("FLOAT", -3.1415)],
            ".00001": [("FLOAT", 1e-05)],
            "0.00001": [("FLOAT", 1e-05)],
        }

        self.run_tests(tests)

    def test_int(self):
        tests = {
            " 1": [("INT", 1)],
            " 1 ": [("INT", 1)],
            "1 ": [("INT", 1)],
            "1": [("INT", 1)],
            "-5": [("INT", -5)],
            "2137": [("INT", 2137)],
        }

        self.run_tests(tests)

    def test_power(self):
        tests = {"**": [("POWER", "**")], "*": [("BIN_OP_1", "*")]}

        self.run_tests(tests)

    def test_special_fn(self):
        tests = {
            "sin": [("UNARY", "sin")],
            "SIN": [("UNARY", "sin")],
            "cos": [("UNARY", "cos")],
            "Cos": [("UNARY", "cos")],
            "Sin": [("UNARY", "sin")],
            "tg": [("UNARY", "tg")],
            "Ctg": [("UNARY", "ctg")],
            "exp": [("UNARY", "exp")],
        }

        self.run_tests(tests)


if __name__ == "__main__":
    unittest.main()
