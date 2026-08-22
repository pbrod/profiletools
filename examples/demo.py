"""
Windows‑safe demo script for profiletools.
Each example runs in isolation and explicitly disables the profiler
to avoid line_profiler shutdown errors on Windows.
"""

import sys
import time

from profiletools import TimeWith, do_cprofile, do_profile, timefun


# ------------------------------------------------------------
# 1. Timing a function with @timefun
# ------------------------------------------------------------
@timefun
def demo_timefun():
    for x in range(50000):
        i = x**3
    return i


def run_timefun():
    print("\n=== Example: @timefun ===")
    demo_timefun()


# ------------------------------------------------------------
# 2. Timing a block with TimeWith
# ------------------------------------------------------------
def run_timewith():
    print("\n=== Example: TimeWith context manager ===")
    with TimeWith("expensive block") as timer:
        for x in range(50000):
            i = x**3
        timer.checkpoint("halfway done")

        for x in range(50000):
            i = x**4
        timer.checkpoint("finished second part")
    return i


# ------------------------------------------------------------
# 3. Profiling a function with @do_cprofile
# ------------------------------------------------------------
def calculate(x):
    time.sleep(0.1)
    return x**3


@do_cprofile()
def demo_cprofile():
    for x in range(10):
        i = calculate(x)
    return i


def run_cprofile():
    print("\n=== Example: @do_cprofile ===")
    demo_cprofile()


# ------------------------------------------------------------
# 4. Line-by-line profiling with @do_profile (follow function)
# ------------------------------------------------------------
def helper():
    yield from range(5000)


@do_profile(follow=[helper])
def demo_do_profile_follow():
    for x in helper():
        i = x**3
    return i


def run_do_profile_follow():
    print("\n=== Example: @do_profile(follow=[helper]) ===")
    demo_do_profile_follow()
    sys.setprofile(None)  # Windows-safe teardown


# ------------------------------------------------------------
# 5. Profiling class method with follow=["method_name"]
# ------------------------------------------------------------
class WorkerFollowName:
    @do_profile(follow=["_numbers"])
    def compute(self):
        for x in self._numbers():
            i = x**4
        return i

    def _numbers(self):
        yield from range(5000)


def run_do_profile_follow_name():
    print("\n=== Example: @do_profile(follow=['_numbers']) on class method ===")
    WorkerFollowName().compute()
    sys.setprofile(None)  # Windows-safe teardown


# ------------------------------------------------------------
# 6. Profiling all class methods with follow_all_methods=True
# ------------------------------------------------------------
class WorkerAllMethods:
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


def run_do_profile_all_methods():
    print("\n=== Example: @do_profile(follow_all_methods=True) ===")
    WorkerAllMethods().compute()
    sys.setprofile(None)  # Windows-safe teardown


# ------------------------------------------------------------
# 7. Using do_profile without a decorator
# ------------------------------------------------------------
class WorkerManual:
    def compute(self):
        for x in self._numbers():
            i = x**3
        return i

    def _numbers(self):
        yield from range(5000)


def run_do_profile_manual():
    print("\n=== Example: do_profile(...) without decorator ===")
    worker = WorkerManual()
    do_profile(follow=[worker._numbers])(worker.compute)()
    sys.setprofile(None)  # Windows-safe teardown


# ------------------------------------------------------------
# Main runner
# ------------------------------------------------------------
if __name__ == "__main__":
    print("Starting demo.....")
    run_timefun()
    run_timewith()
    run_cprofile()
    run_do_profile_follow()
    run_do_profile_follow_name()
    run_do_profile_all_methods()
    run_do_profile_manual()

    print("\nAll examples completed.")
    sys.setprofile(None)  # Final safety
