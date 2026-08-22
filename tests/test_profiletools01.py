from profiletools import TimeWith, do_cprofile, timefun
from profiletools.testing import capture_stdout_and_stderr
from helpers import (
    _expensive_function,
    _extract_do_cprofile_results,
    _get_number,
)


def test_timefun_runs():
    @timefun
    def f(x):
        return x * 2

    assert f(3) == 6


def test_TimeWith_context():
    with TimeWith("test") as tw:
        assert tw.elapsed >= 0.0


def test_do_cprofile_runs():
    @do_cprofile()
    def f(x):
        return x + 1

    assert f(1) == 2


class TestTimeFun:
    def test_decorate_function(self):
        @timefun
        def expensive_function():
            for x in _get_number():
                i = x**3
            return i

        with capture_stdout_and_stderr() as out:
            expensive_function()
        msg = str(out)
        # print(out)
        assert len(out), msg
        assert out[0].startswith("@timefun:expensive_function took"), msg
        time = float(out[0].split("took")[1].strip().split(" ")[0])
        assert time > 0

    def test_direct_on_function(self):
        with capture_stdout_and_stderr() as out:
            timefun(_expensive_function)()
        msg = str(out)
        # print(out)
        assert len(out), msg
        assert out[0].startswith("@timefun:_expensive_function took"), msg
        time = float(out[0].split("took")[1].strip().split(" ")[0])
        assert time > 0


class TestTimeWith:
    def test_timing_with_context_manager(self):
        # prints something like:
        # fancy thing done with something took 0.582462072372 seconds
        # fancy thing done with something else took 1.75355315208 seconds
        # fancy thing finished took 1.7535982132 seconds
        with capture_stdout_and_stderr() as out:
            with TimeWith("fancy thing") as timer:
                _expensive_function()
                timer.checkpoint("done with something")
                _expensive_function()
                _expensive_function()
                timer.checkpoint("done with something else")

        msg = str(out)
        # print(out)
        assert len(out), msg
        out0 = out[0].split("\n")
        assert out0[0].startswith("fancy thing done with something took"), msg
        assert out0[1].startswith("fancy thing done with something else took"), msg
        assert out0[2].startswith("fancy thing finished took"), msg

    def test_direct_timing(self):
        # or directly
        with capture_stdout_and_stderr() as out:
            timer = TimeWith("fancy thing")
            _expensive_function()
            timer.checkpoint("done with something")

        msg = str(out)
        # print(out)
        assert len(out), msg
        assert out[0].startswith("fancy thing done with something took"), msg


class TestDoCProfile:
    def test_on_function(self):
        @do_cprofile()
        def expensive_function():
            for x in _get_number():
                i = x**3
            return i

        with capture_stdout_and_stderr() as out:
            expensive_function()
        results = _extract_do_cprofile_results(out[0])
        print(results)
        msg = str(results)
        assert len(results), msg
        assert results[0][5].startswith("function calls in")
        assert results[0][0] > 50000
        assert (
            results[1]
            == "ncalls  tottime  percall  cumtime  percall filename:lineno(function)"
        )
        num_tests = 0
        for result in results[2:]:
            if result[5].endswith("(expensive_function)"):
                num_tests += 1
                for i in range(5):
                    assert result[i] > 0
            elif result[5].endswith("(_get_number)"):
                num_tests += 1
        if num_tests != 2:
            raise ValueError("Did not find _get_number or expensive_function")
