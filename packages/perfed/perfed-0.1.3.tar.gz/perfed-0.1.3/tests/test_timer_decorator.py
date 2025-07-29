import time

import pytest

from perfed.timer_decorator import TimerDecorator
from perfed.timer_manager import TimerManager


@pytest.fixture(autouse=True)
def clear_timer_decorator():
    TimerDecorator._decorated_managers = {}


class TestTimerDecorator:
    def test_decorate(self):
        @TimerDecorator.decorate("test_tm")
        def dummy_func(x: int) -> int:
            time.sleep(0.1)
            return x + 1

        assert dummy_func(1) == 2
        assert dummy_func(2) == 3
        assert dummy_func(3) == 4

        tm = TimerDecorator._decorated_managers.get("test_tm")
        assert isinstance(tm, TimerManager)
        assert len(tm) == 3
        for timer in tm._timers.values():
            assert timer.get() > 0.1

    def test_decorate_already_exists(self):
        @TimerDecorator.decorate("test_tm")
        def dummy_func_a(x: int) -> int:
            time.sleep(0.1)
            return x + 1

        with pytest.raises(ValueError):
            @TimerDecorator.decorate("test_tm")
            def dummy_func_b(x: int) -> int:
                time.sleep(0.1)
                return x + 1

    def test_get_manager(self):
        @TimerDecorator.decorate("test_tm_a")
        def dummy_func_a(x: int) -> int:
            time.sleep(0.1)
            return x + 1

        assert TimerDecorator.get_manager("test_tm_a") == TimerDecorator._decorated_managers["test_tm_a"]

    def test_get_manager_does_not_exist(self):
        with pytest.raises(ValueError):
            TimerDecorator.get_manager("test_tm_a")

    def test_get_managers(self):
        @TimerDecorator.decorate("test_tm_a")
        def dummy_func_a(x: int) -> int:
            time.sleep(0.1)
            return x + 1

        @TimerDecorator.decorate("test_tm_b")
        def dummy_func_b(x: int) -> int:
            time.sleep(0.1)
            return x + 1

        assert TimerDecorator.get_managers() == TimerDecorator._decorated_managers
