import json
from datetime import date, datetime

import arrow
import pytest
from pydantic import BaseModel

from flexible_datetime import FlexDateTime, flextime


def test_dump_load():
    ft = flextime()
    d = json.dumps(ft.to_json())
    ft2 = flextime.from_json(d)
    assert ft == ft2


def test_dump_load_ymd():
    ft = flextime()
    ft.use_only("year", "month", "day")
    d = json.dumps(ft.to_json())
    ft2 = flextime.from_json(d)
    assert ft == ft2
    assert ft2.mask_str == "0001111"


def test_from_dict():
    d = {"year": 2023, "month": 6, "day": 29}
    ft = flextime(d)
    assert ft.dt == arrow.get("2023-06-29")
    assert ft.mask_str == "0001111"
    assert ft.year == 2023
    assert ft.month == 6
    assert ft.day == 29


def test_from_datetime():
    dt = datetime.now()
    at = arrow.get(dt)
    ft = flextime(dt)

    assert ft.dt == at


def test_from_flexdatetime():

    fdt = FlexDateTime()
    ft = flextime(fdt)

    assert ft.dt == fdt.dt
    assert ft.mask == fdt.mask


def test_from_arrow():
    at = arrow.get()
    ft = flextime(at)

    assert ft.dt == at


def test_dump_load_mode_json():
    ft = flextime()
    d = json.dumps(ft.to_json())
    ft2 = flextime.from_json(d)
    assert ft == ft2


def test_dump_load_mode_json_mask_YYYY():
    ft = flextime()
    ft.use_only("year")
    d = json.dumps(ft.to_json())
    ft2 = flextime.from_json(d)
    assert ft == ft2


def test_from_dict_ymd():
    ft = flextime.from_dict({"year": 2023, "month": 6, "day": 29})
    assert ft.dt == arrow.get("2023-06-29")


def test_from_dict_ym():
    ft = flextime.from_dict({"year": 2023, "month": 6})
    assert ft.dt == arrow.get("2023-06")
    mask = ft.mask_to_binary(ft.mask)
    assert mask == "0011111"


def test_from_flex():
    ft = flextime({"dt": "2023-06-29", "mask": "0001111"})
    assert ft.dt == arrow.get("2023-06-29")
    mask = ft.mask_to_binary(ft.mask)
    assert mask == "0001111"


def test_from_flex_dict_mask():
    ft = flextime(
        {
            "dt": "2023-06-29",
            "mask": {
                "year": False,
                "month": False,
                "day": False,
                "hour": True,
                "minute": True,
                "second": True,
                "millisecond": True,
            },
        }
    )
    assert ft.dt == arrow.get("2023-06-29")
    mask = ft.mask_to_binary(ft.mask)
    assert mask == "0001111"


def test_from_dict_y():
    ft = flextime.from_dict({"year": 2023})
    assert ft.dt == arrow.get("2023")


def test_y():
    ft = flextime({"year": 2023})
    assert ft.dt == arrow.get("2023")


def test_y_str():
    ft = flextime(f"2023")
    assert ft.dt == arrow.get("2023")


def test_in_class_from_datetime():
    class Test(BaseModel):
        ft: flextime

    js = {"ft": datetime.now()}
    t = Test(**js)  # type: ignore
    assert t.ft.dt == arrow.get(js["ft"])


def test_in_class_from_str():
    class Test(BaseModel):
        ft: flextime

    js = {"ft": "2023-06-29"}
    t = Test(**js)  # type: ignore
    assert t.ft.dt == arrow.get(js["ft"])


def test_in_class_from_components():
    class Test(BaseModel):
        ft: flextime

    js = {"ft": {"year": 2023, "month": 6, "day": 29}}
    t = Test(**js)  # type: ignore
    assert t.ft.dt == arrow.get("2023-06-29")


def test_in_class_from_flexdatetime():
    class Test(BaseModel):
        ft: flextime

    fdt = FlexDateTime("2023-06-29")
    js = {"ft": fdt}
    t = Test(**js)  # type: ignore
    assert t.ft.dt == arrow.get("2023-06-29")


def test_in_class_from_components_dump_load():
    class Test(BaseModel):
        ft: flextime

    js = {"ft": {"year": 2023, "month": 6, "day": 29}}
    t = Test(**js)  # type: ignore
    assert t.ft.dt == arrow.get("2023-06-29")
    d = json.dumps(t.model_dump())
    t2 = Test(**json.loads(d))
    assert t == t2


def test_from_date():
    # Creating a Python date object
    dt = date(2022, 6, 2)
    ft = flextime(dt)

    # Expected output is the corresponding arrow object
    expected_dt = arrow.get(dt)
    assert ft.dt == expected_dt
    assert ft.year == 2022
    assert ft.month == 6
    assert ft.day == 2
    assert ft.mask_str == "0001111"


def test_dump_load_from_date():
    # Creating a Python date object and passing it to flextime
    ft = flextime(date(2022, 6, 2))
    d = json.dumps(ft.to_json())

    # Loading the json back and ensuring the object remains the same
    ft2 = flextime.from_json(d)
    assert ft == ft2
    assert ft2.year == 2022
    assert ft2.month == 6
    assert ft2.day == 2
    assert ft.mask_str == "0001111"


def test_from_dateutil():
    ft = flextime("Aug 28")
    now_ft = flextime()
    assert ft.dt == arrow.get(f"{now_ft.year}-08-28")
    assert ft.mask_str == "0001111"


def test_from_dateutil_with_year():
    ft = flextime("Aug 28, 2024")
    assert ft.dt == arrow.get("2024-08-28")
    assert ft.mask_str == "0001111"


def test_from_natural_language():
    # Since we're using dateutil.parser, let's align with its behavior
    from dateutil import parser

    reference_time = arrow.get("2024-01-28 10:00:00", tzinfo="local")
    input_str = "next thursday at 2pm"

    # Parse using dateutil to match the actual code path
    parsed_dt = parser.parse(input_str, fuzzy=True)
    if parsed_dt.year == 1900:  # Match the code's year fixing logic
        parsed_dt = parsed_dt.replace(year=reference_time.year)

    # Convert to Arrow for comparison
    expected_dt = arrow.get(parsed_dt).to("UTC")

    # Create flextime instance
    ft = flextime(input_str)

    print(f"Reference time: {reference_time}")
    print(f"Parsed datetime: {parsed_dt}")
    print(f"Expected UTC: {expected_dt}")
    print(f"Actual ft.dt: {ft.dt}")

    assert ft.dt == expected_dt
    assert ft.mask_str == "0000000"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
