# <img src="assets/logo.svg" alt="logo" width="128" height="128" align="middle"> exectimeit

## Accurate Measurement of Small Execution Times

![PyPI - Version](https://img.shields.io/pypi/v/exectimeit)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/exectimeit)
![GitHub License](https://img.shields.io/github/license/mariolpantunes/exectimeit)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/mariolpantunes/exectimeit/main.yml)
![GitHub last commit](https://img.shields.io/github/last-commit/mariolpantunes/exectimeit)

Measuring small execution times (especially for fast routines $< 100$ milliseconds) in Python can be extremely challenging. The traditional way of timing code is to take the difference of system times before and after a function execution. However, this is highly susceptible to two types of errors:
1. **Random error**: Environmental noise (OS scheduling, CPU frequency scaling) causes variation. This can be reduced by averaging multiple measurements.
2. **Systematic error**: The overhead of invoking the timing instructions themselves is added to the measured duration, which is difficult to filter out.

This library implements the mathematical model proposed by **Carlos Moreno and Sebastian Fischmeister** [[1]](#1) to circumvent systematic measurement overhead.

---

## The Mathematics Behind It

Instead of measuring a single execution of a function $f$, we measure the total duration of executing the function sequentially $k$ times inside a single timing block, for $k = 1, 2, \dots, n$ (where $n$ is the number of repetitions, recommended $\ge 3$).

The total measured time $T_k$ for $k$ executions is modeled as a linear function:
$$T_k = k \cdot t_{\text{exec}} + t_{\text{overhead}} + \epsilon_k$$

Where:
* $t_{\text{exec}}$ is the actual, true execution time of a single run.
* $t_{\text{overhead}}$ is the fixed overhead of starting/stopping the timer.
* $\epsilon_k$ is the random measurement error for trial $k$.

By fitting a simple linear regression $y = m \cdot x + b$ to the data points $(k, T_k)$:
* The **slope ($m$)** represents the true single-run execution time ($t_{\text{exec}}$), entirely free of the timer's start/stop overhead.
* The **intercept ($b$)** represents the fixed timer overhead ($t_{\text{overhead}}$).
* The **Residual Standard Error (RSE)** provides a precise measure of the variation or noise:
  $$rse = \sqrt{\frac{\sum (y_i - \hat{y}_i)^2}{n - 2}}$$

To eliminate loop iteration overhead in Python, `exectimeit` dynamically compiles and caches unrolled execution routines for each $k$.

---

## Installation

```bash
pip install exectimeit
```

Or install from GitHub:
```bash
pip install git+https://github.com/mariolpantunes/exectimeit.git@main
```

---

## Usage

### Option 1: Direct function call wrapper

You can measure any callable using the `timeit` function. It returns an `ExecTimeResult` named tuple containing:
* `time`: estimated execution time per run (in seconds)
* `rse`: residual standard error of the linear fit (in seconds)
* `value`: the return value of the function

```python
from exectimeit import timeit
import time

def my_fast_function(x, y):
    time.sleep(0.001)  # Simulating some work
    return x + y

# Measure with n=5 repetitions
result = timeit(5, my_fast_function, 2, y=3)

# You can access properties by name:
print(f"Time: {result.time:.6f}s, RSE: {result.rse:.6f}s, Return value: {result.value}")

# Or unpack like a standard tuple:
t, rse, val = result
```

### Option 2: Decorator

You can decorate your functions with `@exectime` to automatically wrap them. When called, the decorated function will return the `ExecTimeResult`.

```python
from exectimeit import exectime

@exectime(n=5)
def my_decorated_function(a):
    return a * a

# Executing the function returns the measurement named tuple:
t, rse, val = my_decorated_function(10)
print(f"Time: {t:.6f}s, Return value: {val}")
```

---

## Running Unit Tests

The test suite validates both deterministic mock-timing regression math and real-time execution. Run them with:

```bash
python3 -m unittest discover -s test
```

---

## Documentation

Detailed package documentation is hosted on GitHub Pages:
[https://mariolpantunes.github.io/exectimeit/](https://mariolpantunes.github.io/exectimeit/)

To generate the docs locally:

```bash
pip install pdoc
PYTHONPATH=src pdoc --math -d google -o docs exectimeit \
  --logo "assets/logo.svg" \
  --favicon "assets/logo.svg"
```

---

## References
<a id="1">[1]</a> 
C. Moreno and S. Fischmeister, "Accurate Measurement of Small Execution Times—Getting Around Measurement Errors," in IEEE Embedded Systems Letters, vol. 9, no. 1, pp. 17-20, March 2017, doi: [10.1109/LES.2017.2654160](https://doi.org/10.1109/LES.2017.2654160).

---

## Authors

* **Mário Antunes** - [mariolpantunes](https://github.com/mariolpantunes)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
