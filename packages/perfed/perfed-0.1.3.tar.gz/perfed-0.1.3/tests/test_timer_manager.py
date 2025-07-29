from unittest.mock import Mock, call, mock_open, patch

import pandas as pd
import pytest

from perfed.timer import Timer
from perfed.timer_manager import TimerManager


@pytest.fixture
def tm():
    return TimerManager("test_timer_manager")


@pytest.fixture
def tm_with_timers(tm):
    timer_a = Timer("a")
    timer_a._start = 0
    timer_a._stop = 1000000

    timer_b = Timer("b")
    timer_b._start = 0
    timer_b._stop = 2000000

    timer_c = Timer("c")
    timer_c._start = 0
    timer_c._stop = 3000000

    tm._timers = {
        "a": timer_a,
        "b": timer_b,
        "c": timer_c,
    }
    return tm


class TestTimerManager:
    def test_init(self, tm):
        assert tm._name == "test_timer_manager"
        assert tm._timers == {}

    def test_len(self, tm_with_timers):
        assert len(tm_with_timers) == 3
        tm_with_timers._timers = {}
        assert len(tm_with_timers) == 0

    def test_start(self, tm):
        timer = tm.start("a")
        assert isinstance(timer, Timer)
        assert timer is tm._timers.get("a")
        assert timer._name == "a"
        assert timer._start > 0

    def test_stop(self, tm):
        timer = tm.start("a")
        tm.stop("a")
        assert timer._stop > 0

    def test_stop_no_timer(self, tm):
        with pytest.raises(ValueError):
            tm.stop("a")

    def test_get_timer(self, tm_with_timers):
        assert tm_with_timers.get_timer("a") is tm_with_timers._timers.get("a")
        with pytest.raises(ValueError):
            tm_with_timers.get_timer("z")

    def test_get_timers(self, tm_with_timers):
        assert tm_with_timers.get_timers() is tm_with_timers._timers

    def test_to_tuples(self, tm_with_timers):
        expected = [
            ("a", 0.001),
            ("b", 0.002),
            ("c", 0.003),
        ]
        assert tm_with_timers.to_tuples() == expected

    def test_to_dict(self, tm_with_timers):
        expected = {
            "a": 0.001,
            "b": 0.002,
            "c": 0.003,
        }
        assert tm_with_timers.to_dict() == expected

    def test_to_dataframe(self, tm_with_timers):
        expected = pd.DataFrame({
            "Timer": ["a", "b", "c"],
            "Duration": [0.001, 0.002, 0.003],
        })
        assert tm_with_timers.to_dataframe().equals(expected)

    def test_save_csv(self, tm_with_timers):
        m = mock_open()
        with patch("perfed.timer_manager.open", m):
            tm_with_timers.save("test.csv", "csv", "a")

        m.assert_called_once_with("test.csv", mode="a")
        m().write.assert_has_calls([
            call("a,0.001\n"),
            call("b,0.002\n"),
            call("c,0.003\n"),
        ])

    def test_save_json(self, tm_with_timers):
        m = mock_open()
        with patch("perfed.timer_manager.open", m):
            tm_with_timers.save("test.json", "json", "w")

        m.assert_called_once_with("test.json", mode="w")
        m().write.assert_called_once_with('{"a": 0.001, "b": 0.002, "c": 0.003}')

    def test_save_invalid_args(self, tm_with_timers):
        m = mock_open()
        with patch("perfed.timer_manager.open", m):
            with pytest.raises(ValueError):
                tm_with_timers.save("test.csv", "-", "w")
            with pytest.raises(ValueError):
                tm_with_timers.save("test.json", "json", "-")

    def test_show(self, tm_with_timers):
        mocked_print_fn = Mock()
        with patch("perfed.timer_manager.tabulate") as mocked_tabulate:
            tm_with_timers.show(print_fn=mocked_print_fn)

        mocked_print_fn.assert_called_once()
        mocked_tabulate.assert_called_once()

    def test_show_stats(self, tm_with_timers):
        mocked_print_fn = Mock()
        with patch("perfed.timer_manager.tabulate") as mocked_tabulate:
            tm_with_timers.show_stats(print_fn=mocked_print_fn)

        mocked_print_fn.assert_called_once()
        mocked_tabulate.assert_called_once()
