import arrow
import pytest
from pydantic import BaseModel

from flexible_datetime import FlexDateTime


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


def test_dump_load_mode_json_mask_YYYY():
    fdt = FlexDateTime()
    fdt.use_only("year")
    d = fdt.model_dump(mode="json")
    fdt2 = FlexDateTime(**d)
    assert fdt == fdt2


def test_from_dict_ymd():
    fdt = FlexDateTime.from_dict({"year": 2023, "month": 6, "day": 29})
    assert fdt.dt == arrow.get("2023-06-29")


def test_from_dict_ym():
    fdt = FlexDateTime.from_dict({"year": 2023, "month": 6})
    assert fdt.dt == arrow.get("2023-06")
    mask = fdt.mask_to_binary(fdt.mask)
    assert mask == "0011111"


def test_from_dict_y():
    fdt = FlexDateTime.from_dict({"year": 2023})
    assert fdt.dt == arrow.get("2023")


if __name__ == "__main__":
    pytest.main([__file__])
