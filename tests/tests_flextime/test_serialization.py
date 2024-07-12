import json
from datetime import datetime

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


if __name__ == "__main__":
    pytest.main([__file__])
