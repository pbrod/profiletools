# profiletools

[![PyPI](https://img.shields.io/pypi/v/profiletools.svg)](https://pypi.org/project/profiletools/)
![Python Versions](https://img.shields.io/pypi/pyversions/profiletools.svg)
[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD--3--Clause-blue.svg)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/profiletools.svg)](https://pypistats.org/packages/profiletools)
[![Downloads](https://img.shields.io/badge/dynamic/json?url=https://pypistats.org/api/packages/profiletools/recent&label=Downloads%20per%20month&query=$.data.last_month&color=blue)](https://pypistats.org/packages/profiletools)

Lightweight, decorator-based profiling utilities for Python.  
`profiletools` provides simple timing tools, cProfile integration, and optional line-by-line profiling via `line_profiler`.

It is designed to be:

- minimal  
- dependency-light  
- easy to use  
- suitable for both quick diagnostics and deeper profiling  

---

## Features

- `timefun` — measure execution time of any function  
- `TimeWith` — time code blocks with checkpoints  
- `do_cprofile` — function-level profiling using `cProfile`  
- `do_profile` — line-by-line profiling (optional dependency: `line_profiler`)  

Supports profiling:

- standalone functions  
- class methods  
- helper functions via `follow=`  
- all methods of a class via `follow_all_methods=True`  
- direct decorator application or manual wrapping  

---

## Installation

### Basic installation

```bash
pip install profiletools
```

### Enable line-by-line profiling

```bash
pip install profiletools[line]
```

This installs `line_profiler`, which powers `@do_profile`.

---

## Usage Examples

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
from profiletools import do_cprofile

@do_cprofile
def expensive_function():
    for x in range(50000):
        i = x**3
    return i

expensive_function()
```

Produces standard `cProfile` output:

```
         50000    0.012    0.000    0.012    0.000 example.py:10(expensive_function)
             1    0.000    0.000    0.012    0.012 {built-in method builtins.range}
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
Line #      Hits         Time  Per Hit   % Time  Line Contents
...
def helper():
...
@do_profile(follow=[helper])
...
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

---

## License

This project is licensed under the **BSD-3-Clause License**.  
See the [LICENSE](LICENSE) file for details.

---

## Contributing

Pull requests are welcome.  
If you find a bug or want to propose an enhancement, open an issue on GitHub.

