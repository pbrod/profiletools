from profiletools import do_profile, do_cprofile, timefun, TimeWith


def test_timefun_runs():
    @timefun
    def f(x):
        return x * 2

    assert f(3) == 6


def test_TimeWith_context():
    with TimeWith("test") as tw:
        assert tw.elapsed >= 0.0


def test_do_cprofile_runs():
    @do_cprofile
    def f(x):
        return x + 1

    assert f(1) == 2


def test_do_profile_noop_without_line_profiler():
    @do_profile()
    def f(x):
        return x - 1

    assert f(2) == 1
