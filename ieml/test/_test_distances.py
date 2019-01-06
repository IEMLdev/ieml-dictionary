import pprint
import unittest

from ieml.ieml_objects import Term, Word, Clause, Sentence, SuperSentence, Morpheme, SuperClause, Text, Hypertext

from ieml.calculation.distance import (object_proximity_index,
                                       set_proximity_index, mutual_inclusion_index, build_graph,
                                       partition_graph, get_paradigms, connexity_index,
                                       grammatical_class_index, paradigmatic_equivalence_class_index)
from ieml.script.operator import sc
from ieml.usl import usl


class DistanceComputationTests(unittest.TestCase):

    def setUp(self):

        # These words are going to serve as building blocks to build objects of the layers above.
        self.word_1 = Word(Morpheme([Term(sc('wa.')), Term(sc("l.-x.-s.y.-'")), Term(sc("e.-u.-we.h.-'")),
                                     Term(sc("M:.E:A:M:.-")), Term(sc("E:A:.k.-"))]),
                           Morpheme([Term(sc('wo.')), Term(sc("T:.E:A:T:.-")),
                                     Term(sc("T:.-',S:.-',S:.-'B:.-'n.-S:.U:.-',_"))]))
        self.word_2 = Word(Morpheme([Term(sc("l.-x.-s.y.-'")), Term(sc("e.-u.-we.h.-'"))]),
                           Morpheme([Term(sc("T:.E:A:T:.-")), Term(sc("E:A:.k.-"))]))
        self.word_3 = Word(Morpheme([Term(sc("E:S:.O:B:.-")), Term(sc("E:S:.O:T:.-"))]),# Term(sc("E:S:.U:M:.-"))]),
                           Morpheme([Term(sc("E:O:.S:M:.-"))]))
        self.word_4 = Word(Morpheme([Term(sc("S:M:.e.-t.u.-'"))]),
                           Morpheme([Term(sc("B:M:.y.-")), Term(sc("T:M:.y.-")), Term(sc("S:M:.y.-"))]))
        self.word_5 = Word(Morpheme([Term(sc("j.-'F:.-'k.o.-t.o.-',")), Term(sc("h.-'F:.-'k.o.-t.o.-',")),
                                     Term(sc("c.-'F:.-'k.o.-t.o.-',"))]),
                           Morpheme([Term(sc("E:M:.wa.-")), Term(sc("E:M:.wu.-")), Term(sc("E:M:.we.-"))]))
        self.word_6 = Word(Morpheme([Term(sc("we.y.-"))]))
        self.word_7 = Word(Morpheme([Term(sc("we.b.-")), Term(sc("p.m.-")), Term(sc("M:M:.we.-"))]),
                           Morpheme([Term(sc("a."))]))
        self.word_8 = Word(Morpheme([Term(sc("s.i.-b.i.-'"))]))
        self.word_9 = Word(Morpheme([Term(sc("we.O:B:.-")), Term(sc("we.O:T:.-")), Term(sc("wo.M:U:.-"))]))
        self.word_10 = Word(Morpheme([Term(sc("b.-S:.A:.-'B:.-'B:.-',")), Term(sc("e.-u.-we.h.-'"))]),
                            Morpheme([Term(sc("m.a.-M:M:.a.-f.o.-'")), Term(sc("n.a.-M:M:.a.-f.o.-'")),
                                      Term(sc("b.-S:.A:.-'T:.-'T:.-',"))]))


    def test_set_proximity_text(self):
        # TODO: DO IT
        pass

    def test_set_proximity_super_sentence(self):
        s_1 = Sentence([Clause(self.word_1, self.word_2, self.word_5), Clause(self.word_1, self.word_4, self.word_7),
                        Clause(self.word_1, self.word_6, self.word_9), Clause(self.word_2, self.word_3, self.word_7),
                        Clause(self.word_2, self.word_8, self.word_5), Clause(self.word_6, self.word_10, self.word_5)])

        s_2 = Sentence([Clause(self.word_4, self.word_1, self.word_7), Clause(self.word_4, self.word_6, self.word_8),
                        Clause(self.word_1, self.word_3, self.word_9), Clause(self.word_1, self.word_10, self.word_2),
                        Clause(self.word_6, self.word_5, self.word_9)])

        s_3 = Sentence([Clause(self.word_9, self.word_2, self.word_1), Clause(self.word_2, self.word_6, self.word_3),
                        Clause(self.word_2, self.word_4, self.word_3), Clause(self.word_2, self.word_8, self.word_7),
                        Clause(self.word_4, self.word_10, self.word_7)])

        s_4 = Sentence([Clause(self.word_8, self.word_7, self.word_1), Clause(self.word_7, self.word_6, self.word_2),
                        Clause(self.word_6, self.word_4, self.word_3), Clause(self.word_6, self.word_5, self.word_9)])

        s_5 = Sentence([Clause(self.word_8, self.word_7, self.word_4), Clause(self.word_8, self.word_10, self.word_3)])

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                        Clause(self.word_4, self.word_7, self.word_9)])

        super_sentence_1 = SuperSentence([SuperClause(s_1, s_2, s_3), SuperClause(s_1, s_6, s_4)])
        super_sentence_2 = SuperSentence([SuperClause(s_4, s_2, s_5), SuperClause(s_4, s_1, s_6),
                                          SuperClause(s_4, s_3, s_5)])
        super_sentence_3 = SuperSentence([SuperClause(s_6, s_1, s_3), SuperClause(s_1, s_2, s_4),
                                          SuperClause(s_2, s_5, s_3)])
        super_sentence_4 = SuperSentence([SuperClause(s_4, s_2, s_6), SuperClause(s_4, s_1, s_6),
                                          SuperClause(s_2, s_3, s_6)])

        usl_a = usl(Text([super_sentence_1, super_sentence_2, super_sentence_3]))
        usl_b = usl(Text([super_sentence_1, super_sentence_2, super_sentence_4]))
        index = set_proximity_index(SuperSentence, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = set_proximity_index(SuperSentence, usl_a, usl_a)
        print("Proximity Index for the identical USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_set_proximity_sentence(self):
        s_1 = Sentence([Clause(self.word_1, self.word_2, self.word_5), Clause(self.word_1, self.word_4, self.word_7),
                        Clause(self.word_1, self.word_6, self.word_9), Clause(self.word_2, self.word_3, self.word_7),
                        Clause(self.word_2, self.word_8, self.word_5), Clause(self.word_6, self.word_10, self.word_5)])

        s_2 = Sentence([Clause(self.word_4, self.word_1, self.word_7), Clause(self.word_4, self.word_6, self.word_8),
                        Clause(self.word_1, self.word_3, self.word_9), Clause(self.word_1, self.word_10, self.word_2),
                        Clause(self.word_6, self.word_5, self.word_9)])

        s_3 = Sentence([Clause(self.word_9, self.word_2, self.word_1), Clause(self.word_2, self.word_6, self.word_3),
                        Clause(self.word_2, self.word_4, self.word_3), Clause(self.word_2, self.word_8, self.word_7),
                        Clause(self.word_4, self.word_10, self.word_7)])
        s_4 = Sentence([Clause(self.word_8, self.word_7, self.word_1), Clause(self.word_7, self.word_6, self.word_2),
                        Clause(self.word_6, self.word_4, self.word_3), Clause(self.word_6, self.word_5, self.word_9)])

        s_5 = Sentence([Clause(self.word_8, self.word_7, self.word_4), Clause(self.word_8, self.word_10, self.word_3)])

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                    Clause(self.word_4, self.word_7, self.word_9)])

        usl_a = usl(Text([s_1, s_2, s_6, s_5]))
        usl_b = usl(Text([s_2, s_3, s_6, s_4]))

        index = set_proximity_index(Sentence, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = set_proximity_index(Sentence, usl_a, usl_a)
        print("Proximity Index for the identical USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_set_proximity_word(self):

        usl_a = usl(Text([self.word_1, self.word_3, self.word_2]))
        usl_b = usl(Text([self.word_2, self.word_5]))

        index = set_proximity_index(Word, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = set_proximity_index(Word, usl_a, usl_a)
        print("Proximity Index for the identical USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_object_proximity_text(self):
        # TODO
        pass

    def test_object_proximity_super_sentence(self):
        s_1 = Sentence([Clause(self.word_1, self.word_2, self.word_5), Clause(self.word_1, self.word_4, self.word_7),
                        Clause(self.word_1, self.word_6, self.word_9), Clause(self.word_2, self.word_3, self.word_7),
                        Clause(self.word_2, self.word_8, self.word_5), Clause(self.word_6, self.word_10, self.word_5)])

        s_2 = Sentence([Clause(self.word_4, self.word_1, self.word_7), Clause(self.word_4, self.word_6, self.word_8),
                        Clause(self.word_1, self.word_3, self.word_9), Clause(self.word_1, self.word_10, self.word_2),
                        Clause(self.word_6, self.word_5, self.word_9)])

        s_3 = Sentence([Clause(self.word_9, self.word_2, self.word_1), Clause(self.word_2, self.word_6, self.word_3),
                        Clause(self.word_2, self.word_4, self.word_3), Clause(self.word_2, self.word_8, self.word_7),
                        Clause(self.word_4, self.word_10, self.word_7)])

        s_4 = Sentence([Clause(self.word_8, self.word_7, self.word_1), Clause(self.word_7, self.word_6, self.word_2),
                        Clause(self.word_6, self.word_4, self.word_3), Clause(self.word_6, self.word_5, self.word_9)])

        s_5 = Sentence([Clause(self.word_8, self.word_7, self.word_4), Clause(self.word_8, self.word_10, self.word_3)])

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                        Clause(self.word_4, self.word_7, self.word_9)])

        super_sentence_1 = SuperSentence([SuperClause(s_1, s_2, s_3), SuperClause(s_1, s_6, s_4)])
        super_sentence_2 = SuperSentence([SuperClause(s_4, s_2, s_5), SuperClause(s_4, s_1, s_6),
                                          SuperClause(s_4, s_3, s_5)])
        super_sentence_3 = SuperSentence([SuperClause(s_6, s_1, s_3), SuperClause(s_1, s_2, s_4),
                                          SuperClause(s_2, s_5, s_3)])
        super_sentence_4 = SuperSentence([SuperClause(s_4, s_2, s_6), SuperClause(s_4, s_1, s_6),
                                          SuperClause(s_2, s_3, s_6)])

        usl_a = usl(Text([super_sentence_1, super_sentence_2, super_sentence_3]))
        usl_b = usl(Text([super_sentence_1, super_sentence_2, super_sentence_4]))
        index = object_proximity_index(SuperSentence, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = object_proximity_index(SuperSentence, usl_a, usl_a)
        print("Proximity Index for the identical USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_object_proximity_sentence(self):
        s_1 = Sentence([Clause(self.word_1, self.word_2, self.word_5), Clause(self.word_1, self.word_4, self.word_7),
                        Clause(self.word_1, self.word_6, self.word_9), Clause(self.word_2, self.word_3, self.word_7),
                        Clause(self.word_2, self.word_8, self.word_5), Clause(self.word_6, self.word_10, self.word_5)])

        s_2 = Sentence([Clause(self.word_4, self.word_1, self.word_7), Clause(self.word_4, self.word_6, self.word_8),
                    Clause(self.word_1, self.word_3, self.word_9), Clause(self.word_1, self.word_10, self.word_2),
                    Clause(self.word_6, self.word_5, self.word_9)])

        s_3 = Sentence([Clause(self.word_9, self.word_2, self.word_1), Clause(self.word_2, self.word_6, self.word_3),
                    Clause(self.word_2, self.word_4, self.word_3), Clause(self.word_2, self.word_8, self.word_7),
                    Clause(self.word_4, self.word_10, self.word_7)])
        s_4 = Sentence([Clause(self.word_8, self.word_7, self.word_1), Clause(self.word_7, self.word_6, self.word_2),
                    Clause(self.word_6, self.word_4, self.word_3), Clause(self.word_6, self.word_5, self.word_9)])

        s_5 = Sentence([Clause(self.word_8, self.word_7, self.word_4), Clause(self.word_8, self.word_10, self.word_3)])

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                    Clause(self.word_4, self.word_7, self.word_9)])

        usl_a = usl(Text([s_1, s_2, s_6, s_5]))
        usl_b = usl(Text([s_2, s_3, s_6, s_4]))

        index = object_proximity_index(Sentence, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = object_proximity_index(Sentence, usl_a, usl_a)
        print("Proximity Index for the identical USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_object_proximity_word(self):
        usl_a = usl(Text([self.word_1, self.word_3, self.word_2]))
        usl_b = usl(Text([self.word_2, self.word_5]))

        index = object_proximity_index(Word, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = object_proximity_index(Sentence, usl_a, usl_a)
        print("Proximity Index for the identical USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_mutual_inclusion_text(self):
        # TODO: implement
        pass

    def test_mutual_inclusion_super_sentence(self):
        s_1 = Sentence([Clause(self.word_1, self.word_2, self.word_5), Clause(self.word_1, self.word_4, self.word_7),
                            Clause(self.word_1, self.word_6, self.word_9), Clause(self.word_2, self.word_3, self.word_7),
                            Clause(self.word_2, self.word_8, self.word_5), Clause(self.word_6, self.word_10, self.word_5)])

        s_2 = Sentence([Clause(self.word_4, self.word_1, self.word_7), Clause(self.word_4, self.word_6, self.word_8),
                        Clause(self.word_1, self.word_3, self.word_9), Clause(self.word_1, self.word_10, self.word_2),
                        Clause(self.word_6, self.word_5, self.word_9)])

        s_3 = Sentence([Clause(self.word_9, self.word_2, self.word_1), Clause(self.word_2, self.word_6, self.word_3),
                        Clause(self.word_2, self.word_4, self.word_3), Clause(self.word_2, self.word_8, self.word_7),
                        Clause(self.word_4, self.word_10, self.word_7)])

        s_4 = Sentence([Clause(self.word_8, self.word_7, self.word_1), Clause(self.word_7, self.word_6, self.word_2),
                        Clause(self.word_6, self.word_4, self.word_3), Clause(self.word_6, self.word_5, self.word_9)])

        s_5 = Sentence([Clause(self.word_8, self.word_7, self.word_4), Clause(self.word_8, self.word_10, self.word_3)])

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                        Clause(self.word_4, self.word_7, self.word_9)])

        super_sentence_1 = SuperSentence([SuperClause(s_1, s_2, s_3), SuperClause(s_1, s_6, s_4)])
        super_sentence_2 = SuperSentence([SuperClause(s_4, s_2, s_5), SuperClause(s_4, s_1, s_6),
                                          SuperClause(s_4, s_3, s_5)])
        super_sentence_3 = SuperSentence([SuperClause(s_6, s_1, s_3), SuperClause(s_1, s_2, s_4),
                                          SuperClause(s_2, s_5, s_3)])
        super_sentence_4 = SuperSentence([SuperClause(s_4, s_2, s_6), SuperClause(s_4, s_1, s_6),
                                          SuperClause(s_2, s_3, s_6)])

        usl_a = usl(Text([super_sentence_1, super_sentence_2, super_sentence_3]))
        usl_b = usl(Text([super_sentence_1, super_sentence_2, super_sentence_4]))

        index = mutual_inclusion_index(usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = mutual_inclusion_index(usl_a, usl_a)
        print("Proximity Index for the identical USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_mutual_inclusion_sentence(self):
        s_1 = Sentence([Clause(self.word_1, self.word_2, self.word_5), Clause(self.word_1, self.word_4, self.word_7),
                        Clause(self.word_1, self.word_6, self.word_9), Clause(self.word_2, self.word_3, self.word_7),
                        Clause(self.word_2, self.word_8, self.word_5), Clause(self.word_6, self.word_10, self.word_5)])

        s_2 = Sentence([Clause(self.word_4, self.word_1, self.word_7), Clause(self.word_4, self.word_6, self.word_8),
                    Clause(self.word_1, self.word_3, self.word_9), Clause(self.word_1, self.word_10, self.word_2),
                    Clause(self.word_6, self.word_5, self.word_9)])

        s_3 = Sentence([Clause(self.word_9, self.word_2, self.word_1), Clause(self.word_2, self.word_6, self.word_3),
                    Clause(self.word_2, self.word_4, self.word_3), Clause(self.word_2, self.word_8, self.word_7),
                    Clause(self.word_4, self.word_10, self.word_7)])
        s_4 = Sentence([Clause(self.word_8, self.word_7, self.word_1), Clause(self.word_7, self.word_6, self.word_2),
                    Clause(self.word_6, self.word_4, self.word_3), Clause(self.word_6, self.word_5, self.word_9)])

        s_5 = Sentence([Clause(self.word_8, self.word_7, self.word_4), Clause(self.word_8, self.word_10, self.word_3)])

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                    Clause(self.word_4, self.word_7, self.word_9)])

        usl_a = usl(Text([s_1, s_2, s_6, s_5]))
        usl_b = usl(Text([s_2, s_3, s_6, s_4]))

        index = mutual_inclusion_index(usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = mutual_inclusion_index(usl_a, usl_a)
        print("Proximity Index for the same USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_mutual_inclusion_word(self):
        usl_a = usl(Text([self.word_1, self.word_3, self.word_2]))
        usl_b = usl(Text([self.word_2, self.word_5]))

        index = mutual_inclusion_index(usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = mutual_inclusion_index(usl_a, usl_a)
        print("Proximity Index for the identical USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_connexity_index_text(self):
        pass

    def test_connexity_index_super_sentence(self):
        s_1 = Sentence([Clause(self.word_1, self.word_2, self.word_5), Clause(self.word_1, self.word_4, self.word_7),
                        Clause(self.word_1, self.word_6, self.word_9), Clause(self.word_2, self.word_3, self.word_7),
                        Clause(self.word_2, self.word_8, self.word_5), Clause(self.word_6, self.word_10, self.word_5)])

        s_2 = Sentence([Clause(self.word_4, self.word_1, self.word_7), Clause(self.word_4, self.word_6, self.word_8),
                    Clause(self.word_1, self.word_3, self.word_9), Clause(self.word_1, self.word_10, self.word_2),
                    Clause(self.word_6, self.word_5, self.word_9)])

        s_3 = Sentence([Clause(self.word_9, self.word_2, self.word_1), Clause(self.word_2, self.word_6, self.word_3),
                    Clause(self.word_2, self.word_4, self.word_3), Clause(self.word_2, self.word_8, self.word_7),
                    Clause(self.word_4, self.word_10, self.word_7)])

        s_4 = Sentence([Clause(self.word_8, self.word_7, self.word_1), Clause(self.word_7, self.word_6, self.word_2),
                    Clause(self.word_6, self.word_4, self.word_3), Clause(self.word_6, self.word_5, self.word_9)])

        s_5 = Sentence([Clause(self.word_8, self.word_7, self.word_4), Clause(self.word_8, self.word_10, self.word_3)])

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                    Clause(self.word_4, self.word_7, self.word_9)])

        super_sentence_1 = SuperSentence([SuperClause(s_1, s_2, s_3), SuperClause(s_1, s_6, s_4)])
        super_sentence_2 = SuperSentence([SuperClause(s_4, s_2, s_5), SuperClause(s_4, s_1, s_6),
                                         SuperClause(s_4, s_3, s_5)])
        super_sentence_3 = SuperSentence([SuperClause(s_6, s_1, s_3), SuperClause(s_1, s_2, s_4),
                                          SuperClause(s_2, s_5, s_3)])
        super_sentence_4 = SuperSentence([SuperClause(s_4, s_2, s_6), SuperClause(s_4, s_1, s_6),
                                          SuperClause(s_2, s_3, s_6)])

        usl_a = usl(Text([super_sentence_1, super_sentence_2, super_sentence_3]))
        usl_b = usl(Text([super_sentence_1, super_sentence_2, super_sentence_4]))

        index = connexity_index(SuperSentence, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = connexity_index(SuperSentence, usl_a, usl_a)
        print("Proximity Index for the same USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_connexity_index_sentence(self):
        s_1 = Sentence([Clause(self.word_1, self.word_2, self.word_5), Clause(self.word_1, self.word_4, self.word_7),
                        Clause(self.word_1, self.word_6, self.word_9), Clause(self.word_2, self.word_3, self.word_7),
                        Clause(self.word_2, self.word_8, self.word_5), Clause(self.word_6, self.word_10, self.word_5)])

        s_2 = Sentence([Clause(self.word_4, self.word_1, self.word_7), Clause(self.word_4, self.word_6, self.word_8),
                        Clause(self.word_1, self.word_3, self.word_9), Clause(self.word_1, self.word_10, self.word_2),
                        Clause(self.word_6, self.word_5, self.word_9)])

        s_3 = Sentence([Clause(self.word_9, self.word_2, self.word_1), Clause(self.word_2, self.word_6, self.word_3),
                        Clause(self.word_2, self.word_4, self.word_3), Clause(self.word_2, self.word_8, self.word_7),
                        Clause(self.word_4, self.word_10, self.word_7)])
        s_4 = Sentence([Clause(self.word_8, self.word_7, self.word_1), Clause(self.word_7, self.word_6, self.word_2),
                        Clause(self.word_6, self.word_4, self.word_3), Clause(self.word_6, self.word_5, self.word_9)])

        s_5 = Sentence([Clause(self.word_8, self.word_7, self.word_4), Clause(self.word_8, self.word_10, self.word_3)])

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                        Clause(self.word_4, self.word_7, self.word_9)])

        usl_a = usl(Text([s_1, s_2, s_6, s_5]))
        usl_b = usl(Text([s_2, s_3, s_6, s_4]))

        index = connexity_index(Sentence, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = connexity_index(Sentence, usl_a, usl_a)
        print("Proximity Index for the same USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_connexity_index_word(self):
        usl_a = usl(Text([self.word_1, self.word_3, self.word_2]))
        usl_b = usl(Text([self.word_2, self.word_5]))

        index = connexity_index(Word, usl_a, usl_b)
        print("Proximity Index for the different USLs: " + str(index))
        self.assertTrue(index != 1 and index != 0, "Different USLs should yield and index that isn't null nor is 1")

        index = connexity_index(Word, usl_a, usl_a)
        print("Proximity Index for the same USLs: " + str(index))
        self.assertTrue(index == 1, "Identical USLs should yield and index of 1")

    def test_super_sentence_graph(self):
        s_1 = Sentence([Clause(self.word_1, self.word_2, self.word_5), Clause(self.word_1, self.word_4, self.word_7),
                        Clause(self.word_1, self.word_6, self.word_9), Clause(self.word_2, self.word_3, self.word_7),
                        Clause(self.word_2, self.word_8, self.word_5), Clause(self.word_6, self.word_10, self.word_5)])

        s_2 = Sentence([Clause(self.word_4, self.word_1, self.word_7), Clause(self.word_4, self.word_6, self.word_8),
                        Clause(self.word_1, self.word_3, self.word_9), Clause(self.word_1, self.word_10, self.word_2),
                        Clause(self.word_6, self.word_5, self.word_9)])

        s_3 = Sentence([Clause(self.word_9, self.word_2, self.word_1), Clause(self.word_2, self.word_6, self.word_3),
                        Clause(self.word_2, self.word_4, self.word_3), Clause(self.word_2, self.word_8, self.word_7),
                        Clause(self.word_4, self.word_10, self.word_7)])
        s_4 = Sentence([Clause(self.word_8, self.word_7, self.word_1), Clause(self.word_7, self.word_6, self.word_2),
                        Clause(self.word_6, self.word_4, self.word_3), Clause(self.word_6, self.word_5, self.word_9)])

        s_5 = Sentence([Clause(self.word_8, self.word_7, self.word_4), Clause(self.word_8, self.word_10, self.word_3)])

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                        Clause(self.word_4, self.word_7, self.word_9)])

        super_sentence_1 = SuperSentence([SuperClause(s_1, s_2, s_6), SuperClause(s_1, s_3, s_6),
                                          SuperClause(s_3, s_4, s_6)])
        super_sentence_2 = SuperSentence([SuperClause(s_2, s_1, s_6), SuperClause(s_2, s_3, s_6),
                                          SuperClause(s_3, s_4, s_6)])

        graph = build_graph(super_sentence_1, super_sentence_2,
                            set(super_sentence_1.tree_graph.nodes) & set(super_sentence_2.tree_graph.nodes))

        correct_graph = {
            s_1: [s_2],
            s_2: [s_1],
            s_3: [s_4],
            s_4: [s_3]
        }

        # The node adjacency list should be sorted
        for v_1, v_2 in zip(correct_graph.values(), graph.values()):
            v_1.sort()
            v_2.sort()

        pp = pprint.PrettyPrinter()

        print("Built graph: ")
        pp.pprint(graph)
        print("Correct graph: ")
        pp.pprint(correct_graph)

        self.assertEqual(graph, correct_graph)

    def test_sentence_graph(self):
        s_1 = Sentence([Clause(self.word_1, self.word_2, self.word_10), Clause(self.word_1, self.word_3, self.word_10),
                        Clause(self.word_1, self.word_4, self.word_10), Clause(self.word_3, self.word_9, self.word_10),
                        Clause(self.word_3, self.word_5, self.word_10), Clause(self.word_4, self.word_6, self.word_10),
                        Clause(self.word_5, self.word_8, self.word_10), Clause(self.word_6, self.word_7, self.word_10)])

        s_2 = Sentence([Clause(self.word_2, self.word_1, self.word_10), Clause(self.word_2, self.word_5, self.word_10),
                        Clause(self.word_2, self.word_3, self.word_10), Clause(self.word_1, self.word_4, self.word_10),
                        Clause(self.word_5, self.word_7, self.word_10), Clause(self.word_5, self.word_8, self.word_10),
                        Clause(self.word_3, self.word_9, self.word_10), Clause(self.word_4, self.word_6, self.word_10)])

        intersection = set(s_1.tree_graph.nodes) & set(s_1.tree_graph.nodes)
        graph = build_graph(s_1, s_2, intersection)

        correct_graph = {
            self.word_1: [self.word_2, self.word_4],
            self.word_2: [self.word_1],
            self.word_3: [self.word_9],
            self.word_4: [self.word_1, self.word_6],
            self.word_5: [self.word_8],
            self.word_6: [self.word_4],
            self.word_7: [],
            self.word_8: [self.word_5],
            self.word_9: [self.word_3],
        }

        # The node adjacency list should be sorted
        for v_1, v_2 in zip(correct_graph.values(), graph.values()):
            v_1.sort()
            v_2.sort()

        pp = pprint.PrettyPrinter()

        print("Built graph: ")
        pp.pprint(graph)
        print("Correct graph: ")
        pp.pprint(correct_graph)

        self.assertEqual(graph, correct_graph)

    def test_word_graph(self):

        intersection = set(self.word_1.root.children + self.word_1.flexing.children) & \
                       set(self.word_2.root.children + self.word_2.flexing.children)

        graph = build_graph(self.word_1, self.word_2, intersection)

        term_1 = Term(sc("l.-x.-s.y.-'"))
        term_2 = Term(sc("E:A:.k.-"))
        term_3 = Term(sc("T:.E:A:T:.-"))
        term_4 = Term(sc("e.-u.-we.h.-'"))

        correct_graph = {
            term_1: [term_3],
            term_2: [],
            term_3: [term_1, term_4],
            term_4: [term_3]
        }

        # The node adjacency list should be sorted
        for v_1, v_2 in zip(correct_graph.values(), graph.values()):
            v_1.sort()
            v_2.sort()

        pp = pprint.PrettyPrinter()

        print("Built graph: ")
        pp.pprint(graph)
        print("Correct graph: ")
        pp.pprint(correct_graph)

        self.assertEqual(graph, correct_graph)

    def test_partition_sentences(self):
        s_1 = Sentence([Clause(self.word_1, self.word_2, self.word_10), Clause(self.word_1, self.word_3, self.word_10),
                        Clause(self.word_1, self.word_4, self.word_10), Clause(self.word_3, self.word_9, self.word_10),
                        Clause(self.word_3, self.word_5, self.word_10), Clause(self.word_4, self.word_6, self.word_10),
                        Clause(self.word_5, self.word_8, self.word_10), Clause(self.word_6, self.word_7, self.word_10)])

        s_2 = Sentence([Clause(self.word_2, self.word_1, self.word_10), Clause(self.word_2, self.word_5, self.word_10),
                    Clause(self.word_2, self.word_3, self.word_10), Clause(self.word_1, self.word_4, self.word_10),
                    Clause(self.word_5, self.word_7, self.word_10), Clause(self.word_5, self.word_8, self.word_10),
                    Clause(self.word_3, self.word_9, self.word_10), Clause(self.word_4, self.word_6, self.word_10)])

        intersection = list(set(s_1.tree_graph.nodes) & set(s_2.tree_graph.nodes))
        intersection.sort()

        graph = build_graph(s_1, s_2, intersection)

        partitions = partition_graph(graph)
        correct_partitions = [{self.word_1, self.word_2, self.word_4, self.word_6}, {self.word_3, self.word_9},
                              {self.word_5, self.word_8}, {self.word_7}]

        # This is because the order doesn't matter to us but the partition_graph method returns a list
        def same_partitions(p1, p2):

            if len(p1) != len(p2):
                return False
            else:
                return all(partition in p2 for partition in p1)

        self.assertTrue(same_partitions(partitions, correct_partitions))

    def test_grammatical_class_index_sentences(self):
        s_1 = Sentence([Clause(self.word_1, self.word_2, self.word_5), Clause(self.word_1, self.word_4, self.word_7),
                        Clause(self.word_1, self.word_6, self.word_9), Clause(self.word_2, self.word_3, self.word_7),
                        Clause(self.word_2, self.word_8, self.word_5), Clause(self.word_6, self.word_10, self.word_5)])

        s_2 = Sentence([Clause(self.word_4, self.word_1, self.word_7), Clause(self.word_4, self.word_6, self.word_8),
                        Clause(self.word_1, self.word_3, self.word_9), Clause(self.word_1, self.word_10, self.word_2),
                        Clause(self.word_6, self.word_5, self.word_9)])

        s_3 = Sentence([Clause(self.word_9, self.word_2, self.word_1), Clause(self.word_2, self.word_6, self.word_3),
                        Clause(self.word_2, self.word_4, self.word_3), Clause(self.word_2, self.word_8, self.word_7),
                        Clause(self.word_4, self.word_10, self.word_7)])
        s_4 = Sentence([Clause(self.word_8, self.word_7, self.word_1), Clause(self.word_7, self.word_6, self.word_2),
                        Clause(self.word_6, self.word_4, self.word_3), Clause(self.word_6, self.word_5, self.word_9)])

        s_5 = Sentence([Clause(self.word_8, self.word_7, self.word_4), Clause(self.word_8, self.word_10, self.word_3)])

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                        Clause(self.word_4, self.word_7, self.word_9)])

        usl_a = usl(Text([s_1, s_2, s_6, s_5]))
        usl_b = usl(Text([s_2, s_3, s_6, s_4]))

        eo_index = grammatical_class_index(usl_a, usl_b, 'EO', Sentence)
        oo_index = grammatical_class_index(usl_a, usl_b, 'OO', Sentence)

        print("EO index: " + str(eo_index))
        print("OO index: " + str(oo_index))

        self.assertTrue(eo_index != 1, "Two different USLs don't have an EO index of 1")
        self.assertTrue(oo_index != 1, "Two different USLs don't have an EO index of 1")

    def test_grammatical_class_index_super_sentence(self):
        s_1 = Sentence([Clause(self.word_1, self.word_2, self.word_5), Clause(self.word_1, self.word_4, self.word_7),
                        Clause(self.word_1, self.word_6, self.word_9), Clause(self.word_2, self.word_3, self.word_7),
                        Clause(self.word_2, self.word_8, self.word_5), Clause(self.word_6, self.word_10, self.word_5)])

        s_2 = Sentence([Clause(self.word_4, self.word_1, self.word_7), Clause(self.word_4, self.word_6, self.word_8),
                        Clause(self.word_1, self.word_3, self.word_9), Clause(self.word_1, self.word_10, self.word_2),
                        Clause(self.word_6, self.word_5, self.word_9)])

        s_3 = Sentence([Clause(self.word_9, self.word_2, self.word_1), Clause(self.word_2, self.word_6, self.word_3),
                        Clause(self.word_2, self.word_4, self.word_3), Clause(self.word_2, self.word_8, self.word_7),
                        Clause(self.word_4, self.word_10, self.word_7)])

        s_4 = Sentence([Clause(self.word_8, self.word_7, self.word_1), Clause(self.word_7, self.word_6, self.word_2),
                        Clause(self.word_6, self.word_4, self.word_3), Clause(self.word_6, self.word_5, self.word_9)])

        s_5 = Sentence([Clause(self.word_8, self.word_7, self.word_4), Clause(self.word_8, self.word_10, self.word_3)])

        s_6 = Sentence([Clause(self.word_6, self.word_3, self.word_1), Clause(self.word_6, self.word_4, self.word_10),
                        Clause(self.word_4, self.word_7, self.word_9)])

        super_sentence_1 = SuperSentence([SuperClause(s_1, s_2, s_3), SuperClause(s_1, s_6, s_4)])
        super_sentence_2 = SuperSentence([SuperClause(s_4, s_2, s_5), SuperClause(s_4, s_1, s_6),
                                          SuperClause(s_4, s_3, s_5)])
        super_sentence_3 = SuperSentence([SuperClause(s_6, s_1, s_3), SuperClause(s_1, s_2, s_4),
                                          SuperClause(s_2, s_5, s_3)])
        super_sentence_4 = SuperSentence([SuperClause(s_4, s_2, s_6), SuperClause(s_4, s_1, s_6),
                                          SuperClause(s_2, s_3, s_6)])

        usl_a = usl(Text([super_sentence_1, super_sentence_2, super_sentence_3]))
        usl_b = usl(Text([super_sentence_1, super_sentence_2, super_sentence_4]))

        eo_index = grammatical_class_index(usl_a, usl_b, 'EO', SuperSentence)
        oo_index = grammatical_class_index(usl_a, usl_b, 'OO', SuperSentence)

        print("EO index: " + str(eo_index))
        print("OO index: " + str(oo_index))

        self.assertTrue(eo_index != 1, "Two different USLs don't have an EO index of 1")
        self.assertTrue(oo_index != 1, "Two different USLs don't have an EO index of 1")

    def test_get_paradigm(self):
        usl_a = usl(Text([self.word_1, self.word_3, self.word_2]))

        paradigms = get_paradigms(self.word_1)

        print(paradigms)

        self.assertTrue(isinstance(paradigms, dict))

    def test_grammatical_class_index_words(self):
        usl_a = usl(Text([self.word_1, self.word_3, self.word_2]))
        usl_b = usl(Text([self.word_2, self.word_5]))

        eo_index = grammatical_class_index(usl_a, usl_b, 'EO', Word)
        oo_index = grammatical_class_index(usl_a, usl_b, 'OO', Word)

        print("EO index: " + str(eo_index))
        print("OO index: " + str(oo_index))

        self.assertTrue(eo_index != 1, "Two different USLs don't have an EO index of 1")
        self.assertTrue(oo_index != 1, "Two different USLs don't have an EO index of 1")

    def test_paradigm_class_index_word(self):
        usl_a = usl(Text([self.word_1, self.word_3, self.word_2]))
        usl_b = usl(Text([self.word_2, self.word_5]))

        eo_index = paradigmatic_equivalence_class_index(usl_a, usl_b, 1, 'EO')
        oo_index = paradigmatic_equivalence_class_index(usl_a, usl_b, 1, 'OO')

        print("EO index: " + str(eo_index))
        print("OO index: " + str(oo_index))

        self.assertTrue(eo_index != 1, "Two different USLs don't have an EO index of 1")
        self.assertTrue(oo_index != 1, "Two different USLs don't have an EO index of 1")


if __name__ == '__main__':
    unittest.main()
