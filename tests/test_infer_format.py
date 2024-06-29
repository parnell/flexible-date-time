import pytest
from dateutil.parser._parser import ParserError
from flexible_datetime import FlexDateTime  # Replace 'your_module' with the actual module name

def test_format_YYYY():
    assert FlexDateTime.infer_format("2023") == "YYYY"

def test_format_YYYYMM():
    """ This test should fail. The format isn't recognized by dateutil. and is uncommon"""
    with pytest.raises(ParserError):
        assert FlexDateTime.infer_format("202306") == "YYYYMM"

def test_format_YYYY_MM():
    assert FlexDateTime.infer_format("2023-06") == "YYYY-MM"

def test_format_YYYYMMDD():
    assert FlexDateTime.infer_format("20230629") == "YYYYMMDD"

def test_format_YYYY_MM_DD():
    assert FlexDateTime.infer_format("2023-06-29") == "YYYY-MM-DD"

def test_format_YYYY_MM_DDTHH():
    assert FlexDateTime.infer_format("2023-06-29T14") == "YYYY-MM-DDTHH"

def test_format_YYYYMMDDTHHmm():
    assert FlexDateTime.infer_format("20230629T1455") == "YYYYMMDDTHHmm"

def test_format_YYYY_MM_DDTHH_mm():
    assert FlexDateTime.infer_format("2023-06-29T14:55") == "YYYY-MM-DDTHH:mm"

def test_format_YYYYMMDDTHHmmss():
    assert FlexDateTime.infer_format("20230629T145530") == "YYYYMMDDTHHmmss"

def test_format_YYYY_MM_DDTHH_mm_ss():
    assert FlexDateTime.infer_format("2023-06-29T14:55:30") == "YYYY-MM-DDTHH:mm:ss"

def test_format_YYYYMMDDTHHmmssSSS():
    assert FlexDateTime.infer_format("20230629T145530.123") == "YYYYMMDDTHHmmssSSS"

def test_format_YYYY_MM_DDTHH_mm_ssSSS():
    assert FlexDateTime.infer_format("2023-06-29T14:55:30.123") == "YYYY-MM-DDTHH:mm:ssSSS"

def test_format_YYYYMMDDTHHmmssSSSSSS():
    assert FlexDateTime.infer_format("20230629T145530.123456") == "YYYYMMDDTHHmmssSSSSSS"

def test_format_YYYY_MM_DDTHH_mm_ssSSSSSS():
    assert FlexDateTime.infer_format("2023-06-29T14:55:30.123456") == "YYYY-MM-DDTHH:mm:ssSSSSSS"

def test_format_YYYYMMDDTHHmmssSSSSSSZZ():
    assert FlexDateTime.infer_format("20230629T145530.123456Z") == "YYYYMMDDTHHmmssSSSSSSZZ"

def test_format_YYYY_MM_DDTHH_mm_ssSSSSSSZZ():
    assert FlexDateTime.infer_format("2023-06-29T14:55:30.123456+00:00") == "YYYY-MM-DDTHH:mm:ssSSSSSSZZ"

def test_invalid_format():
    with pytest.raises(ValueError):
        FlexDateTime.infer_format("invalid_date")

# Run the tests
if __name__ == "__main__":
    pytest.main(["-v", __file__])