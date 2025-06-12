# coding: utf-8

__author__ = 'Mário Antunes'
__version__ = '0.1'
__email__ = 'mariolpantunes@gmail.com'
__status__ = 'Development'


import time
import unittest
import exectimeit.timeit as timeit


# global variable for the negative test
execution=0


def f1():
    time.sleep(0.1)


def f2():
    time.sleep(0.5)


def f3(t:int=1):
    global execution
    if execution < t:
        time.sleep(1)
    else:
        time.sleep(0.1)
    execution += 1


@timeit.exectime(3)
def wf1():
    return f1()


@timeit.exectime(3)
def wf2():
    return f2()


@timeit.exectime(5)
def wf3(t:int=1):
    return f3(t)


class TestExecTime(unittest.TestCase):
    def test_f1_00(self):
        with self.assertRaises(Exception):
            _ , _, _ = timeit.timeit(1, f1)
    
    def test_f1_01(self):
        with self.assertRaises(Exception):
            _ , _, _ = timeit.timeit(2, f1)
    
    def test_f1_02(self):
        t , _, _ = timeit.timeit(3, f1)
        desired = 0.1
        self.assertAlmostEqual(t, desired, delta=0.01)
    
    def test_f1_03(self):
        t , _, _ = timeit.timeit(4, f1)
        desired = 0.1
        self.assertAlmostEqual(t, desired, delta=0.01)

    def test_f2_00(self):
        with self.assertRaises(Exception):
            _ , _, _ = timeit.timeit(1, f2)
    
    def test_f2_01(self):
        with self.assertRaises(Exception):
            _ , _, _ = timeit.timeit(2, f2)
    
    def test_f2_02(self):
        t , _, _ = timeit.timeit(3, f2)
        desired = 0.5
        self.assertAlmostEqual(t, desired, delta=0.01)
    
    def test_f2_03(self):
        t , _, _ = timeit.timeit(4, f2)
        desired = 0.5
        self.assertAlmostEqual(t, desired, delta=0.01)

    def test_decorator_f1(self):
        t, _, _ = wf1()
        desired = 0.1
        self.assertAlmostEqual(t, desired, delta=0.01)
    
    def test_decorator_f2(self):
        t, _, _ = wf2()
        desired = 0.5
        self.assertAlmostEqual(t, desired, delta=0.01)
    
    def test_negative_time_00(self):
        t, _, _ = wf3()
        desired = 0.1
        self.assertAlmostEqual(t, desired, delta=0.01)
    
    def test_negative_time_01(self):
        global execution
        execution = 0
        with self.assertRaises(Exception):
            _, _, _ = wf3(3)


if __name__ == '__main__':
    unittest.main()
