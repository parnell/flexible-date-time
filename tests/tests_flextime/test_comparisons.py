import pytest

from flexible_datetime import flex_datetime


def test_eq():
    fdt1 = flex_datetime("2024-06-28T14:30:00")
    fdt2 = flex_datetime("2024-06-28T14:30:00")
    assert fdt1 == fdt2


def test_ne():
    fdt1 = flex_datetime("2024-06-28T14:30:00")
    fdt2 = flex_datetime("2023-06-28T14:30:00")
    assert fdt1 != fdt2


def test_eq_with_mask():
    fdt1 = flex_datetime("2024-06-28T14:30:00")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2024-06-28T14:30:00")
    fdt2.apply_mask(year=True)
    assert fdt1 == fdt2


def test_ne_with_mask():
    fdt1 = flex_datetime("2024-06-28T14:30:00")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2023-06-28T14:30:00")
    fdt2.apply_mask(year=True)
    assert fdt1 == fdt2  # Masked year should make them equal


def test_lt():
    fdt1 = flex_datetime("2024-06-28T14:30:00")
    fdt2 = flex_datetime("2024-06-29T14:30:00")
    assert fdt1 < fdt2


def test_le():
    fdt1 = flex_datetime("2024-06-28T14:30:00")
    fdt2 = flex_datetime("2024-06-28T14:30:00")
    fdt3 = flex_datetime("2024-06-29T14:30:00")
    assert fdt1 <= fdt2
    assert fdt1 <= fdt3


def test_gt():
    fdt1 = flex_datetime("2024-06-29T14:30:00")
    fdt2 = flex_datetime("2024-06-28T14:30:00")
    assert fdt1 > fdt2


def test_ge():
    fdt1 = flex_datetime("2024-06-28T14:30:00")
    fdt2 = flex_datetime("2024-06-28T14:30:00")
    fdt3 = flex_datetime("2024-06-27T14:30:00")
    assert fdt1 >= fdt2
    assert fdt1 >= fdt3


def test_lt_with_mask():
    fdt1 = flex_datetime("2024-06-28T14:30:00")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2023-06-29T14:30:00")
    fdt2.apply_mask(year=True)
    assert fdt1 < fdt2  # Masked year should be ignored


def test_le_with_mask():
    fdt1 = flex_datetime("2024-06-28T14:30:00")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2023-06-28T14:30:00")
    fdt2.apply_mask(year=True)
    assert fdt1 <= fdt2  # Masked year should be ignored


def test_gt_with_mask():
    fdt1 = flex_datetime("2024-06-28T14:30:00")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2025-06-27T14:30:00")
    fdt2.apply_mask(year=True)
    assert fdt1 > fdt2  # Masked year should be ignored


def test_ge_with_mask():
    fdt1 = flex_datetime("2024-06-28T14:30:00")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2023-06-27T14:30:00")
    fdt2.apply_mask(year=True)
    assert fdt1 >= fdt2  # Masked year should be ignored


def test_eq_yyyy_mm_dd():
    fdt1 = flex_datetime("2024-06-28")
    fdt2 = flex_datetime("2024-06-28")
    assert fdt1 == fdt2


def test_ne_yyyy_mm_dd():
    fdt1 = flex_datetime("2024-06-28")
    fdt2 = flex_datetime("2023-06-28")
    assert fdt1 != fdt2


def test_eq_with_mask_yyyy_mm_dd():
    fdt1 = flex_datetime("2024-06-28")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2024-06-28")
    fdt2.apply_mask(year=True)
    assert fdt1 == fdt2


def test_ne_with_mask_yyyy_mm_dd():
    fdt1 = flex_datetime("2024-06-28")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2023-06-28")
    fdt2.apply_mask(year=True)
    assert fdt1 == fdt2  # Masked year should make them equal


def test_lt_yyyy_mm_dd():
    fdt1 = flex_datetime("2024-06-28")
    fdt2 = flex_datetime("2024-06-29")
    assert fdt1 < fdt2


def test_le_yyyy_mm_dd():
    fdt1 = flex_datetime("2024-06-28")
    fdt2 = flex_datetime("2024-06-28")
    fdt3 = flex_datetime("2024-06-29")
    assert fdt1 <= fdt2
    assert fdt1 <= fdt3


def test_gt_yyyy_mm_dd():
    fdt1 = flex_datetime("2024-06-29")
    fdt2 = flex_datetime("2024-06-28")
    assert fdt1 > fdt2


def test_ge_yyyy_mm_dd():
    fdt1 = flex_datetime("2024-06-28")
    fdt2 = flex_datetime("2024-06-28")
    fdt3 = flex_datetime("2024-06-27")
    assert fdt1 >= fdt2
    assert fdt1 >= fdt3


def test_lt_with_mask_yyyy_mm_dd():
    fdt1 = flex_datetime("2024-06-28")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2023-06-29")
    fdt2.apply_mask(year=True)
    assert fdt1 < fdt2  # Masked year should be ignored


def test_le_with_mask_yyyy_mm_dd():
    fdt1 = flex_datetime("2024-06-28")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2023-06-28")
    fdt2.apply_mask(year=True)
    assert fdt1 <= fdt2  # Masked year should be ignored


def test_gt_with_mask_yyyy_mm_dd():
    fdt1 = flex_datetime("2024-06-28")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2025-06-27")
    fdt2.apply_mask(year=True)
    assert fdt1 > fdt2  # Masked year should be ignored


def test_ge_with_mask_yyyy_mm_dd():
    fdt1 = flex_datetime("2024-06-28")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2023-06-27")
    fdt2.apply_mask(year=True)
    assert fdt1 >= fdt2  # Masked year should be ignored


def test_eq_yyyy_mm():
    fdt1 = flex_datetime("2024-06")
    fdt2 = flex_datetime("2024-06")
    assert fdt1 == fdt2


def test_ne_yyyy_mm():
    fdt1 = flex_datetime("2024-06")
    fdt2 = flex_datetime("2023-06")
    assert fdt1 != fdt2


def test_eq_with_mask_yyyy_mm():
    fdt1 = flex_datetime("2024-06")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2024-06")
    fdt2.apply_mask(year=True)
    assert fdt1 == fdt2


def test_ne_with_mask_yyyy_mm():
    fdt1 = flex_datetime("2024-06")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2023-06")
    fdt2.apply_mask(year=True)
    assert fdt1 == fdt2  # Masked year should make them equal


def test_lt_yyyy_mm():
    fdt1 = flex_datetime("2024-06")
    fdt2 = flex_datetime("2024-07")
    assert fdt1 < fdt2


def test_lt_yyyy_mm2():
    fdt1 = flex_datetime("2024-06")
    fdt2 = flex_datetime("2024-07")
    assert fdt1 < fdt2


def test_le_yyyy_mm():
    fdt1 = flex_datetime("2024-06")
    fdt2 = flex_datetime("2024-06")
    fdt3 = flex_datetime("2024-07")
    assert fdt1 <= fdt2
    assert fdt1 <= fdt3


def test_gt_yyyy_mm():
    fdt1 = flex_datetime("2024-07")
    fdt2 = flex_datetime("2024-06")
    assert fdt1 > fdt2


def test_ge_yyyy_mm():
    fdt1 = flex_datetime("2024-06")
    fdt2 = flex_datetime("2024-06")
    fdt3 = flex_datetime("2024-05")
    assert fdt1 >= fdt2
    assert fdt1 >= fdt3


def test_lt_with_mask_yyyy_mm():
    fdt1 = flex_datetime("2024-06")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2023-07")
    fdt2.apply_mask(year=True)
    assert fdt1 < fdt2  # Masked year should be ignored


def test_le_with_mask_yyyy_mm():
    fdt1 = flex_datetime("2024-06")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2023-06")
    fdt2.apply_mask(year=True)
    assert fdt1 <= fdt2  # Masked year should be ignored


def test_gt_with_mask_yyyy_mm():
    fdt1 = flex_datetime("2024-06")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2025-05")
    fdt2.apply_mask(year=True)
    assert fdt1 > fdt2  # Masked year should be ignored


def test_ge_with_mask_yyyy_mm():
    fdt1 = flex_datetime("2024-06")
    fdt1.apply_mask(year=True)
    fdt2 = flex_datetime("2023-05")
    fdt2.apply_mask(year=True)
    assert fdt1 >= fdt2  # Masked year should be ignored


def test_comparison_different_masks():
    fdt1 = flex_datetime("2024-06-28")
    fdt2 = flex_datetime("2024-06-28")
    fdt1.apply_mask(year=True)
    fdt2.apply_mask(month=True)

    with pytest.raises(ValueError):
        assert fdt1 == fdt2

    with pytest.raises(ValueError):
        assert fdt1 <= fdt2

    with pytest.raises(ValueError):
        assert fdt1 >= fdt2

    with pytest.raises(ValueError):
        assert fdt1 != fdt2

    with pytest.raises(ValueError):
        assert fdt1 > fdt2

    with pytest.raises(ValueError):
        assert fdt1 < fdt2


if __name__ == "__main__":
    pytest.main([__file__])
