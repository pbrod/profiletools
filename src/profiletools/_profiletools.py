"""
Profiling and timing utilities.

This module provides several levels of performance analysis:

* ``timefun`` for lightweight timing of function calls.
* ``TimeWith`` for timing arbitrary code blocks and reporting
  intermediate checkpoints.
* ``do_cprofile`` for function-level profiling using ``cProfile``.
* ``do_profile`` for line-by-line profiling using ``line_profiler``.

Choose the simplest tool that answers the question at hand:

* Use ``timefun`` when you only need the total execution time of a
  function.
* Use ``TimeWith`` when you want to instrument sections of a function or
  workflow.
* Use ``do_cprofile`` to identify expensive functions and call paths.
* Use ``do_profile`` to determine which lines of code account for most of
  the execution time.


See also:
https://zapier.com/engineering/profiling-python-boss/
https://www.pythoncentral.io/measure-time-in-python-time-time-vs-time-clock/
"""

# mypy: disable-error-code=return-value
# mypy: disable-error-code=no-redef
from __future__ import annotations
import sys
import cProfile
import pstats
import inspect
import logging
import warnings
from collections.abc import Callable, Sequence
from functools import wraps
from timeit import default_timer as timer
from types import TracebackType
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def _add_all_class_methods(
    profiler: LineProfiler,
    instance: Any,
    except_: str = "",
    include_inherited_methods: bool = False,
) -> None:
    cls = type(instance)
    items = (
        inspect.getmembers(cls)
        if include_inherited_methods
        else cls.__dict__.items()
    )
    for name, member in items:
        if name == except_:
            continue
        if inspect.isfunction(member) or inspect.ismethod(member):
            profiler.add_function(member)
        elif isinstance(member, (staticmethod, classmethod)):
            profiler.add_function(member.__func__)


def _add_function_or_classmethod(
    profiler: LineProfiler,
    f: Any,
    args: tuple[Any, ...],
) -> None:
    if isinstance(f, str):
        if not args:
            raise ValueError(
                f"Cannot follow method name '{f}' without a bound instance."
            )
        instance = args[0]
        profiler.add_function(getattr(instance, f))
    else:
        profiler.add_function(f)


def do_profile(
    follow: Sequence[Any] = (),
    follow_all_methods: bool = False,
    include_inherited_methods: bool = False,
) -> Callable[[F], F]:
    """
    Profile a function or method using ``line_profiler``.

    Parameters
    ----------
    follow : sequence, optional
        Additional functions or methods to profile.

        If an item is a string, it is interpreted as the name of a method
        on the bound instance and resolved at call time.
    follow_all_methods : bool, optional
        If True, profile all methods on the bound instance in addition to
        the decorated method.
    include_inherited_methods : bool, optional
        When ``follow_all_methods`` is True, also include methods inherited
        from base classes. Default is False.

    Returns
    -------
    callable
        Wrapped function that prints line-by-line profiling statistics.

    Notes
    -----
    Requires the optional ``line_profiler`` dependency.

    Line profiling provides detailed timing for each executed line of code,
    but introduces significant overhead and is not suitable for benchmarking.

    See Also
    --------
    do_cprofile

    Examples
    --------
    Profile a function and a helper function:

    >>> def helper():
    ...     return sum(range(100))
    ...
    >>> @do_profile(follow=[helper])
    ... def work():
    ...     return helper()
    ...
    >>> work()  # doctest: +SKIP

    Profile all methods defined on a class:

    >>> class Worker:
    ...     @do_profile(follow_all_methods=True)
    ...     def run(self):
    ...         return self.step()
    ...
    ...     def step(self):
    ...         return sum(range(100))
    ...
    >>> Worker().run()  # doctest: +SKIP
    """
    try:
        # Lazy import to avoid LineProfiler interaction with CProfile
        from line_profiler import LineProfiler
    except ImportError:
        LineProfiler = None
        warnings.warn(
            "line_profiler not installed; do_profile will be a no-op.",
            stacklevel=2,
        )

    if LineProfiler is None:
        def inner(func: F) -> F:
            @wraps(func)
            def nothing(*args: Any, **kwargs: Any) -> Any:
                return func(*args, **kwargs)
            return nothing
        return inner

    def inner(func: F) -> F:
        @wraps(func)
        def profiled_func(*args: Any, **kwargs: Any) -> Any:
            profiler = LineProfiler()
            profiler.add_function(func)

            if follow_all_methods:
                if not args:
                    raise ValueError(
                        "follow_all_methods=True requires a bound instance."
                    )
                _add_all_class_methods(
                    profiler,
                    args[0],
                    except_=func.__name__,
                    include_inherited_methods=include_inherited_methods,
                )

            for f in follow:
                _add_function_or_classmethod(profiler, f, args)

            profiler.enable_by_count()
            try:
                return func(*args, **kwargs)
            finally:
                profiler.print_stats()

        return profiled_func

    return inner


def timefun(fun: F) -> F:
    """
    Measure and report the execution time of a function.

    Parameters
    ----------
    fun : callable
        Function to be timed.

    Returns
    -------
    callable
        Wrapped function that prints the elapsed execution time.

    Notes
    -----
    This decorator is intended for lightweight profiling and quick
    identification of performance bottlenecks.

    Examples
    --------
    >>> @timefun
    ... def square(x):
    ...     return x * x
    ...
    >>> square(4)  # doctest: +ELLIPSIS
    @timefun:square took ... seconds
    16
    """
    @wraps(fun)
    def measure_time(*args: Any, **kwargs: Any) -> Any:
        t1 = timer()
        result = fun(*args, **kwargs)
        t2 = timer()
        print(f"@timefun:{fun.__name__} took {t2 - t1:.6f} seconds")
        return result

    return measure_time


class TimeWith:
    """
    Context manager for timing code blocks.

    Parameters
    ----------
    name : str, optional
        Descriptive name included in timing output.
    logger : logging.Logger or None, optional
        Logger used for output. If None, timing information is written
        to standard output.

    Examples
    --------
    >>> with TimeWith("task") as timer:  # doctest: +ELLIPSIS
    ...     _ = sum(range(1000))
    ...
    task finished took ... seconds

    Report intermediate checkpoints:

    >>> with TimeWith("task") as timer:  # doctest: +ELLIPSIS
    ...     _ = sum(range(100))
    ...     timer.checkpoint("halfway")
    ...
    task halfway took ... seconds
    task finished took ... seconds
    """
    def __init__(self, name: str = "", logger: logging.Logger | None = None) -> None:
        self.name = name
        self.logger = logger
        self.start = timer()

    @property
    def elapsed(self) -> float:
        return timer() - self.start

    def checkpoint(self, name: str = "") -> None:
        """
        Report elapsed time since entering the context.

        Parameters
        ----------
        name : str, optional
            Label included in the timing output.
        """
        msg = f"{self.name} {name} took {self.elapsed:.6f} seconds".strip()
        if self.logger is not None:
            self.logger.info(msg)
        else:
            print(msg)

    def __enter__(self) -> TimeWith:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type:
            self.checkpoint(f"raised {exc_type.__name__}")
        else:
            self.checkpoint("finished")


def do_cprofile(
    func: Callable[..., Any] | None = None,
    *,
    sort: str = "cumulative",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Profile a function using ``cProfile``.

    Parameters
    ----------
    sort : str, optional
        Sort key passed to ``pstats.Stats.sort_stats``.
        Common values are:

        - ``"cumulative"``: cumulative time including subcalls.
        - ``"tottime"``: time spent in the function itself.
        - ``"calls"``: number of calls.
        - ``"ncalls"``: number of primitive calls.

    Returns
    -------
    callable
        Decorator that prints profiling statistics.

    Examples
    --------
    >>> import time
    >>>
    >>> @do_cprofile(sort="tottime")
    ... def work():
    ...     time.sleep(0.01)
    ...
    >>> work()  # doctest: +SKIP
    """

    print("decorator called", func, sort)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def profiled_func(*args: Any, **kwargs: Any) -> Any:
            print("profiled_func called")
            print("current profiler =", sys.getprofile())
            current = sys.getprofile()
            if current is not None:
                warnings.warn(
                    f"Another profiler is already active: {current!r}. "
                    "Skipping cProfile profiling.",
                    stacklevel=2,
                )
                return func(*args, **kwargs)
            profile = cProfile.Profile()
            profile.enable()
            try:
                return func(*args, **kwargs)
            finally:
                profile.disable()
                stats = pstats.Stats(profile)
                stats.sort_stats(sort)
                stats.print_stats()

        return profiled_func

    # @do_cprofile
    if func is not None:
        return decorator(func)

    # @do_cprofile(...)
    return decorator


if __name__ == "__main__":

    from profiletools.testing import test_docstrings
    # test_docstrings()
    @do_cprofile()
    def work():
        pass

    work()

    @do_cprofile
    def work1():
        pass

    work1()
