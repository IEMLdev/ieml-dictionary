from functools import reduce
from operator import mul
from typing import List, Union

from ieml.lexicon.grammar.character import Character, character

from ieml.dictionary.script import Script, script
from ieml.lexicon.grammar.usl import Literal
from .usl import Usl
from ieml.exceptions import InvalidIEMLObjectArgument
from ieml.constants import MAX_SINGULAR_SEQUENCES, CHARACTER_SIZE_LIMIT


def _character(semes: List[Union[Script, str]]):
    if not semes:
        return [script('E:')]

    try:
        _semes = [script(e) for e in semes]
    except TypeError:
        raise InvalidIEMLObjectArgument(Character, "The root argument %s is not an iterable" % str(semes))

    if len(_semes) > CHARACTER_SIZE_LIMIT:
        raise InvalidIEMLObjectArgument(Character, "Invalid semes count %d, must be lower or equal than %d."
                                        % (len(_semes), CHARACTER_SIZE_LIMIT))

    if any(not isinstance(c, Script) for c in _semes):
        raise InvalidIEMLObjectArgument(Character, "The children of a Topic must be a Word instance.")

    singular_sequences = [s for t in _semes for s in t.singular_sequences]
    if len(singular_sequences) != len(set(singular_sequences)):
        raise InvalidIEMLObjectArgument(Character, "Singular sequences intersection in %s." %
                                        str([str(t) for t in _semes]))

    return _semes


def word(substance: List[Union[str, Script]] = None,
         attribute: List[Union[str, Script]] = None,
         mode: List[Union[str, Script]] = None,
         literals:Literal = None):

    substance = _character(substance)
    attribute = _character(attribute)
    mode = _character(mode)

    return Word(substance, attribute, mode, literals=literals)


class Word(Usl):
    def __init__(self,
                 substance: List[Script],
                 attribute: List[Script],
                 mode: List[Script],
                 literals:Literal = None):

        self.substance = substance
        self.attribute = attribute
        self.mode = mode

        super().__init__(literals=literals)

        if self.cardinal > MAX_SINGULAR_SEQUENCES:
            raise InvalidIEMLObjectArgument(Word, "Too many Topic- singular sequences defined (max: 360): %d" % self.cardinal)

    def __iter__(self):
        return [self.substance, self.attribute, self.mode].__iter__()

    @property
    def grammatical_class(self):
        return max(s.script_class for s in self.substance)

    def _get_cardinal(self):
        return reduce(mul, [w.cardinal for char in [self.substance, self.attribute, self.mode] for w in char], 1)

    @staticmethod
    def _char_str(char):
        return "({0})".format("+".join("[{}]".format(str(e)) for e in char))

    def compute_str(self):
        return "[{0}*{1}*{2}]".format(self._char_str(self.substance),
                                      self._char_str(self.attribute),
                                      self._char_str(self.mode))

    def _do_gt(self, other):
        return (self.substance, self.attribute, self.mode) > (other.substance, other.attribute, other.mode)

    # def __iter__(self):
    #     return self.semes.__iter__()

    def _get_semes(self):
        return set(self.attribute + self.substance + self.mode)

    def _get_words(self):
        return {self}

    def _get_facts(self):
        return set()

    def _get_theories(self):
        return set()
    #
    # def __repr__(self, lang='en'):
    #     row_format = "{:50s}" * 2
    #     print(row_format.format("root", "flexion"))
    #
    #     clip = lambda s, n: s[:n-3] + '..' if len(s) > n else s
    #     res = ''
    #     for r, f in zip_longest(self.root, self.flexing, fillvalue=""):
    #         if r:
    #             r = clip(r.__repr__(lang=lang), 50)
    #         if f:
    #             f = clip(f.__repr__(lang=lang), 50)
    #         res += "{}\n".format(row_format.format(r,f))
    #
    #     return res


# class Topic(Word):
#     def __init__(self, substance: List[Script], attribute: List[Script], literals: Literal = None):
#         super().__init__(substance=substance, attribute=attribute, mode=[], literals=literals)
#
#
# class Character(Topic):
#     def __init__(self, substance: List[Script], literals: Literal = None):
#         super().__init__(substance=substance, attribute=[], literals=literals)
