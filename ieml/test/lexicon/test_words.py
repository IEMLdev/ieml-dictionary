import unittest

from ieml.lexicon.grammar import usl
from ieml.lexicon.lexicon import Lexicon


class MyTestCase(unittest.TestCase):
    def test_contains(self):
        w = usl("[([S:.E:A:S:.-]+[T:.E:A:S:.-]+[s.-S:.A:.-'+we.f.T:.-+u.A:.-+p.E:A:S:.-+E:T:S:+T:.-'])*([E:])*([E:])]")
        self.assertIn(w, w)

        wss = usl("[([S:.E:A:S:.-]+[T:.E:A:S:.-]+[s.-S:.A:.-'])*([E:])*([E:])]")
        self.assertIn(wss, w)

    def test_lexicon(self):
        for folder in Lexicon.load().names:
            lex = Lexicon.load(names=[folder])
            print(folder)

            paradigms = [u for u in lex.usls if u.cardinal != 1]
            sing = [u for u in lex.usls if u.cardinal == 1]
            for p in paradigms:
                lex.display(p)

            for s in sing:
                for p in paradigms:
                    if s in p:
                        break
                else:
                    lex.display(s)
                    self.fail("Not found in paradigms")


    # [("[([n.-T:.A:.-']+[d.-h.-']+[u.l.-+a.B:.-'+f.-S:.U:.-+T:.A:.-'])*([E:])*([E:])]", )]

if __name__ == '__main__':
    unittest.main()
