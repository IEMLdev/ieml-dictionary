import unittest
# We use protected method _compute_rank for dependency injection
from ieml.dictionary import Dictionary, term
from ieml.dictionary.script import script as sc


class RankComputationTest(unittest.TestCase):

    # TODO: Tests for paradigms built from 3d tables

    def setUp(self):
        self.dic = Dictionary()

    def test_rank1_2d(self):
        for t in Dictionary().roots:
            self.assertTrue(t.rank == 0, "The rank of a root paradigm is not 0")

    def test_rank2_2d(self):
        term = self.dic.terms[sc("O:M:.M:M:.-+M:M:.O:M:.-")]

        root_table = term.tables[1]
        h = root_table
        term = self.dic.terms[sc([h.columns[4],h.columns[5],h.columns[3]])]

        self.assertEqual(term.rank, 2)

    def test_rank3_2d(self):
        t = self.dic.terms[sc("c.-'O:M:.-'n.o.-s.o.-',")]

        self.assertEqual(t.rank, 3)

    def test_rank4_2d(self):
        t = self.dic.terms["E:.-U:.S:M:.-l.-'"]

        self.assertEqual(t.rank, 5)

    def test_rank5_2d(self):
        term = self.dic.terms[sc("O:M:.M:M:.-+M:M:.O:M:.-")]
        # Build table for the paradigm of rank 3 (root_table.headers[1][2])
        root_table = term.tables[1]
        root_table = root_table.rows[2]
        h = root_table.rows[0]

        self.assertEqual(h.rank, 5)

    def test_paradigm_from_multiple_tables(self):
        term = self.dic.terms[sc("S:M:.e.-M:M:.u.-wa.e.-'+B:M:.e.-M:M:.a.-wa.e.-'+T:M:.e.-M:M:.i.-wa.e.-'")]
        self.assertEqual(term.rank, 1)

    def test_additive_parent_paradigm(self):
        term = self.dic.terms[sc("O:M:.M:M:.-")]
        self.assertEqual(term.rank, 1)

    def test_rank0(self):
        self.assertListEqual([t for t in Dictionary() if t.rank == 0], sorted(Dictionary().roots))

if __name__ == '__main__':
    unittest.main()
