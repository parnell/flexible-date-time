import arrow
import pytest

from flexible_datetime import FlexDateTime


@pytest.fixture
def example_date():
    return arrow.get(2023, 6, 29, 12, 34, 56, 789000)


@pytest.fixture
def example_dict():
    return {
        "year": 2023,
        "month": 6,
        "day": 29,
        "hour": 12,
        "minute": 34,
        "second": 56,
        "millisecond": 789,
    }


def test_from_dict():
    date_dict = {
        "year": 2023,
        "month": 6,
        "day": 29,
        "hour": 12,
        "minute": 34,
        "second": 56,
        "millisecond": 789,
    }
    flex_date = FlexDateTime.from_dict(date_dict)
    assert flex_date.dt.year == 2023
    assert flex_date.dt.month == 6
    assert flex_date.dt.day == 29
    assert flex_date.dt.hour == 12
    assert flex_date.dt.minute == 34
    assert flex_date.dt.second == 56
    assert flex_date.dt.microsecond == 789000
    assert not any(flex_date.mask.values())


def test_from_str():
    date_str = "2023-06-29 12:34:56.789"
    flex_date = FlexDateTime.from_str(date_str, "YYYY-MM-DD HH:mm:ss.SSS")
    assert flex_date.dt.year == 2023
    assert flex_date.dt.month == 6
    assert flex_date.dt.day == 29
    assert flex_date.dt.hour == 12
    assert flex_date.dt.minute == 34
    assert flex_date.dt.second == 56
    assert flex_date.dt.microsecond == 789000
    assert flex_date.to_minimal_datetime("YYYY-MM-DD HH:mm:ss.SSS") == date_str
    assert not any(flex_date.mask.values())


def test_to_str_S():
    dt = arrow.get(2023, 6, 29, 12, 34, 56, 789000)
    flex_date = FlexDateTime(dt=dt)
    assert flex_date.to_minimal_datetime("YYYY-MM-DD HH:mm:ss.S") == "2023-06-29 12:34:56.7"


def test_to_str_SS():
    dt = arrow.get(2023, 6, 29, 12, 34, 56, 789000)
    flex_date = FlexDateTime(dt=dt)
    assert flex_date.to_minimal_datetime("YYYY-MM-DD HH:mm:ss.SS") == "2023-06-29 12:34:56.78"


def test_to_str_SSS():
    dt = arrow.get(2023, 6, 29, 12, 34, 56, 789000)
    flex_date = FlexDateTime(dt=dt)
    assert flex_date.to_minimal_datetime("YYYY-MM-DD HH:mm:ss.SSS") == "2023-06-29 12:34:56.789"


def test_to_str_SSSS():
    dt = arrow.get(2023, 6, 29, 12, 34, 56, 789123)
    flex_date = FlexDateTime(dt=dt)
    assert flex_date.to_minimal_datetime("YYYY-MM-DD HH:mm:ss.SSSS") == "2023-06-29 12:34:56.7891"


def test_to_str_SSSSS():
    dt = arrow.get(2023, 6, 29, 12, 34, 56, 789123)
    flex_date = FlexDateTime(dt=dt)
    assert flex_date.to_minimal_datetime("YYYY-MM-DD HH:mm:ss.SSSSS") == "2023-06-29 12:34:56.78912"


def test_to_str_SSSSSS():
    dt = arrow.get(2023, 6, 29, 12, 34, 56, 789123)
    flex_date = FlexDateTime(dt=dt)
    assert flex_date.to_minimal_datetime("YYYY-MM-DD HH:mm:ss.SSSSSS") == "2023-06-29 12:34:56.789123"


def test_edge_case_zero_milliseconds():
    date_str = "2023-06-29 12:34:56.000"
    flex_date = FlexDateTime.from_str(date_str, "YYYY-MM-DD HH:mm:ss.SSS")
    assert flex_date.dt.microsecond == 0
    assert not any(flex_date.mask.values())


def test_edge_case_max_milliseconds():
    date_str = "2023-06-29 12:34:56.999"
    flex_date = FlexDateTime.from_str(date_str, "YYYY-MM-DD HH:mm:ss.SSS")
    assert flex_date.dt.microsecond == 999000
    assert not any(flex_date.mask.values())


if __name__ == "__main__":
    pytest.main([__file__])
