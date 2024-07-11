import json
from datetime import datetime

import arrow
import pytest
from pydantic import BaseModel

from flexible_datetime import flextime


def test_dump_load():
    fdt = flextime()
    d = json.dumps(fdt.to_json())
    fdt2 = flextime.from_json(d)
    assert fdt == fdt2


def test_dump_load_ymd():
    fdt = flextime()
    fdt.use_only("year", "month", "day")
    d = json.dumps(fdt.to_json())
    fdt2 = flextime.from_json(d)
    assert fdt == fdt2
    assert fdt2.mask_str == "0001111"


def test_from_dict():
    d = {"year": 2023, "month": 6, "day": 29}
    fdt = flextime(d)
    assert fdt.dt == arrow.get("2023-06-29")
    assert fdt.mask_str == "0001111"
    assert fdt.year == 2023
    assert fdt.month == 6
    assert fdt.day == 29


def test_from_datetime():
    dt = datetime.now()
    at = arrow.get(dt)
    fdt = flextime(dt)

    assert fdt.dt == at


def test_from_arrow():
    at = arrow.get()
    fdt = flextime(at)

    assert fdt.dt == at


def test_dump_load_mode_json():
    fdt = flextime()
    d = json.dumps(fdt.to_json())
    fdt2 = flextime.from_json(d)
    assert fdt == fdt2


def test_dump_load_mode_json_mask_YYYY():
    fdt = flextime()
    fdt.use_only("year")
    d = json.dumps(fdt.to_json())
    fdt2 = flextime.from_json(d)
    assert fdt == fdt2


def test_from_dict_ymd():
    fdt = flextime.from_dict({"year": 2023, "month": 6, "day": 29})
    assert fdt.dt == arrow.get("2023-06-29")


def test_from_dict_ym():
    fdt = flextime.from_dict({"year": 2023, "month": 6})
    assert fdt.dt == arrow.get("2023-06")
    mask = fdt.mask_to_binary(fdt.mask)
    assert mask == "0011111"


def test_from_dict_y():
    fdt = flextime.from_dict({"year": 2023})
    assert fdt.dt == arrow.get("2023")


def test_y():
    fdt = flextime({"year": 2023})
    assert fdt.dt == arrow.get("2023")


def test_y_str():
    fdt = flextime(f"2023")
    assert fdt.dt == arrow.get("2023")


def test_in_class_from_datetime():
    class Test(BaseModel):
        fdt: flextime

    js = {"fdt": datetime.now()}
    t = Test(**js)  # type: ignore
    assert t.fdt.dt == arrow.get(js["fdt"])


def test_in_class_from_str():
    class Test(BaseModel):
        # ar : arrow.Arrow
        fdt: flextime

    js = {"fdt": "2023-06-29"}
    t = Test(**js)  # type: ignore
    assert t.fdt.dt == arrow.get(js["fdt"])


def test_in_class_from_components():
    class Test(BaseModel):
        # ar : arrow.Arrow
        fdt: flextime

    js = {"fdt": {"year": 2023, "month": 6, "day": 29}}
    t = Test(**js)  # type: ignore
    assert t.fdt.dt == arrow.get("2023-06-29")


def test_in_class_from_components_dump_load():
    class Test(BaseModel):
        # ar : arrow.Arrow
        fdt: flextime

    js = {"fdt": {"year": 2023, "month": 6, "day": 29}}
    t = Test(**js)  # type: ignore
    assert t.fdt.dt == arrow.get("2023-06-29")
    d = json.dumps(t.model_dump())
    t2 = Test(**json.loads(d))
    assert t == t2


if __name__ == "__main__":
    pytest.main([__file__])
