import unittest
from unittest.mock import patch
from src.sketch_generation.generation import *
from math import comb
from random import randint

Feature = Union[dlplan.Boolean, dlplan.Numerical]


class SketchGeneration(unittest.TestCase):
    def check_len_sets(self, number_b, number_n, number_fs):
        n_fs = ["n1"]*number_n
        b_fs = ["b1"]*number_b
        i = 0
        for f in get_feature_sets(b_fs, n_fs, number_fs):
            i += 1
        self.assertEqual(i, comb(number_b + number_n, number_fs))

    def test_feature_sets(self):
        for i in range(10):
            b = randint(1, 10)
            n = randint(1, 10)
            self.check_len_sets(b, n, randint(1, b+n))

    def check_len_conditions(self, number_n, number_b):
        nfs = ["n1"] * number_n
        bfs = ["b1"] * number_b
        self.assertEqual(pow(3, number_n + number_b), len(list(possible_conditions(bfs, nfs))))

    def test_condition_len(self):
        for i in range(10):
            b = randint(1, 10)
            n = randint(1, 10)
            self.check_len_sets(b, n, randint(1, b + n))

    def check_n_rules(self, number_n, number_b):
        nfs = ["n1"] * number_n
        bfs = ["b1"] * number_b

    def test_n_rules(self):
        print(len(list(generate_rules(['b']*26, ['n']*62))))


    def test_condition_generation(self):
        self.assertEqual([[]], list(possible_conditions([], [])))

        pcs = [[CBAny('b1'), CBAny('b2')],
               [CBAny('b1'), CNegative('b2')],
               [CBAny('b1'), CPositive('b2')],
               [CNegative('b1'), CBAny('b2')],
               [CNegative('b1'), CNegative('b2')],
               [CNegative('b1'), CPositive('b2')],
               [CPositive('b1'), CBAny('b2')],
               [CPositive('b1'), CNegative('b2')],
               [CPositive('b1'), CPositive('b2')]]
        self.assertEqual(pcs, list(possible_conditions(['b1', 'b2'], [])))

        pcs2 = [[CNAny('n1'), CNAny('n2')],
                [CNAny('n1'), CZero('n2')],
                [CNAny('n1'), CGreater('n2')],
                [CZero('n1'), CNAny('n2')],
                [CZero('n1'), CZero('n2')],
                [CZero('n1'), CGreater('n2')],
                [CGreater('n1'), CNAny('n2')],
                [CGreater('n1'), CZero('n2')],
                [CGreater('n1'), CGreater('n2')]]
        self.assertEqual(pcs2, list(possible_conditions([], ['n1', 'n2'])))

        pcs3 = [[CNAny('n1'), CBAny('b1')],
                [CNAny('n1'), CNegative('b1')],
                [CNAny('n1'), CPositive('b1')],
                [CZero('n1'), CBAny('b1')],
                [CZero('n1'), CNegative('b1')],
                [CZero('n1'), CPositive('b1')],
                [CGreater('n1'), CBAny('b1')],
                [CGreater('n1'), CNegative('b1')],
                [CGreater('n1'), CPositive('b1')]]

        self.assertEqual(pcs3, list(possible_conditions(['b1'], ['n1'])))


if __name__ == '__main__':
    unittest.main()
