from datetime import time

import pytest

from flexible_datetime import flex_time


def test_eq():
    ft1 = flex_time("14:30:00")
    ft2 = flex_time("14:30:00")
    assert ft1 == ft2


def test_ne():
    ft1 = flex_time("14:30:00")
    ft2 = flex_time("15:30:00")
    assert ft1 != ft2


def test_eq_with_mask():
    ft1 = flex_time({"hour": 14, "minute": 30})  # second masked
    ft2 = flex_time({"hour": 14, "minute": 30})  # second masked
    assert ft1 == ft2


def test_ne_with_mask():
    ft1 = flex_time({"hour": 14, "minute": 30})  # second masked
    ft2 = flex_time({"hour": 14, "minute": 30, "second": 45})
    ft2.mask["second"] = True  # mask the second
    assert ft1 == ft2  # should be equal since seconds are masked


def test_lt():
    ft1 = flex_time("14:30:00")
    ft2 = flex_time("14:31:00")
    assert ft1 < ft2


def test_le():
    ft1 = flex_time("14:30:00")
    ft2 = flex_time("14:30:00")
    ft3 = flex_time("14:31:00")
    assert ft1 <= ft2
    assert ft1 <= ft3


def test_gt():
    ft1 = flex_time("14:31:00")
    ft2 = flex_time("14:30:00")
    assert ft1 > ft2


def test_ge():
    ft1 = flex_time("14:30:00")
    ft2 = flex_time("14:30:00")
    ft3 = flex_time("14:29:00")
    assert ft1 >= ft2
    assert ft1 >= ft3


def test_lt_with_mask():
    ft1 = flex_time({"hour": 14, "minute": 30})
    ft2 = flex_time({"hour": 14, "minute": 31})
    assert ft1 < ft2  # masked seconds should be ignored


def test_le_with_mask():
    ft1 = flex_time({"hour": 14, "minute": 30})
    ft2 = flex_time({"hour": 14, "minute": 30})
    ft3 = flex_time({"hour": 14, "minute": 31})
    assert ft1 <= ft2
    assert ft1 <= ft3


def test_gt_with_mask():
    ft1 = flex_time({"hour": 14, "minute": 31})
    ft2 = flex_time({"hour": 14, "minute": 30})
    assert ft1 > ft2


def test_ge_with_mask():
    ft1 = flex_time({"hour": 14, "minute": 30})
    ft2 = flex_time({"hour": 14, "minute": 30})
    ft3 = flex_time({"hour": 14, "minute": 29})
    assert ft1 >= ft2
    assert ft1 >= ft3


def test_hour_only():
    ft1 = flex_time("14")
    ft2 = flex_time("14")
    assert ft1 == ft2
    assert ft1.mask["second"] is True


def test_hour_minute():
    ft1 = flex_time("14:30")
    ft2 = flex_time("14:30")
    assert ft1 == ft2
    assert ft1.mask["second"] is True


def test_time_formats():
    # Test various time format inputs
    formats = [
        "14",  # hour only
        "14:30",  # hour:minute
        "14:30:00",  # hour:minute:second
        "2:30 PM",  # 12-hour with space
        "2:30PM",  # 12-hour without space
        "14.30",  # dot separator
        "1430",  # no separator
    ]

    for fmt in formats:
        ft = flex_time(fmt)
        assert isinstance(ft.time, time)


def test_dict_format():
    # Test dictionary input format
    ft1 = flex_time({"hour": 14, "minute": 30})
    ft2 = flex_time({"hour": 14, "minute": 30, "second": 0})
    assert ft1 == ft2
    assert ft1.mask["second"] is True
    assert ft2.mask["second"] is False


def test_subset_mask_le():
    """Tests less than or equal with subset masking"""
    # Same times, different precision
    ft1 = flex_time({"hour": 14, "minute": 30})  # second masked
    ft2 = flex_time({"hour": 14, "minute": 30, "second": 0})  # nothing masked
    assert ft1 <= ft2
    assert ft2 <= ft1

    # Different times, should still work
    ft3 = flex_time({"hour": 14, "minute": 30})  # second masked
    ft4 = flex_time({"hour": 14, "minute": 31, "second": 0})  # nothing masked
    assert ft3 <= ft4
    assert not ft4 <= ft3

    # Edge case - times differ only in masked component
    ft5 = flex_time({"hour": 14, "minute": 30})  # second masked
    ft6 = flex_time({"hour": 14, "minute": 30, "second": 45})  # nothing masked
    assert ft5 <= ft6


def test_subset_mask_ge():
    """Tests greater than or equal with subset masking"""
    # Same times, different precision
    ft1 = flex_time({"hour": 14, "minute": 30})  # second masked
    ft2 = flex_time({"hour": 14, "minute": 30, "second": 0})  # nothing masked
    assert ft1 >= ft2
    assert ft2 >= ft1

    # Different times, should still work
    ft3 = flex_time({"hour": 14, "minute": 31})  # second masked
    ft4 = flex_time({"hour": 14, "minute": 30, "second": 0})  # nothing masked
    assert ft3 >= ft4
    assert not ft4 >= ft3

    # Edge case - times differ only in masked component
    ft5 = flex_time({"hour": 14, "minute": 30})  # second masked
    ft6 = flex_time({"hour": 14, "minute": 30, "second": 45})  # nothing masked
    assert ft6 >= ft5


def test_subset_mask_hour_only():
    """Tests comparisons when only hours are specified"""
    ft1 = flex_time({"hour": 14})  # minute and second masked
    ft2 = flex_time({"hour": 14, "minute": 0, "second": 0})  # nothing masked
    assert ft1 <= ft2
    assert ft2 <= ft1
    assert ft1 >= ft2
    assert ft2 >= ft1
    assert ft1 == ft2

    ft3 = flex_time({"hour": 15})  # minute and second masked
    ft4 = flex_time({"hour": 14, "minute": 59, "second": 59})  # nothing masked
    assert ft3 >= ft4
    assert not ft4 >= ft3
    assert ft4 <= ft3
    assert not ft3 <= ft4


def test_subset_mask_chains():
    """Tests chains of different mask levels"""
    ft1 = flex_time({"hour": 14})  # minute and second masked
    ft2 = flex_time({"hour": 14, "minute": 30})  # second masked
    ft3 = flex_time({"hour": 14, "minute": 30, "second": 45})  # nothing masked

    # They should all be comparable
    assert ft1 <= ft2
    assert ft2 <= ft3
    assert ft1 <= ft3

    # And in reverse
    assert ft3 >= ft2
    assert ft2 >= ft1
    assert ft3 >= ft1


if __name__ == "__main__":
    pytest.main([__file__])
