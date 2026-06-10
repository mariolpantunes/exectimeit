__author__ = "Mário Antunes"
__version__ = "0.2.0"
__email__ = "mario.antunes@ua.pt"
__status__ = "Development"

# coding: utf-8

"""
Substantial unit tests for exectimeit.
Covers mock-timing math, real-timing tests, decorator metadata, and error handling.
"""


import time
import unittest
from unittest.mock import patch

from exectimeit.timeit import RSE, ExecTimeResult, exectime, linear_regression, timeit

# State for negative time testing
execution_counter = 0


def dummy_fn():
    pass


def sleeping_fn(t: float = 0.001):
    time.sleep(t)
    return "done"


def stateful_fn(threshold: int = 3):
    global execution_counter
    # Simulate step-change in performance to trigger negative slope or high noise
    if execution_counter < threshold:
        time.sleep(0.005)
    else:
        time.sleep(0.001)
    execution_counter += 1
    return execution_counter


@exectime(3)
def decorated_fn(x: int, y: int) -> int:
    """Docstring for decorated_fn."""
    return x + y


class MockTimer:
    """
    Deterministic mock timer to simulate exact execution times and timer overheads.
    T_k = k * t_exec + t_overhead.
    """

    t_exec: float
    t_overhead: float
    current_time: float
    k: int
    state: int

    def __init__(self, t_exec: float, t_overhead: float):
        self.t_exec = t_exec
        self.t_overhead = t_overhead
        self.current_time = 1000.0
        self.k = 1
        self.state = 0  # 0: start of timing, 1: end of timing

    def __call__(self) -> float:
        if self.state == 0:
            self.state = 1
            return self.current_time
        else:
            self.state = 0
            duration = self.k * self.self_exec_duration() + self.t_overhead
            self.current_time += duration
            self.k += 1
            return self.current_time

    def self_exec_duration(self) -> float:
        return self.t_exec


class TestExecTime(unittest.TestCase):
    def test_mock_timing_precision(self):
        """
        Verify that our linear regression and RSE math correctly reconstructs
        the exact slope and yields zero RSE under deterministic simulated timings.
        """
        # True execution time = 1234.0 ns, overhead = 567.0 ns
        mock_timer = MockTimer(1234.0, 567.0)

        with patch("time.perf_counter_ns", side_effect=mock_timer):
            res = timeit(5, dummy_fn)

            # Reconstructed slope should be exactly 1234 ns (in seconds)
            self.assertAlmostEqual(res.time, 1234.0 / 1e9, places=15)
            # RSE should be 0.0 (no noise)
            self.assertAlmostEqual(res.rse, 0.0, places=15)

    def test_named_tuple_unpacking(self):
        """
        Verify that ExecTimeResult supports both named attribute access
        and backward-compatible tuple unpacking.
        """
        mock_timer = MockTimer(100.0, 50.0)
        with patch("time.perf_counter_ns", side_effect=mock_timer):
            res = timeit(3, dummy_fn)

            # Attribute access
            self.assertAlmostEqual(res.time, 100.0 / 1e9)
            self.assertAlmostEqual(res.rse, 0.0)
            self.assertIsNone(res.value)

            # Tuple unpacking
            t, rse, val = res
            self.assertAlmostEqual(t, 100.0 / 1e9)
            self.assertAlmostEqual(rse, 0.0)
            self.assertIsNone(val)

    def test_decorator_metadata_preservation(self):
        """
        Verify that the @exectime decorator uses functools.wraps
        to preserve the original function's name and docstring.
        """
        self.assertEqual(decorated_fn.__name__, "decorated_fn")
        self.assertEqual(decorated_fn.__doc__, "Docstring for decorated_fn.")

    def test_decorator_execution(self):
        """
        Verify that calling a decorated function executes the timing model
        and returns the NamedTuple.
        """
        mock_timer = MockTimer(500.0, 100.0)
        with patch("time.perf_counter_ns", side_effect=mock_timer):
            res = decorated_fn(2, 3)
            self.assertIsInstance(res, ExecTimeResult)
            self.assertAlmostEqual(res.time, 500.0 / 1e9)
            self.assertEqual(res.value, 5)

    def test_error_n_too_low(self):
        """
        Verify that n <= 2 raises a RuntimeError.
        """
        with self.assertRaises(RuntimeError) as ctx:
            _ = timeit(2, dummy_fn)
        self.assertIn("iterations too low", str(ctx.exception))

        with self.assertRaises(RuntimeError):
            _ = timeit(1, dummy_fn)

    def test_negative_slope_exception(self):
        """
        Verify that a negative estimated execution time (negative slope)
        correctly raises a RuntimeError.
        """
        # We need to return:
        # k=1: begin=0, end=1000
        # k=2: begin=0, end=500
        # k=3: begin=0, end=100
        mock_seq = [0, 1000, 0, 500, 0, 100]
        with patch("time.perf_counter_ns", side_effect=mock_seq):
            with self.assertRaises(RuntimeError) as ctx:
                _ = timeit(3, dummy_fn)
            self.assertIn("Negative execution time", str(ctx.exception))

    def test_real_timer_fast_sleep(self):
        """
        Verify the timing logic works under real system timers (perf_counter_ns)
        using small sleep times (1ms) to keep execution fast.
        """
        res = timeit(3, sleeping_fn, 0.001)
        self.assertGreater(res.time, 0.0)
        self.assertEqual(res.value, "done")
        # Slope should be roughly in the neighborhood of 0.001 seconds
        self.assertAlmostEqual(res.time, 0.001, delta=0.005)

    def test_linear_regression_helper(self):
        """
        Directly test the linear regression helper with known data.
        """
        x = [1.0, 2.0, 3.0, 4.0]
        y = [2.0, 4.0, 6.0, 8.0]
        m, b = linear_regression(x, y)
        self.assertAlmostEqual(m, 2.0)
        self.assertAlmostEqual(b, 0.0)

        # Collinear inputs on x should raise ValueError
        with self.assertRaises(ValueError):
            _ = linear_regression([1.0, 1.0], [2.0, 3.0])

    def test_rse_helper_boundary(self):
        """
        Verify the RSE helper error conditions.
        """
        with self.assertRaises(ValueError):
            _ = RSE([1.0, 2.0], [1.1, 1.9])


if __name__ == "__main__":
    unittest.main()
