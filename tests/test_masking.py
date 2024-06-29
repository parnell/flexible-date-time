import pytest

from flexible_datetime import FlexDateTime


@pytest.fixture
def fdt():
    return FlexDateTime()


def test_initial_mask(fdt: FlexDateTime):
    assert fdt.mask == {
        "year": False,
        "month": False,
        "day": False,
        "hour": False,
        "minute": False,
        "second": False,
        "millisecond": False,
    }


def test_apply_mask(fdt: FlexDateTime):
    fdt.apply_mask(year=True, month=True)
    assert fdt.mask["year"] == True
    assert fdt.mask["month"] == True


def test_clear_mask(fdt: FlexDateTime):
    fdt.apply_mask(year=True, month=True)
    fdt.clear_mask()
    assert fdt.mask == {
        "year": False,
        "month": False,
        "day": False,
        "hour": False,
        "minute": False,
        "second": False,
        "millisecond": False,
    }


def test_toggle_mask(fdt: FlexDateTime):
    fdt.apply_mask(year=True)
    fdt.toggle_mask(year=False, day=True)
    assert fdt.mask["year"] == False
    assert fdt.mask["day"] == True


def test_use_only(fdt: FlexDateTime):
    fdt.apply_mask(year=True)
    fdt.use_only(month=True, day=True)
    assert fdt.mask == {
        "year": False,
        "month": True,
        "day": True,
        "hour": False,
        "minute": False,
        "second": False,
        "millisecond": False,
    }


# Run the tests
if __name__ == "__main__":
    pytest.main(["-v", __file__])
