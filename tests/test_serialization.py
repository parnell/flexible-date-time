import pytest
import arrow

from flexible_datetime import FlexDateTime
from pydantic import BaseModel

def test_dump_load():
    class T(BaseModel):
        fdt: FlexDateTime
    fdt = FlexDateTime()
    d = fdt.model_dump()
    fdt2 = FlexDateTime(**d)
    assert fdt == fdt2

def test_dump_load_mode_json():
    fdt = FlexDateTime()
    d = fdt.model_dump(mode="json")
    fdt2 = FlexDateTime(**d)
    assert fdt == fdt2

def test_from_dict_ymd():
    fdt = FlexDateTime.from_dict({"year": 2023, "month": 6, "day": 29})
    assert fdt.dt == arrow.get("2023-06-29")

def test_from_dict_ym():
    fdt = FlexDateTime.from_dict({"year": 2023, "month": 6})
    assert fdt.dt == arrow.get("2023-06")

def test_from_dict_y():
    fdt = FlexDateTime.from_dict({"year": 2023})
    assert fdt.dt == arrow.get("2023")

if __name__ == "__main__":
    pytest.main([__file__])
