"""
This library implements a wrapper that can be used to accuratly measure small execution times.
This work is an implementation of the method described in this work:

C. Moreno and S. Fischmeister, "Accurate Measurement of Small Execution Times—Getting Around Measurement Errors," 
in IEEE Embedded Systems Letters, vol. 9, no. 1, pp. 17-20, March 2017, doi: 10.1109/LES.2017.2654160.

Measuring execution times, especially for quick applications (< 100 milliseconds), can be quite hard.
The traditional method to do it is by simply measuring the system time before and after a function call.
This is not very robust and it is even susceptible to systematic and random measurement errors:

1. Systematic error: by invoking the measuring instruction, an unknown amount of time is added to the execution time of the target function.
This unknown amount depends on the OS, the particular implementation and other uncontrollable factors.

2. Random error: the execution time of the target function will vary to a certain degree.

We can minimize the random error by just performing multiple measurements and taking the average of those. 
However, it is much more challenging to remove the systematic error.

Carlos Moreno and Sebastian Fischmeister presented a novel technique to combat this systematic error. 
The basic idea is to measure the execution time of an incremental sequential number of function executions.
Starting to measure the time of one execution, then two executions and so on.
The overall execution time can then be obtained by taking the slope a from the fitted line.
The authors also note that this type of measurement is very robust against occasional measurements with large errors.
"""

import exectimeit.timeit