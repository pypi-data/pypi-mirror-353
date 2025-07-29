import pytest

from perfed.util import convert_from_ns


def test_convert_from_ns():
    time_ns = 100000
    assert convert_from_ns(time_ns=time_ns, unit="ns") == time_ns
    assert convert_from_ns(time_ns=time_ns, unit="ms") == time_ns / 1e3
    assert convert_from_ns(time_ns=time_ns, unit="sec") == time_ns / 1e9
    assert convert_from_ns(time_ns=time_ns, unit="min") == time_ns / 1e9 / 60
    with pytest.raises(ValueError):
        convert_from_ns(time_ns=time_ns, unit="aa")  # type: ignore
