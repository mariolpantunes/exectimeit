__author__ = "Mário Antunes"
__version__ = "0.2.0"
__email__ = "mario.antunes@ua.pt"
__status__ = "Development"

"""
Simple example showcasing the usage of the exectimeit library.
"""

import time

from exectimeit import exectime, timeit


def my_fast_function(x: int, y: int) -> int:
    time.sleep(0.001)  # Simulating some work
    return x + y


@exectime(n=5)
def my_decorated_function(a: int) -> int:
    time.sleep(0.001)  # Simulating some work
    return a * a


def main() -> None:
    # 1. Direct function call wrapper
    print("--- 1. Direct Function Timing ---")
    result = timeit(5, my_fast_function, 2, y=3)
    print(f"Time: {result.time:.6f}s, RSE: {result.rse:.6f}s, Return value: {result.value}")

    # 2. Decorator timing
    print("\n--- 2. Decorator Timing ---")
    t, rse, val = my_decorated_function(10)
    print(f"Time: {t:.6f}s, RSE: {rse:.6f}s, Return value: {val}")


if __name__ == "__main__":
    main()
