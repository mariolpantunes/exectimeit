# coding: utf-8

__author__ = 'Mário Antunes'
__version__ = '0.1'
__email__ = 'mariolpantunes@gmail.com'
__status__ = 'Development'


import math
import time
import numpy as np


def RSE(y, y_hat):
    RSS = np.sum(np.square(y - y_hat))
    rse = math.sqrt(RSS / (len(y) - 2))
    return rse


def timeit(n, fn, *args, **kwargs):
    # execute first time
    begin = time.perf_counter()
    rv = fn(*args, **kwargs)
    end = time.perf_counter()

    # durations list 
    durations = [end-begin]
    
    if n < 3:
        for i in range(1, n):
            begin = time.perf_counter()
            fn(*args, **kwargs)
            end = time.perf_counter()
            durations.append(end-begin)
        return np.mean(durations), np.std(durations), rv
    else:
        for i in range(1, n):
            d = 0
            for _ in range(i+1):
                begin = time.perf_counter()
                fn(*args, **kwargs)
                end = time.perf_counter()
                d += end-begin

            durations.append(d)

        x = np.arange(1, n+1)
        m, b = np.polyfit(x, durations, 1)

        y_hat = x*m+b

        return m, RSE(durations, y_hat), rv


def exectime(n=3):
    def decorate(fn):
        def wrapper(*args, **kwargs):
            return timeit(n, fn, *args, **kwargs)
        return wrapper
    return decorate