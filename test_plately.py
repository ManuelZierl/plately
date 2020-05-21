import unittest

from plately import *


class TestIterators(unittest.TestCase):

    def test_identity(self):
        ident = identity("abc", container=None)
        self.assertEqual(next(ident), "abc")
        self.assertEqual(next(ident), "abc")
        self.assertEqual(next(ident), "abc")

        self.assertEqual(ident[12], "abc")
        self.assertEqual(ident[200], "abc")

        self.assertEqual(len(ident), 1)

    def test_iteration(self):
        it = iteration(1, 2, 3, container=None)
        self.assertEqual(next(it), 1)
        self.assertEqual(next(it), 2)
        self.assertEqual(next(it), 3)
        self.assertEqual(next(it), 1)

        self.assertEqual(it[0], "1")
        self.assertEqual(it[4], "2")

        self.assertEqual(len(it), 3)

    def test_random(self):
        ran = random("1", "2", "3", container=None)
        self.assertIn(next(ran), {"1", "2", "3"})
        self.assertIn(next(ran), {"1", "2", "3"})

        self.assertIn(ran[43], {"1", "2", "3"})

        self.assertEqual(len(ran), 1)

    def test_interval_iterator(self):
        ii = interval_iterator(1, 2, 3, interval=1, container=None)
        for x in [1, 2, 3, 1, 2, 3, 1, 2, 3]:
            self.assertEqual(next(ii), x)

        ii = interval_iterator(1, 2, 3, interval=2, container=None)
        for x in [1, 1, 2, 2, 3, 3, 1, 1, 2, 2]:
            self.assertEqual(next(ii), x)

        ii = interval_iterator(1, 2, 3, interval=3, container=None)
        for x in [1, 1, 1, 2, 2, 2, 3, 3, 3, 1, 1, 1, 2, 2, 2, 3, 3, 3, 1, 1, 1]:
            self.assertEqual(next(ii), x)

        ii = interval_iterator(1, 2, interval=2, container=None)

        self.assertEqual(ii[0], "1")
        self.assertEqual(ii[1], "1")
        self.assertEqual(ii[2], "2")
        self.assertEqual(ii[3], "2")
        self.assertEqual(ii[4], "1")
        self.assertEqual(ii[5], "1")
        self.assertEqual(ii[6], "2")
        self.assertEqual(ii[7], "2")
        self.assertEqual(ii[8], "1")

        self.assertEqual(len(ii), 4)

    def test_container(self):
        cont = Container()
        self.assertEqual(cont.elements, [])
        self.assertEqual(cont.variables, {})
        self.assertEqual(cont.counter, -1)
        self.assertEqual(cont.max, 0)

        cont = Container("a", iteration(1, 2, 3), "b")
        self.assertEqual(len(cont.elements), 3)
        self.assertTrue(all(isinstance(x, BaseIterator) for x in cont.elements))
        self.assertEqual(cont.variables, {})
        self.assertEqual(cont.counter, -1)
        self.assertEqual(cont.max, 3)

        cont = Container(iteration(1, 2, 3, container=None), "a", "b",
                         interval_iterator(1, 2, 3, interval=2, container=None), "c")
        self.assertEqual(len(cont.elements), 5)
        self.assertIsInstance(cont.elements[0], iteration)
        self.assertIsInstance(cont.elements[1], identity)
        self.assertIsInstance(cont.elements[2], identity)
        self.assertIsInstance(cont.elements[3], interval_iterator)
        self.assertIsInstance(cont.elements[4], identity)

        class Foo:
            pass

        f = Foo()
        with self.assertRaises(AssertionError):
            _ = Container(f, "str1")

        self.assertEqual(cont[0], "1ab1c")
        self.assertEqual(cont[1], "2ab1c")
        self.assertEqual(cont[2], "3ab2c")
        self.assertEqual(cont[3], "1ab2c")
        self.assertEqual(cont[4], "2ab3c")
        self.assertEqual(cont[5], "3ab3c")

        cont = Container(product(1, 2, 3), product(1, 2, 3))
        tmp = ["11", "12", "13", "21", "22", "23", "31", "32", "33"]
        for i, x in enumerate(cont):
            self.assertEqual(x, tmp[i])

    def test_variable(self):
        kwargs = {"var1": 1, "var2": 2}
        container = Container(elements=None, kwargs=kwargs)
        var = variable(container=container, name="var2", default="mises")
        self.assertEqual(next(var), "mises")
        self.assertEqual(next(var), "mises")
        self.assertEqual(next(var), "mises")

        self.assertEqual(var[32], "mises")
        self.assertEqual(var[42], "mises")

        self.assertEqual(len(var), 1)

    def test_product(self):
        # todo: ?
        pass

    def test_inifite_iteration(self):
        ii = infinte_iteration(start=0, step=5)
        self.assertEqual(next(ii), 0)
        self.assertEqual(next(ii), 5)
        self.assertEqual(next(ii), 10)
        self.assertEqual(ii[10], 50)


class TestBaseIterator(unittest.TestCase):
    def test_paste(self):
        self.assertEqual(BaseIterator.paste("1", "___"), "__1")
        self.assertEqual(BaseIterator.paste("abcd", "___"), "abcd")
        self.assertEqual(BaseIterator.paste("43", "_____"), "___43")
        self.assertEqual(BaseIterator.paste("43", ""), "43")


class TestParser(unittest.TestCase):

    def test_identity(self):
        x = Parser.parse("a{ b }c")
        self.assertEqual("abc", x[0])
        self.assertEqual("abc", x[1])

        # escaping
        self.assertEqual(Parser.parse("{ { }}")[0], "{}")
        self.assertEqual(Parser.parse("{ { }{ } }")[0], "{ }")
        self.assertEqual(Parser.parse("{ { }[1,2,3]}")[0], "{[1,2,3]}")

    def test_product(self):
        results = ["img_1_1.png", "img_1_2.png", "img_1_3.png", "img_2_1.png", "img_2_2.png", "img_2_3.png"]
        for i, result in enumerate(Parser.parse("img_{.1,2.}_{.1,2,3.}.png")):
            self.assertEqual(results[i], result)

    def test_iteration(self):
        results = ["img_a.png", "img_b.png", "img_c.png"]
        for i, result in enumerate(Parser.parse("img_{[a,b,c]}.png")):
            self.assertEqual(results[i], result)

    def test_variable(self):
        for result in Parser.parse("img_{(var1)}.png", {"var1": "13"}):
            self.assertEqual(result, "img_13.png")

        #default
        for result in Parser.parse("img_{(var1)}.png"):
            self.assertEqual(result, "img_.png")

        for result in Parser.parse("img_{(var|def)}.png"):
            self.assertEqual(result, "img_def.png")

    def test_ininite_iterator(self):
        for result in Parser.parse("{oo}"):
            self.assertEqual(result, "0")

    def test_variable_with_custom_default(self):
        for result in Parser.parse("img_{(var1,_)}.png", {"var1": "13"}):
            self.assertEqual("img_13.png", result)

        for result in Parser.parse("img_{(var1,_)}.png", {"var2": "13"}):
            self.assertEqual("img__.png", result)

    def test_split(self):
        parser = Parser()
        self.assertEqual(parser.split("abcdefghi", 3, 7), ['abc', 'defg', 'hi'])
        self.assertEqual(parser.split("abcdefghi", 0, 3), ['', 'abc', 'defghi'])

    def test_parse_element(self):
        parser = Parser()
        with self.assertRaises(AssertionError):
            parser.parse_element("rothbard")

        self.assertIsInstance(parser.parse_element("{ abc }"), identity)
        self.assertEqual(parser.parse_element("{ abc }").value, "abc")
        self.assertEqual(parser.parse_element("{ { }").value, "{")

        self.assertIsInstance(parser.parse_element("{.1,2.}"), product)
        self.assertEqual(parser.parse_element("{.1,2.}").values, ("1", "2"))

        self.assertIsInstance(parser.parse_element("{[3,4]}"), iteration)
        self.assertEqual(parser.parse_element("{[3,4]}").values, ("3", "4"))

        self.assertIsInstance(parser.parse_element("{(var1)}"), variable)
        self.assertIsInstance(parser.parse_element("{(var1;hayek)}"), variable)
        self.assertEqual(parser.parse_element("{(var1)}").name, "var1")
        self.assertEqual(parser.parse_element("{(var1)}").default, "")
        self.assertEqual(parser.parse_element("{(var1,hayek)}").name, "var1")
        self.assertEqual(parser.parse_element("{(var1,hayek)}").default, "hayek")

        self.assertIsInstance(parser.parse_element("{?a,b,c?}"), random)
        self.assertAlmostEqual(parser.parse_element("{?a,b,c?}").values, ("a", "b", "c"))

        self.assertIsInstance(parser.parse_element("{-1,2,3,4;2-}"), interval_iterator)
        self.assertAlmostEqual(parser.parse_element("{-1,2,3,4;2-}").values, ("1", "2", "3", "4"))
        self.assertAlmostEqual(parser.parse_element("{-1,2,3,4;2-}").interval, 2)

        self.assertEqual(Parser.parse("__{(var1)}__", {"var1": "hallo welt"})[0], "__hallo welt__")

    def test_default_pattern(self):
        self.assertEqual(Parser.parse("{[1,22,3243|___]}")[0], "__1")
        self.assertEqual(Parser.parse("{[1,22,3243|___]}")[1], "_22")
        self.assertEqual(Parser.parse("{[1,22,3243|___]}")[2], "3243")

        self.assertEqual(Parser.parse("{.1,100|___.}_{.20,30.}")[0], "__1_20")
        self.assertEqual(Parser.parse("{.1,100|___.}_{.20,30.}")[2], "100_20")

    def test_complex_example(self):
        from plately import Parser

        # example email template
        template = """
        Dear {(customer)},
        It is {.January,February,March.} the {.1,2,3.}th
        this is the {o1,1o}th e-mail you receive from us
        Your Lucky number of tody is: {?1,2,3,4,5,6,7?}
        """
        #todo: ...
        for result in Parser.parse(template, {"customer": "Anna"}):
            print(result)

        # example hyperparameter optimisation


