import unittest

from ieml.constants import DICTIONARY_FOLDER
from ieml.dictionary.dictionary import Dictionary
from ieml.dictionary.script.parser import ScriptParser
from ieml.dictionary.script import AdditiveScript, MultiplicativeScript, NullScript

# from ieml.dictionary import Dictionary
from ieml.dictionary.script import script as sc
from ieml.exceptions import CannotParse


class TestTermParser(unittest.TestCase):
    def setUp(self):
        self.parser = ScriptParser()

    def test_layer4(self):
        script = self.parser.parse("s.-S:.U:.-'l.-S:.O:.-'n.-T:.A:.-',+M:.-'M:.-'n.-T:.A:.-',")
        self.assertTrue(isinstance(script, AdditiveScript))
        self.assertTrue(isinstance(script.children[0], MultiplicativeScript))
        self.assertTrue(isinstance(script.children[1], MultiplicativeScript))
        self.assertTrue(script.layer == 4)

        self.assertEqual(str(script), "s.-S:.U:.-'l.-S:.O:.-'n.-T:.A:.-',+M:.-'M:.-'n.-T:.A:.-',")

    def test_fail(self):
        with self.assertRaises(CannotParse):
            ScriptParser().parse('wa:O:.')

    def test_layer(self):
        script = self.parser.parse("t.i.-s.i.-'u.T:.-U:.-'O:O:.-',B:.-',_M:.-',_;")
        self.assertTrue(script.layer == 6)
        self.assertEqual(str(script), "t.i.-s.i.-'u.T:.-U:.-'O:O:.-',B:.-',_M:.-',_;")
        for i in range(0,5):
            if isinstance(script, AdditiveScript):
                script = script.children[0]
            self.assertTrue(script.layer == (6 - i))
            script = script.children[0]

    def test_script(self):
        list_scripts = ["S:.-',S:.-',S:.-'B:.-'n.-S:.U:.-',_",
                        "S:M:.e.-M:M:.u.-E:.-+wa.e.-'+B:M:.e.-M:M:.a.-E:.-+wa.e.-'+T:M:.e.-M:M:.i.-E:.-+wa.e.-'"]
        for s in list_scripts:
            script = self.parser.parse(s)
            self.assertEqual(str(script), s)

    def test_empty(self):
        script = self.parser.parse("E:E:.E:.E:E:E:.-E:E:E:.E:.-E:E:.E:E:E:.-'")
        self.assertTrue(script.empty)
        self.assertEqual(str(script), "E:.-'")
        self.assertIsInstance(self.parser.parse('E:'), NullScript)

    def test_reduction(self):
        script = self.parser.parse("A:U:E:.")
        self.assertIsNotNone(script.character)
        self.assertEqual(str(script), "wu.")

    def test_singular_sequence(self):
        script = self.parser.parse("M:.-',M:.-',S:.-'B:.-'n.-S:.U:.-',_")

        self.assertEqual(script.cardinal, 9)
        self.assertEqual(script.cardinal, len(script.singular_sequences))
        self.assertSetEqual(set(map(str, script.singular_sequences)), {"S:.-',S:.-',S:.-'B:.-'n.-S:.U:.-',_",
                                                                   "S:.-',B:.-',S:.-'B:.-'n.-S:.U:.-',_",
                                                                   "S:.-',T:.-',S:.-'B:.-'n.-S:.U:.-',_",
                                                                   "B:.-',S:.-',S:.-'B:.-'n.-S:.U:.-',_",
                                                                   "B:.-',B:.-',S:.-'B:.-'n.-S:.U:.-',_",
                                                                   "B:.-',T:.-',S:.-'B:.-'n.-S:.U:.-',_",
                                                                   "T:.-',S:.-',S:.-'B:.-'n.-S:.U:.-',_",
                                                                   "T:.-',B:.-',S:.-'B:.-'n.-S:.U:.-',_",
                                                                   "T:.-',T:.-',S:.-'B:.-'n.-S:.U:.-',_"})
        for s in script.singular_sequences:
            self.assertEqual(s.cardinal, 1)

    def test_all_scripts(self):
        parser = ScriptParser()
        terms = [str(script) for script in Dictionary.load().scripts]
        terms_ast = [str(parser.parse(term)) for term in terms]
        self.assertListEqual(terms_ast, terms)

    def test_reduction_single_add(self):
        script = self.parser.parse("M:.-',M:.-',S:.-'B:.-'n.-S:.U:.-',_")
        self.assertIsInstance(script, MultiplicativeScript)
        script = MultiplicativeScript(substance=AdditiveScript(children=[script]))
        self.assertIsInstance(script.children[0], MultiplicativeScript)

    def test_duplicate_addition(self):
        script = AdditiveScript(children=[
            AdditiveScript(children=[
                MultiplicativeScript(character='wa'),
                MultiplicativeScript(character='wo')]),
            AdditiveScript(children=[
                MultiplicativeScript(character='j'),
                AdditiveScript(children=[
                    MultiplicativeScript(character='i'),
                    MultiplicativeScript(
                        attribute=AdditiveScript(character='M'),
                        substance=AdditiveScript(character='O'),
                        mode=MultiplicativeScript(character='U')
                    )
                ])
            ])])

        self.assertTrue(all(isinstance(s, MultiplicativeScript) for s in script.children))

    def test_singular_sequences_special(self):
        script = self.parser.parse('E:E:F:.')
        self.assertTrue(script.paradigm)
        self.assertEqual(script.cardinal, 5)
        self.assertListEqual(list(map(str, script.singular_sequences)),
                             ['E:E:U:.', 'E:E:A:.', 'E:E:S:.', 'E:E:B:.', 'E:E:T:.'])

    def test_compare(self):
        s1 = self.parser.parse("U:S:+T:S:. + S:S:S:+B:. + U:+S:T:B:.")
        s2 = self.parser.parse("U:T:S:+B:. + S:S:+T:B:. + U:+S:S:S:.")
        # print(old_canonical(s1))
        # print(old_canonical(s2))
        self.assertTrue(s1 > s2)
        s1 = sc('o.O:M:.-')
        s2 = sc('E:O:.T:M:.-')
        self.assertLess(s2, s1)


# Lot of test to do :
# - testing invalid ieml construction
# - testing redondant element in ieml addition
# -