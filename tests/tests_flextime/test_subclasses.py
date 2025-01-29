import pytest

from flexible_datetime import (
    short_time,
    component_time,
    iso_time,
    mask_time,
)


@pytest.fixture
def sample_datetime():
    return "2023-06-15T14:30:45"


@pytest.fixture
def partial_datetime():
    return "2023-06"


def test_component_time_output(sample_datetime):
    ct = component_time(sample_datetime)
    expected = {"year": 2023, "month": 6, "day": 15, "hour": 14, "minute": 30, "second": 45}
    assert ct.to_components() == expected


def test_minimal_time_output(sample_datetime):
    mt = short_time(sample_datetime)
    assert str(mt) == "2023-06-15T14:30:45"


def test_iso_time_output(sample_datetime):
    it = iso_time(sample_datetime)
    assert str(it) == "2023-06-15T14:30:45+00:00"


def test_masked_time_output(sample_datetime):
    mt = short_time(sample_datetime)
    expected = {"dt": "2023-06-15T14:30:45+00:00", "mask": "0000001"}
    assert mt.to_flex() == expected


def test_partial_dates():
    """Test how each format handles partial dates"""
    dt = "2023-06"

    # Component time should only include provided components
    ct = component_time(dt)
    assert ct.to_components() == {"year": 2023, "month": 6}

    # Minimal time should show only provided components
    mt = short_time(dt)
    assert str(mt) == "2023-06"

    # ISO time shows full datetime
    it = iso_time(dt)
    assert str(it) == "2023-06-01T00:00:00+00:00"

    # Masked time shows full datetime with mask
    mt = mask_time(dt)
    expected = {"dt": "2023-06-01T00:00:00+00:00", "mask": "0011111"}
    assert mt.to_flex() == expected


def test_inheritance_features():
    """Test that the new classes inherit all flextime features"""
    ct = component_time("2023-06-15")

    # Test masking
    ct.apply_mask(day=True)
    assert ct.to_components() == {"year": 2023, "month": 6}

    # Test component access
    assert ct.year == 2023
    assert ct.month == 6

    # Test comparison with masked components
    ct1 = component_time("2023-06-15")
    ct2 = component_time("2023-06-20")
    ct1.apply_mask(day=True)
    ct2.apply_mask(day=True)
    assert ct1 == ct2


def test_format_override():
    """Test that we can still override the default format"""
    ct = component_time("2023-06-15")

    # Default is components
    assert isinstance(ct.to_components(), dict)

    # Override to minimal
    assert ct.to_str("short") == "2023-06-15"

    # Override to ISO
    assert ct.to_str("datetime") == "2023-06-15T00:00:00+00:00"

    # Override to flex
    flex_output = ct.to_flex()
    assert isinstance(flex_output, dict)
    assert "dt" in flex_output
    assert "mask" in flex_output


if __name__ == "__main__":
    pytest.main(["-v", __file__])
