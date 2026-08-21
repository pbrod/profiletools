# profiletools

[![PyPI](https://img.shields.io/pypi/v/profiletools.svg)](https://pypi.org/project/profiletools/)
![Python Versions](https://img.shields.io/pypi/pyversions/profiletools.svg)
[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD--3--Clause-blue.svg)](LICENSE)
[![Downloads](https://img.shields.io/badge/dynamic/json?url=https://pypistats.org/api/packages/profiletools/recent&label=Downloads%20per%20month&query=$.data.last_month&color=blue)](https://pypistats.org/packages/profiletools)

Lightweight, decorator-based profiling utilities for Python.

`profiletools` provides simple timing utilities, cProfile integration, and optional line-by-line profiling through `line_profiler`.

It is designed to be:

- minimal  
- dependency-light  
- easy to use  
- suitable for both quick diagnostics and deeper profiling  

---

## 🚀 Quick Start
 
```python
from profiletools import timefun
 
@timefun
def slow_function():
    for i in range(100_000):
        _ = i**2

slow_function()
```


Output:
```text
@timefun:slow_function took 0.001234 seconds
```


Choose the tool that matches your needs:
- `@timefun` for lightweight timing
- `TimeWith` for timing arbitrary code blocks
- `@do_cprofile` for function-level profiling with `cProfile`
- `@do_profile` for line-by-line profiling with `line_profiler`

---

## ✨ Features

- `timefun` — measure execution time of any function  
- `TimeWith` — time code blocks with checkpoints  
- `do_cprofile` — function-level profiling using `cProfile`  
- `do_profile` — line-by-line profiling (optional dependency: `line_profiler`)  

Supports profiling:

- standalone functions  
- class methods  
- additional functions via `follow=`  
- all methods of a class via `follow_all_methods=True`  
- direct decorator application or manual wrapping  

---

## 🤔 Why profiletools?
 
`profiletools` provides a simple decorator-based interface on top of
Python profiling tools.
 
| Tool | Purpose |
|--------|----------|
| `timefun` | Lightweight timing of functions |
| `TimeWith` | Timing code blocks with checkpoints |
| `do_cprofile` | Easy integration with `cProfile` |
| `do_profile` | Line-by-line profiling using `line_profiler` |

---

## 📥 Installation

### Basic installation

```bash
pip install profiletools
```

### Enable line-by-line profiling

```bash
pip install profiletools[line]
```

The `line_profiler` dependency is optional and only required when using `@do_profile`.

---

## 📚 Usage Examples

---

## ⏱️ Timing a function with `@timefun`

```python
from profiletools import timefun

@timefun
def expensive_function():
    for x in range(50000):
        i = x**3
    return i

expensive_function()
```

Output:

```
@timefun:expensive_function took 0.012345 seconds
```

---

## ⏱️ Timing a block with `TimeWith`

```python
from profiletools import TimeWith

with TimeWith("expensive block") as timer:
    for x in range(50000):
        i = x**3
    timer.checkpoint("halfway done")

    for x in range(50000):
        i = x**4
    timer.checkpoint("finished second part")
```

Example output:

```
expensive block halfway done took 0.123456 seconds
expensive block finished second part took 0.234567 seconds
expensive block finished took 0.234890 seconds
```

---

## 🧵 Profiling a function with `@do_cprofile`

```python
import time
from profiletools import do_cprofile

def calculate(x):
    time.sleep(0.1)
    return x**3

@do_cprofile
def expensive_function():
    for x in range(10):
        i = calculate(x)
    return i

expensive_function()
```

Produces output similar to:

```
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
       10    0.000    0.000    1.003    0.100 demo.py:46(calculate)
        1    0.000    0.000    1.003    1.003 demo.py:50(expensive_function)
       10    1.003    0.100    1.003    0.100 {built-in method time.sleep}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
```

---

## 📊 Line-by-line profiling with `@do_profile`

> Requires `line_profiler` installed.

### Profile a function and follow another function

```python
from profiletools import do_profile

def helper():
    yield from range(5000)

@do_profile(follow=[helper])
def expensive_function():
    for x in helper():
        i = x**3
    return i

expensive_function()
```

Output includes both functions:

```
Function: expensive_function at line 63

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    63                                           @do_profile(follow=[helper])
    64                                           def expensive_function():
    65      5001      28256.0      5.7     65.2      for x in helper():
    66      5000      15103.0      3.0     34.8          i = x**3
    67         1          3.0      3.0      0.0      return i


Function: helper at line 59

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
    59                                           def helper():
    60         1         49.0     49.0    100.0      yield from range(5000)
```

---

## 📦 Profiling class methods

### Follow a class method by name

```python
from profiletools import do_profile

class Worker:
    @do_profile(follow=["_numbers"])
    def compute(self):
        for x in self._numbers():
            i = x**4
        return i

    def _numbers(self):
        yield from range(5000)

Worker().compute()
```

---

## 🧩 Profile all methods of a class

```python
from profiletools import do_profile

class Worker:
    @do_profile(follow_all_methods=True)
    def compute(self):
        for x in self._numbers():
            for y in self._small_numbers():
                i = x ^ y
        return i

    def _numbers(self):
        yield from range(5000)

    def _small_numbers(self):
        yield from range(50)

Worker().compute()
```

This automatically profiles:

- `compute`
- `_numbers`
- `_small_numbers`

```
Function: Worker.compute at line 100

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
   100                                               @do_profile(follow_all_methods=True)
   101                                               def compute(self):
   102      5001      36921.0      7.4      1.4          for x in self._numbers():
   103    255000    1760586.0      6.9     66.9              for y in self._small_numbers():
   104    250000     835163.0      3.3     31.7                  i = x ^ y
   105         1          5.0      5.0      0.0          return i

Total time: 4.3e-06 s

Function: Worker._numbers at line 107

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
   107                                               def _numbers(self):
   108         1         43.0     43.0    100.0          yield from range(5000)

Total time: 0.003679 s

Function: Worker._small_numbers at line 110

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
   110                                               def _small_numbers(self):
   111      5000      36790.0      7.4    100.0          yield from range(50)
```

---

## 🔧 Using `do_profile` without a decorator

```python
from profiletools import do_profile

class Worker:
    def compute(self):
        for x in self._numbers():
            i = x**3
        return i

    def _numbers(self):
        yield from range(5000)

worker = Worker()
do_profile(follow=[worker._numbers])(worker.compute)()
```

Will profile:

- `compute`
- `_numbers`

---

## 📄 License

This project is licensed under the **BSD-3-Clause License**.  
See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Pull requests are welcome.

If you discover a bug or would like to propose an enhancement, please
open an issue or submit a pull request.

