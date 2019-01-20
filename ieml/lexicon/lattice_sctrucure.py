from collections import defaultdict
from itertools import product



class LatticeNode:
    def __init__(self, word, parents, child):
        self.word = word
        self.parents = parents
        self.child = child


class LatticeStructure:
    def __init__(self, words):
        self.words_to_latticeNode, self.roots = self._build_hierarchie(words)

    def __getitem__(self, item):
        return self.words_to_latticeNode[item]

    @staticmethod
    def _build_hierarchie(words):
        word_to_parents = {w: set() for w in words}
        word_to_child = {w: set() for w in words}

        for w0, w1 in product(words, words):
            if w0 != w1 and w0 in w1:
                word_to_parents[w0].add(w1)
                word_to_child[w1].add(w0)

        words_to_lattice = {w: LatticeNode(w, parents, child=word_to_child[w]) for w, parents in word_to_parents.items()}
        roots = [words_to_lattice[w] for w, parents in word_to_parents.items() if not parents]

        return words_to_lattice, roots