# coding: utf-8

__author__ = 'Mário Antunes'
__version__ = '0.1'
__email__ = 'mariolpantunes@gmail.com'
__status__ = 'Development'


import math
import time
import numpy as np


from typing import Callable 


def RSE(y: np.ndarray, y_hat: np.ndarray) -> float:
    """
    Return the Root Square Error (RSE):
    $$
    rse = \\sqrt{\\sum (y-\\hat{y})^{2}}
    $$

    Args:
        y     (np.ndarray): numpy array
        y_hat (np.ndarray): numpy array
    Returns:
        int: Root Square Error (RSE)
    """
    RSS = np.sum(np.square(y - y_hat))
    rse = math.sqrt(RSS / (len(y) - 2))
    return rse


def timeit(n:int, fn:Callable, *args, **kwargs) -> tuple:
    """
    Measures the execution time using a stable algorithms
    that minimizes systematic and random errors.

    The algorithm was proposed by Carlos Moreno and
    Sebastian Fischmeister here:
    https://doi.org/10.1109/LES.2017.2654160

    Args:
        n       (int): number of repetitions
        fn (Callable): numpy array
        args       ():
        kwargs     ():
    Returns:
        tuple: (mean execution time,
        variantion on execution,
        fn result)
    """
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


def exectime(n:int=4) -> Callable:
    """
    Implements a decorator that executes exectime.timeit on
    a specified function.

    Args:
        n (int): number of repetitions (default: 4)
        
    Returns:
        Callable: python decorator for exectime.timeit
    """
    def decorate(fn: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> tuple:
            return timeit(n, fn, *args, **kwargs) 
        return wrapper
    return decorate