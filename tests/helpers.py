from collections.abc import Callable
from typing import Any


def disable_profiler_cleanup():
    import sys

    sys.setprofile(None)


def row_finder(rows: list[Any]) -> Callable[[str], tuple]:
    def find_row(text: str) -> tuple:
        row = next(
            (row for row in rows if isinstance(row, tuple) and row[5].strip() == text),
            None,
        )
        assert row is not None, f"Could not find row: {text!r}"
        return row

    return find_row


def _get_stats(line):
    item, _, tail = line.partition(" ")
    try:
        line_no = int(item)
    except ValueError:
        return None
    try:
        vals: list[float] = [0.0] * 4
        for i in range(4):
            item, _, tail = tail.strip().partition(" ")
            vals[i] = float(item)

        hits, time, perhit, percent_time = vals
    except ValueError:
        tail = " ".join((item, tail))
        hits, time, perhit, percent_time = 0, 0, 0.0, 0.0
    return line_no, hits, time, perhit, percent_time, tail


def _extract_do_profile_results(txt, header_start="Line #"):
    results = []
    for line in txt.split("\n"):
        line = line.strip()
        if line.startswith(header_start):
            results.append(line)
            continue
        stats = _get_stats(line)
        if stats:
            results.append(stats)

    return results


def _extract_do_cprofile_results(txt):
    """
     ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    5000001    0.326    0.000    0.326    0.000 testing.py:118(_get_number)
          1    0.858    0.858    1.184    1.184 testing.py:163(expensive_function2)
          1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
    """
    return _extract_do_profile_results(txt, header_start="ncalls")


def _get_number():
    yield from range(50000)


def _expensive_function():
    i = 0
    for x in _get_number():
        i = i ^ x
    return i


class ExpensiveClass4:
    n = 5000

    def expensive_method4(self):
        for x in self._get_number4():
            i = x**3
        return i

    def _get_number4(self):
        yield from range(self.n)
