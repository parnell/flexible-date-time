from datetime import timedelta

import pytest

from flexible_datetime import flex_time


def test_basic_subtraction():
    """Test basic subtraction between two flex_time objects"""
    t1 = flex_time("14:30")
    t2 = flex_time("12:15")
    diff = t1 - t2
    assert diff == timedelta(hours=2, minutes=15)


def test_subtraction_with_seconds():
    """Test subtraction when seconds are included"""
    t1 = flex_time("14:30:45")
    t2 = flex_time("12:15:20")
    diff = t1 - t2
    assert diff == timedelta(hours=2, minutes=15, seconds=25)


def test_subtraction_across_midnight():
    """Test subtraction when times span across midnight"""
    t1 = flex_time("01:00")
    t2 = flex_time("23:00")
    diff = t1 - t2
    assert diff == timedelta(days=-1, hours=2)  # -22 hours, represented as -1 day + 2 hours


def test_subtraction_with_masks():
    """Test subtraction with different mask combinations"""
    # Both times have seconds masked
    t1 = flex_time({"hour": 14, "minute": 15})
    t2 = flex_time({"hour": 12, "minute": 0})
    diff = t1 - t2
    assert diff == timedelta(hours=2, minutes=15)

    # One time has seconds, but they're masked in comparison
    t3 = flex_time({"time": "14:30:00", "mask": "001"})  # Only mask microseconds
    t4 = flex_time({"time": "12:15:00", "mask": "001"})  # Only mask microseconds
    diff = t3 - t4
    assert diff == timedelta(hours=2, minutes=15)


def test_subtraction_incompatible_masks():
    """Test that subtraction fails with incompatible masks"""
    t1 = flex_time({"hour": 14})  # Only hour specified
    t2 = flex_time({"minute": 30})  # Only minute specified
    with pytest.raises(ValueError, match="incompatible masks"):
        _ = t1 - t2


def test_basic_addition():
    """Test adding timedelta to flex_time"""
    t1 = flex_time("14:30")
    delta = timedelta(hours=2, minutes=15)
    result = t1 + delta
    assert result == flex_time("16:45")


def test_addition_with_seconds():
    """Test addition with seconds precision"""
    t1 = flex_time("14:30:45")
    delta = timedelta(hours=2, minutes=15, seconds=20)
    result = t1 + delta
    assert result == flex_time("16:46:05")


def test_addition_across_midnight():
    """Test addition that wraps around midnight"""
    t1 = flex_time("23:30")
    delta = timedelta(hours=1)
    result = t1 + delta
    assert result == flex_time("00:30")


def test_addition_preserves_mask():
    """Test that addition preserves the original mask"""
    t1 = flex_time({"hour": 14, "minute": 30})  # seconds masked
    delta = timedelta(hours=2, minutes=15, seconds=30)
    result = t1 + delta
    assert result.mask["second"]
    assert result == flex_time({"hour": 16, "minute": 45})


def test_reverse_addition():
    """Test that reverse addition (timedelta + flex_time) works"""
    t1 = flex_time("14:30")
    delta = timedelta(hours=2, minutes=15)
    result = delta + t1
    assert result == flex_time("16:45")


def test_reverse_subtraction():
    """Test that reverse subtraction (other - flex_time) is not supported"""
    t1 = flex_time("14:30")
    delta = timedelta(hours=2)
    with pytest.raises(TypeError):
        _ = delta - t1


def test_addition_large_values():
    """Test addition with large time values"""
    t1 = flex_time("14:30")
    delta = timedelta(days=2, hours=12)
    result = t1 + delta
    assert result == flex_time("02:30")  # Should wrap around multiple days


def test_subtraction_microseconds():
    """Test subtraction with microsecond precision"""
    # Create times with explicit microseconds and unmask them
    t1 = flex_time({"time": "14:30:45.500000", "mask": "0000"})  # Unmask all components
    t2 = flex_time({"time": "14:30:45.200000", "mask": "0000"})  # Unmask all components
    diff = t1 - t2
    assert diff == timedelta(microseconds=300000)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
