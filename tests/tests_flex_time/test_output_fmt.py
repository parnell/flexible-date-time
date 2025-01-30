import pytest

from flexible_datetime import FTOutputFormat, flex_time


@pytest.fixture
def ft():
    return flex_time("12:34:56")


def test_minimal_time_hm(ft: flex_time):
    # Set mask to show only hours and minutes
    ft.mask["second"] = True
    ft.output_format = FTOutputFormat("short")

    assert str(ft) == "12:34"


def test_minimal_time_h(ft: flex_time):
    # Set mask to show only hours
    ft.mask["minute"] = True
    ft.mask["second"] = True
    ft._output_format = FTOutputFormat.short

    assert str(ft) == "12"


def test_full_time(ft: flex_time):
    # Test full time output format
    ft._output_format = FTOutputFormat.time

    assert str(ft) == "12:34:56"


def test_flex_format(ft: flex_time):
    # Test mask output format
    ft.mask["second"] = True  # Mask the seconds
    ft._output_format = FTOutputFormat.mask
    expected = {"time": "12:34:56", "mask": "0011"}

    assert ft.to_flex() == expected
    assert str(ft) == str(expected)


def test_components_hms(ft: flex_time):
    # Test components output format
    ft._output_format = FTOutputFormat.components
    expected = {"hour": 12, "minute": 34, "second": 56}

    assert ft.to_components() == expected
    assert str(ft) == str(expected)


def test_components_hm(ft: flex_time):
    # Test components with masked second
    ft.mask["second"] = True
    ft._output_format = FTOutputFormat.components
    expected = {"hour": 12, "minute": 34}

    assert ft.to_components() == expected


def test_time_parsing():
    # Test various time input formats
    assert str(flex_time("12:34")) == "12:34"
    assert str(flex_time("12")) == "12:00"
    assert str(flex_time("1:30 PM")) == "13:30"
    assert str(flex_time("9am")) == "09:00"


def test_time_comparison():
    # Test comparison operators with compatible masks
    t1 = flex_time("12:30")  # implicitly masks seconds
    t2 = flex_time("12:45")  # implicitly masks seconds

    assert t1 < t2
    assert t1 <= t2
    assert t2 > t1
    assert t2 >= t1
    assert t1 != t2

    t3 = flex_time("12:30")
    assert t1 == t3


if __name__ == "__main__":
    pytest.main([__file__])
