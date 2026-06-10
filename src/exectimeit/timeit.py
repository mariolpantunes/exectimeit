__author__ = "Mário Antunes"
__version__ = "0.2.0"
__email__ = "mario.antunes@ua.pt"
__status__ = "Development"

# coding: utf-8

"""
Core implementation of exectimeit.
Implements the timeit function and exectime decorator.
"""


import functools
import math
import time
from typing import Any, Callable, NamedTuple, TypeVar, cast

T = TypeVar("T")


class ExecTimeResult(NamedTuple):
    """
    Represents the result of an execution time measurement.

    Attributes:
        time (float): The estimated mean execution time of a single run in seconds.
        rse (float): The Residual Standard Error (RSE) of the linear regression in seconds.
        value (Any): The return value of the function from the timing trials.
    """

    time: float
    rse: float
    value: Any


def linear_regression(x: list[float], y: list[float]) -> tuple[float, float]:
    """
    Computes the slope (m) and intercept (b) of a simple linear regression y = m * x + b.

    Args:
        x (list[float]): The independent variable values (number of executions).
        y (list[float]): The dependent variable values (durations).

    Returns:
        tuple[float, float]: (slope, intercept)
    """
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xx = sum(xi * xi for xi in x)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))

    denom = n * sum_xx - sum_x * sum_x
    if denom == 0:
        raise ValueError("Denominator is zero in linear regression (all x values are equal)")

    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n
    return slope, intercept


def RSE(y: list[float], y_hat: list[float]) -> float:
    """
    Return the Root Square Error (RSE) or Residual Standard Error:
    $$
    rse = \\sqrt{\\frac{\\sum (y - \\hat{y})^{2}}{N - 2}}
    $$

    Args:
        y     (list[float]): actual duration values
        y_hat (list[float]): predicted duration values

    Returns:
        float: Root Square Error (RSE)
    """
    n = len(y)
    if n <= 2:
        raise ValueError("RSE requires at least 3 elements to compute degree of freedom (N-2)")

    rss = sum((yi - yhat_i) ** 2 for yi, yhat_i in zip(y, y_hat))
    rse = math.sqrt(rss / (n - 2))
    return rse


# Type for the internal runner: takes (function, args, kwargs) and returns the result of the function
RunnerCallable = Callable[[Callable[..., Any], tuple[Any, ...], dict[str, Any]], Any]

_runners: dict[int, RunnerCallable] = {}


def _get_runner(k: int) -> RunnerCallable:
    """
    Generates and caches an unrolled runner function that executes a target callable k times.
    If k > 100, falls back to a standard loop to prevent code bloat.

    Args:
        k (int): Number of executions.

    Returns:
        RunnerCallable: The runner function signature `runner(fn, args, kwargs)`.
    """
    if k not in _runners:
        if k <= 100:
            code = "def runner(fn, args, kwargs):\n"
            if k == 1:
                code += "    return fn(*args, **kwargs)\n"
            else:
                code += "    rv = fn(*args, **kwargs)\n"
                for _ in range(k - 1):
                    code += "    fn(*args, **kwargs)\n"
                code += "    return rv\n"
            local_vars: dict[str, Any] = {}
            exec(code, {}, local_vars)
            _runners[k] = cast(RunnerCallable, local_vars["runner"])
        else:
            # Fallback loop runner for large k to avoid massive compiled functions
            def loop_runner(fn: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
                rv = fn(*args, **kwargs)
                for _ in range(k - 1):
                    fn(*args, **kwargs)
                return rv

            _runners[k] = loop_runner
    return _runners[k]


def timeit(n: int, fn: Callable[..., T], *args: Any, **kwargs: Any) -> ExecTimeResult:
    """
    Measures the execution time using a stable algorithm
    that minimizes systematic and random errors.

    The algorithm is an implementation of the method proposed by Carlos Moreno
    and Sebastian Fischmeister in:
    "Accurate Measurement of Small Execution Times—Getting Around Measurement Errors"
    (https://doi.org/10.1109/LES.2017.2654160)

    The duration of executing the function k times is modeled as:
    $$
    T_k = k \\cdot t_{exec} + t_{overhead} + \\epsilon_k
    $$
    where $$t_{exec}$$ is the actual execution time, $$t_{overhead}$$ is the fixed
    measurement overhead (timer calls), and $$\\epsilon_k$$ is the random error.
    Using simple linear regression, the slope represents $$t_{exec}$$.

    Args:
        n       (int): number of repetitions (recommended >= 3)
        fn (Callable): the function to measure
        args         : positional arguments for fn
        kwargs       : keyword arguments for fn

    Returns:
        ExecTimeResult: NamedTuple containing:
            - time (float): mean execution time in seconds
            - rse (float): residual standard error in seconds
            - value (T): return value of the function call
    """
    if n <= 2:
        raise RuntimeError("Number of iterations too low, we recommend n equal or greater than 3.")

    # warm-up: execute and discard time
    _ = fn(*args, **kwargs)

    # durations array
    durations: list[float] = []
    rv: T | None = None

    # Measure durations for k = 1 to n
    for k in range(1, n + 1):
        runner = _get_runner(k)
        begin = time.perf_counter_ns()
        rv = cast(T, runner(fn, args, kwargs))
        end = time.perf_counter_ns()
        durations.append(float(end - begin))

    # Perform linear regression to find slope (m) and intercept (b)
    x = [float(xi) for xi in range(1, n + 1)]
    m, b = linear_regression(x, durations)

    if m <= 0:
        raise RuntimeError("Estimated Negative execution time, please increase the number of folds.")

    # Predicted values for RSE
    y_hat = [xi * m + b for xi in x]
    rse_val = RSE(durations, y_hat)

    return ExecTimeResult(m / 1e9, rse_val / 1e9, cast(T, rv))


def exectime(n: int = 4) -> Callable[[Callable[..., T]], Callable[..., ExecTimeResult]]:
    """
    Implements a decorator that executes exectime.timeit on
    a specified function.

    Args:
        n (int): number of repetitions (default: 4)

    Returns:
        Callable: python decorator for exectime.timeit
    """

    def decorate(fn: Callable[..., T]) -> Callable[..., ExecTimeResult]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> ExecTimeResult:
            return timeit(n, fn, *args, **kwargs)

        return wrapper

    return decorate
