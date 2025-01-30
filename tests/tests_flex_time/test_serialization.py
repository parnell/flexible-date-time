import json
from datetime import datetime, time

import pytest
from pydantic import BaseModel

from flexible_datetime.flex_time import flex_time


def test_dump_load():
    ft = flex_time("14:30:00")
    d = json.dumps(ft.to_flex())
    ft2 = flex_time(json.loads(d))
    assert ft == ft2
    # Should have seconds unmasked since explicitly provided
    assert ft2.mask_to_binary(ft2.mask) == "0001"


def test_dump_load_hm():
    ft = flex_time("14:30")  # Only hour and minute
    d = json.dumps(ft.to_flex())
    ft2 = flex_time(json.loads(d))
    assert ft == ft2
    # Should mask seconds and microseconds
    assert ft2.mask["second"] is True
    assert ft2.mask_to_binary(ft2.mask) == "0011"


def test_from_dict():
    d = {"hour": 14, "minute": 30}
    ft = flex_time(d)
    assert ft.time == time(14, 30)
    # Should mask seconds and microseconds since not provided
    assert ft.mask_to_binary(ft.mask) == "0011"
    assert ft.hour == 14
    assert ft.minute == 30
    assert ft.second == 0  # default value


def test_from_time():
    t = time(14, 30, 45)
    ft = flex_time(t)
    assert ft.time == t
    # Should only mask microseconds for time objects
    assert ft.mask_to_binary(ft.mask) == "0001"


def test_from_datetime():
    dt = datetime.now()
    ft = flex_time(dt)
    assert ft.time == dt.time()
    # Should only mask microseconds for datetime objects
    assert ft.mask_to_binary(ft.mask) == "0001"


def test_from_string_formats():
    # Test various string formats
    test_cases = [
        (
            "14:00",
            time(14, 0, 0),
            "0011",
        ),  # HH:mm format - show hours and minutes, mask seconds and microseconds
        ("14:30", time(14, 30, 0), "0011"),  # HH:mm format
        ("14:30:45", time(14, 30, 45), "0001"),  # HH:mm:ss format - only mask microseconds
        ("2pm", time(14, 0, 0), "0011"),  # 12-hour format - show hours and minutes
        ("2:30pm", time(14, 30, 0), "0011"),  # 12-hour with minutes
    ]

    for time_str, expected_time, expected_mask in test_cases:
        ft = flex_time(time_str)
        assert ft.time == expected_time, f"Failed for time {ft.time} with input: {time_str}"
        assert (
            ft.mask_to_binary(ft.mask) == expected_mask
        ), f"Wrong mask for input: {time_str}. Got {ft.mask_to_binary(ft.mask)}, expected {expected_mask}"


def test_string_output_formats():
    # Test with seconds provided
    ft = flex_time("14:30:45")
    assert ft.to_str(output_format="short") == "14:30:45"

    # Test with only hour and minute
    ft = flex_time("14:30")
    assert ft.to_str(output_format="short") == "14:30"

    # Test with only hour - should still show minutes
    ft = flex_time("14")
    assert ft.to_str(output_format="short") == "14:00"


def test_to_components():
    # Full time provided
    ft = flex_time("14:30:45")
    components = ft.to_components()
    assert components == {"hour": 14, "minute": 30, "second": 45}

    # Test with only hours and minutes
    ft = flex_time("14:30")  # second is masked
    components = ft.to_components()
    assert components == {"hour": 14, "minute": 30}
    assert "second" not in components


@pytest.mark.parametrize(
    "time_str, reason",
    [
        ("14:30:61", "invalid second"),
        ("14:60", "invalid minute"),
        ("25:00", "invalid hour"),
        ("invalid", "invalid format"),
        ("14:30:12.1234567", "too many microsecond digits"),
        (":30", "missing hour"),
    ],
)
def test_invalid_formats(time_str, reason):
    """Test that invalid formats raise ValueError with clear error messages."""
    try:
        result = flex_time(time_str)
        pytest.fail(
            f"Expected ValueError for '{time_str}' ({reason}) result={result}\n"
            f"Instead got: time={result.time}, mask={result.mask_to_binary(result.mask)}"
        )
    except ValueError:
        pass  # This is what we want - these should raise ValueError


def test_in_pydantic_model():
    class TimeModel(BaseModel):
        time_field: flex_time

    # Test with string
    model = TimeModel(time_field=flex_time("14:30"))
    assert model.time_field.hour == 14
    assert model.time_field.minute == 30
    assert model.time_field.mask_to_binary(model.time_field.mask) == "0011"

    # Test with dict
    model = TimeModel(time_field=flex_time({"hour": 14, "minute": 30}))
    assert model.time_field.hour == 14
    assert model.time_field.minute == 30
    assert model.time_field.mask_to_binary(model.time_field.mask) == "0011"

    # Test serialization/deserialization
    json_str = model.model_dump_json()
    model2 = TimeModel.model_validate_json(json_str)
    assert model.time_field == model2.time_field


def test_meridian_format():
    # Test AM/PM formats with expected masks
    test_cases = [
        ("12am", time(0, 0, 0), "0011"),
        ("12pm", time(12, 0, 0), "0011"),
        ("1am", time(1, 0, 0), "0011"),
        ("1pm", time(13, 0, 0), "0011"),
        ("11:30am", time(11, 30, 0), "0011"),
        ("11:30pm", time(23, 30, 0), "0011"),
        ("11:30:00am", time(11, 30, 0), "0001"),
        ("11:30:00pm", time(23, 30, 0), "0001"),
    ]

    for time_str, expected_time, expected_mask in test_cases:
        ft = flex_time(time_str)
        assert ft.time == expected_time, f"Failed for input: {time_str}"
        assert ft.mask_to_binary(ft.mask) == expected_mask, f"Wrong mask for input: {time_str}"


def test_get_comparable_time():
    # Test with seconds provided
    t1 = flex_time("14:30:45")
    comparable = t1.get_comparable_time()
    assert comparable == time(14, 30, 45)

    # Test with only hours and minutes
    t2 = flex_time("14:30")
    comparable = t2.get_comparable_time()
    assert comparable == time(14, 30, 0)  # seconds zeroed out


def test_24hour_format():
    """Test 24-hour time formats."""
    test_cases = [
        # With seconds (HH:mm:ss)
        ("14:30:45", time(14, 30, 45), "0001"),  # normal case
        ("00:00:00", time(0, 0, 0), "0001"),  # midnight
        ("23:59:59", time(23, 59, 59), "0001"),  # end of day
        # Without seconds (HH:mm)
        ("14:30", time(14, 30, 0), "0011"),  # normal case
        ("00:00", time(0, 0, 0), "0011"),  # midnight
        ("23:59", time(23, 59, 0), "0011"),  # end of day
    ]

    for time_str, expected_time, expected_mask in test_cases:
        ft = flex_time(time_str)
        assert ft.time == expected_time, f"Time parsing failed for input: {time_str}"
        assert ft.mask_to_binary(ft.mask) == expected_mask, f"Mask failed for input: {time_str}"


def test_12hour_format():
    """Test 12-hour time formats with AM/PM."""
    test_cases = [
        # With space before AM/PM (h:mm A/a)
        ("2:30 AM", time(2, 30, 0), "0011"),  # morning
        ("2:30 PM", time(14, 30, 0), "0011"),  # afternoon
        ("12:00 AM", time(0, 0, 0), "0011"),  # midnight
        ("12:00 PM", time(12, 0, 0), "0011"),  # noon
        ("11:59 PM", time(23, 59, 0), "0011"),  # end of day
        # With leading zero (hh:mm a)
        ("02:30 am", time(2, 30, 0), "0011"),  # morning
        ("02:30 pm", time(14, 30, 0), "0011"),  # afternoon
        # Without space before AM/PM (h:mmA/a)
        ("2:30AM", time(2, 30, 0), "0011"),  # morning
        ("2:30PM", time(14, 30, 0), "0011"),  # afternoon
        # With seconds
        ("2:30:00 AM", time(2, 30, 0), "0001"),  # morning with seconds
        ("2:30:00 PM", time(14, 30, 0), "0001"),  # afternoon with seconds
    ]

    for time_str, expected_time, expected_mask in test_cases:
        ft = flex_time(time_str)
        assert ft.time == expected_time, f"Time parsing failed for input: {time_str}"
        assert ft.mask_to_binary(ft.mask) == expected_mask, f"Mask failed for input: {time_str}"


def test_hour_only_format():
    """Test hour-only formats with AM/PM."""
    test_cases = [
        # Hour only with AM/PM (ha)
        ("2AM", time(2, 0, 0), "0011"),  # morning
        ("2PM", time(14, 0, 0), "0011"),  # afternoon
        ("12AM", time(0, 0, 0), "0011"),  # midnight
        ("12PM", time(12, 0, 0), "0011"),  # noon
        # Hour only with space (h a)
        ("2 AM", time(2, 0, 0), "0011"),  # morning
        ("2 PM", time(14, 0, 0), "0011"),  # afternoon
        ("12 AM", time(0, 0, 0), "0011"),  # midnight
        ("12 PM", time(12, 0, 0), "0011"),  # noon
        # Single digit cases
        ("9am", time(9, 0, 0), "0011"),  # morning
        ("9pm", time(21, 0, 0), "0011"),  # evening
    ]

    for time_str, expected_time, expected_mask in test_cases:
        ft = flex_time(time_str)
        assert ft.time == expected_time, f"Time parsing failed for input: {time_str}"
        assert ft.mask_to_binary(ft.mask) == expected_mask, f"Mask failed for input: {time_str}"


def test_special_formats():
    """Test special cases and variations in format."""
    test_cases = [
        # Period notation in AM/PM
        ("1:30P.M.", time(13, 30, 0), "0011"),  # with periods
        ("1:30 P.M.", time(13, 30, 0), "0011"),  # with periods and space
        # Dots instead of colons
        ("14.30", time(14, 30, 0), "0011"),  # dots
        ("14.30.45", time(14, 30, 45), "0001"),  # dots with seconds
        ("2.30pm", time(14, 30, 0), "0011"),  # dots with pm
        # Extra spaces
        ("14 : 30", time(14, 30, 0), "0011"),  # spaces around colon
        ("2 :30 PM", time(14, 30, 0), "0011"),  # irregular spaces
    ]

    for time_str, expected_time, expected_mask in test_cases:
        ft = flex_time(time_str)
        assert ft.time == expected_time, f"Time parsing failed for input: {time_str}"
        assert ft.mask_to_binary(ft.mask) == expected_mask, f"Mask failed for input: {time_str}"


def test_natural_language_formats():
    """Test natural language time expressions that specifically map to exact times."""
    test_cases = [
        # Specific fixed times
        ("noon", time(12, 0, 0), "0011"),
        ("midnight", time(0, 0, 0), "0011"),
        ("midday", time(12, 0, 0), "0011"),
        # Natural variations of midnight
        ("mid night", time(0, 0, 0), "0011"),
        ("mid-night", time(0, 0, 0), "0011"),
        # Natural variations of noon/midday
        ("mid day", time(12, 0, 0), "0011"),
        ("mid-day", time(12, 0, 0), "0011"),
        # Case variations
        ("NOON", time(12, 0, 0), "0011"),
        ("Midnight", time(0, 0, 0), "0011"),
        ("MidDay", time(12, 0, 0), "0011"),
        ("MidNight", time(0, 0, 0), "0011"),
        # times that might be prefixed
        ("at 9pm", time(21, 0, 0), "0011"),
        ("before 9pm", time(21, 0, 0), "0011"),
        ("after 9pm", time(21, 0, 0), "0011"),
        ("by 9pm", time(21, 0, 0), "0011"),
        # more times that might be prefixed
        ("at 9", time(9, 0, 0), "0011"),
        ("before 9", time(9, 0, 0), "0011"),
        ("after 9", time(9, 0, 0), "0011"),
        ("by 9", time(9, 0, 0), "0011"),
    ]

    for time_str, expected_time, expected_mask in test_cases:
        ft = flex_time(time_str)
        assert ft.time == expected_time, f"Time parsing failed for input: {time_str}"
        assert ft.mask_to_binary(ft.mask) == expected_mask, f"Mask failed for input: {time_str}"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
