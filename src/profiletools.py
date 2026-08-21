from __future__ import annotations

import cProfile
import inspect
import logging
import warnings
from collections.abc import Callable
from functools import wraps
from timeit import default_timer as timer
from types import TracebackType
from typing import Any, TypeVar, Optional

F = TypeVar("F", bound=Callable[..., Any])

try:
    from line_profiler import LineProfiler
except ImportError:
    LineProfiler = None
    warnings.warn(
        "line_profiler not installed; do_profile will be a no-op.",
        stacklevel=2,
    )


def _add_all_class_methods(
    profiler: LineProfiler,
    instance: Any,
    except_: str = "",
) -> None:
    cls = type(instance)
    for name, member in inspect.getmembers(cls):
        if name == except_:
            continue
        if inspect.isfunction(member) or inspect.ismethod(member):
            profiler.add_function(member)


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
    follow: tuple[Any, ...] = (),
    follow_all_methods: bool = False,
) -> Callable[[F], F]:
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
                _add_all_class_methods(profiler, args[0], except_=func.__name__)

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
    @wraps(fun)
    def measure_time(*args: Any, **kwargs: Any) -> Any:
        t1 = timer()
        result = fun(*args, **kwargs)
        t2 = timer()
        print(f"@timefun:{fun.__name__} took {t2 - t1:.6f} seconds")
        return result

    return measure_time


class TimeWith:
    def __init__(self, name: str = "", logger: Optional[logging.Logger] = None) -> None:
        self.name = name
        self.logger = logger
        self.start = timer()

    @property
    def elapsed(self) -> float:
        return timer() - self.start

    def checkpoint(self, name: str = "") -> None:
        msg = f"{self.name} {name} took {self.elapsed:.6f} seconds".strip()
        if self.logger:
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
        self.checkpoint("finished")


def do_cprofile(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def profiled_func(*args: Any, **kwargs: Any) -> Any:
        profile = cProfile.Profile()
        profile.enable()
        try:
            return func(*args, **kwargs)
        finally:
            profile.disable()
            profile.print_stats(sort="cumulative")

    return profiled_func
