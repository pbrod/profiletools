from importlib.util import find_spec

import pytest

from profiletools import do_profile
from profiletools.testing import capture_stdout_and_stderr

from .helpers import (
    ExpensiveClass4,
    _extract_do_profile_results,
    _get_number,
    disable_profiler_cleanup,
    row_finder,
)

HAS_LINE_PROFILER = find_spec("line_profiler") is not None
FIRST_LINE = "Line #      Hits         Time  Per Hit   % Time  Line Contents"


def test_do_profile_noop_without_line_profiler():
    @do_profile()
    def f(x):
        return x - 1

    assert f(2) == 1


#  @pytest.mark.skip('Suspect this test fucks up coverage stats.')
@pytest.mark.skipif(not HAS_LINE_PROFILER, reason="LineProfiler is not installed.")
class TestDoProfile:
    def test_on_function_and_follow_function(self):
        @do_profile(follow=[_get_number])
        def expensive_function():
            for x in _get_number():
                i = x**3
            return i

        with capture_stdout_and_stderr() as out:
            expensive_function()
        results = _extract_do_profile_results(out[0])
        msg = str(results)

        assert len(results) > 0, msg
        assert results[0] == FIRST_LINE, msg

        find_row = row_finder(results)
        find_row("def _get_number():")
        find_row("@do_profile(follow=[_get_number])")

        disable_profiler_cleanup()

    def test_on_class_method_and_follow_function(self):
        class ExpensiveClass1:
            @do_profile(follow=[_get_number])
            def expensive_method1(self):
                for x in _get_number():
                    i = x ^ 6
                return i

        with capture_stdout_and_stderr() as out:
            ExpensiveClass1().expensive_method1()
        results = _extract_do_profile_results(out[0])
        print(results)
        msg = str(results)
        assert len(results) > 0, msg
        assert results[0] == FIRST_LINE, msg

        find_row = row_finder(results)
        find_row("def _get_number():")
        find_row("@do_profile(follow=[_get_number])")

        disable_profiler_cleanup()

    def test_on_class_method_and_follow_class_method(self):
        class ExpensiveClass2:
            n = 5000
            """You can not put class method _get_number2 directly into follow
            instead you must pass its name as a string:
            """

            @do_profile(follow=["_get_number2"])
            def expensive_method2(self):
                for x in self._get_number2():
                    i = x**4
                return i

            def _get_number2(self):
                yield from range(self.n)

        with capture_stdout_and_stderr() as out:
            ExpensiveClass2().expensive_method2()
        results = _extract_do_profile_results(out[0])
        print(results)
        msg = str(results)
        assert len(results) > 0, msg
        assert results[0] == FIRST_LINE, msg

        find_row = row_finder(results)
        find_row('@do_profile(follow=["_get_number2"])')
        assert find_row("def expensive_method2(self):")[1] == 0, msg
        find_row("def _get_number2(self):")

        disable_profiler_cleanup()

    def test_on_all_class_methods(self):
        class ExpensiveClass3:
            n = 5000
            n2 = 50
            """Profile all methods of ExpensiveClass3"""

            @do_profile(follow_all_methods=True)
            def expensive_method3(self):
                for x in self._get_number3():
                    for _ in self._get_number32():
                        i = x ^ 9
                return i

            def _get_number3(self):
                yield from range(self.n)

            def _get_number32(self):
                yield from range(self.n2)

        with capture_stdout_and_stderr() as out:
            ExpensiveClass3().expensive_method3()
        results = _extract_do_profile_results(out[0])
        msg = str(results)
        assert len(results) > 0, msg
        assert results[0] == FIRST_LINE

        find_row = row_finder(results)
        find_row("@do_profile(follow_all_methods=True)")
        row = find_row("def expensive_method3(self):")
        assert row[1] == 0
        assert row[2] == 0

        find_row("def _get_number3(self):")

        disable_profiler_cleanup()

    def test_on_all_class_methods_without_decorator(self):
        with capture_stdout_and_stderr() as out:
            cls = ExpensiveClass4()
            do_profile(follow=[cls._get_number4])(cls.expensive_method4)()
        results = _extract_do_profile_results(out[0])
        print(results)
        msg = str(results)
        assert len(results) > 0, msg
        assert results[0] == FIRST_LINE, msg
        find_row = row_finder(results)
        find_row("def expensive_method4(self):")
        row = find_row("for x in self._get_number4():")
        assert row[1] == 5001, msg
        assert row[2] > 10, msg

        find_row("def _get_number4(self):")

        disable_profiler_cleanup()

    def test_follow_all_methods_excludes_inherited_methods(self):
        class Base:
            def base_method(self):
                yield from range(10)

        class Child(Base):
            @do_profile(
                follow_all_methods=True,
                include_inherited_methods=False,
            )
            def run(self):
                for _ in self.derived_method():
                    pass

            def derived_method(self):
                yield from range(10)

        with capture_stdout_and_stderr() as out:
            Child().run()

        results = _extract_do_profile_results(out[0])

        find_row = row_finder(results)

        # Own method should be present
        find_row("def derived_method(self):")

        # Inherited method should not be present
        inherited = [
            row
            for row in results
            if isinstance(row, tuple) and row[5].strip() == "def base_method(self):"
        ]
        assert inherited == []

        disable_profiler_cleanup()

    def test_follow_all_methods_includes_inherited_methods(self):
        class Base:
            def base_method(self):
                yield from range(10)

        class Child(Base):
            @do_profile(
                follow_all_methods=True,
                include_inherited_methods=True,
            )
            def run(self):
                for _ in self.base_method():
                    pass

            def derived_method(self):
                yield from range(10)

        with capture_stdout_and_stderr() as out:
            Child().run()

        results = _extract_do_profile_results(out[0])

        find_row = row_finder(results)

        # Own method should be present
        find_row("def derived_method(self):")

        # Inherited method should also be present
        find_row("def base_method(self):")

        disable_profiler_cleanup()
