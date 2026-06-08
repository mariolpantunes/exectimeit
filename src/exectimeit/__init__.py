"""
This library implements a wrapper that can be used to accurately measure small execution times.
This work is an implementation of the method described in this work:

C. Moreno and S. Fischmeister, "Accurate Measurement of Small Execution Times—Getting Around Measurement Errors,"
in IEEE Embedded Systems Letters, vol. 9, no. 1, pp. 17-20, March 2017, doi: 10.1109/LES.2017.2654160.
"""

from exectimeit.timeit import ExecTimeResult, exectime, timeit

__all__ = ["timeit", "exectime", "ExecTimeResult"]
