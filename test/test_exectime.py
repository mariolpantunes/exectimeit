# coding: utf-8

__author__ = 'Mário Antunes'
__version__ = '0.1'
__email__ = 'mariolpantunes@gmail.com'
__status__ = 'Development'


import time
import unittest
import exectime.timeit as timeit


@timeit.exectime(3)
def one_second():
    time.sleep(1)


@timeit.exectime(3)
def two_second():
    time.sleep(2)


class TestExecTime(unittest.TestCase):
    def test_decorator_one_second(self):
        t, _, _ = one_second()
        desired = 1.0
        self.assertAlmostEqual(t, desired, 2)
    
    def test_decorator_two_second(self):
        t, _, _ = two_second()
        desired = 2.0
        self.assertAlmostEqual(t, desired, 2)


if __name__ == '__main__':
    unittest.main()