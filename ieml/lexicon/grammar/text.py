from itertools import chain

from ieml.exceptions import InvalidIEMLObjectArgument
from ieml.lexicon.grammar.usl import Usl
from ieml.lexicon.grammar.fact import Fact
from ieml.lexicon.grammar.theory import Theory
from ieml.lexicon.grammar.word import Word

def text(children, literals=None):
    try:
        _children = [e for e in children]
    except TypeError:
        raise InvalidIEMLObjectArgument(Text, "The argument %s is not iterable." % str(children))

    if not all(isinstance(e, (Word, Word, Fact, Theory, Text)) for e in _children):
        raise InvalidIEMLObjectArgument(Text, "Invalid type instance in the list of a text,"
                                              " must be Word, Sentence, SuperSentence or Text")

    return Text(_children, literals=literals)


class Text(Usl):
    def __init__(self, children, literals=None):

        _children = [topic([c]) if isinstance(c, Word) else c for c in children]
        _children = list(chain([c for c in _children if not isinstance(c, Text)],
                               *(c.children for c in _children if isinstance(c, Text))))
        self.children = sorted(set(_children))

        dictionary_version = self.children[0].dictionary_version
        if any(e.dictionary_version != dictionary_version for e in self.children):
            raise InvalidIEMLObjectArgument(Fact, "Incompatible dictionary version in the list of usls")

        super().__init__(dictionary_version, literals=literals)

    def compute_str(self):
        return '/{0}/'.format('//'.join(str(c) for c in self.children))

    def __iter__(self):
        return self.children.__iter__()

    def _get_semes(self):
        return set(chain.from_iterable(c.semes for c in self.children))

    def _get_words(self):
        return set(chain.from_iterable(c.words for c in self.children))

    def _get_facts(self):
        return set(chain.from_iterable(c.facts for c in self.children))

    def _get_theories(self):
        return set(chain.from_iterable(c.theories for c in self.children))

    def _set_version(self, version):
        for c in self.children:
            c.set_dictionary_version(version)

    def _do_gt(self, other):
        return self.children > other.children

    def __repr__(self, lang='en'):
        return "[{}]".format(', '.join([c.__repr__() for c in self.children]))