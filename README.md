# profiletools

Lightweight decorators and context managers for profiling Python code.

## Features

- `@do_profile` — line-by-line profiling via `line_profiler` (optional dependency)
- `@do_cprofile` — function-level profiling via `cProfile`
- `@timefun` — simple timing decorator
- `TimeWith` — timing context manager with checkpoints

## Installation

```bash
pip install profiletools
# optional line_profiler support
pip install profiletools[line]
