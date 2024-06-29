import re

from dateutil.parser import parse


def infer_time_format(date_str: str) -> str:
    """
    Infers the date format from the given date string, including handling milliseconds.
    """
    dt = parse(date_str)

    # Generate format string based on the parsed datetime object
    if re.match(r"^\d{4}$", date_str):
        return "YYYY"
    if re.match(r"^\d{4}(-|/)\d{2}$", date_str):
        return "YYYY-MM"
    if re.match(r"^\d{8}$", date_str):
        return "YYYYMMDD"
    if re.match(r"^\d{4}(-|/)\d{2}(-|/)\d{2}$", date_str):
        return "YYYY-MM-DD"
    if re.match(r"^\d{4}(-|/)\d{2}(-|/)\d{2}T\d{2}$", date_str):
        return "YYYY-MM-DDTHH"
    if re.match(r"^\d{8}T\d{4}$", date_str):
        return "YYYYMMDDTHHmm"
    if re.match(r"^\d{4}(-|/)\d{2}(-|/)\d{2}T\d{2}:\d{2}$", date_str):
        return "YYYY-MM-DDTHH:mm"
    if re.match(r"^\d{8}T\d{6}$", date_str):
        return "YYYYMMDDTHHmmss"
    if re.match(r"^\d{4}(-|/)\d{2}(-|/)\d{2}T\d{2}:\d{2}:\d{2}$", date_str):
        return "YYYY-MM-DDTHH:mm:ss"

    # Handle milliseconds
    if re.match(r"^\d{8}T\d{6}\.\d{1,6}Z?$", date_str):
        milliseconds = date_str.split(".")[-1].rstrip("Z")
        ms_length = len(milliseconds)
        if date_str.endswith("Z"):
            return "YYYYMMDDTHHmmss" + "S" * ms_length + "ZZ"
        else:
            return "YYYYMMDDTHHmmss" + "S" * ms_length
    if re.match(
        r"^\d{4}(-|/)\d{2}(-|/)\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}(Z|\+\d{2}:\d{2})?$", date_str
    ):
        milliseconds = date_str.split(".")[-1].rstrip("Z")
        ms_length = len(milliseconds.split("+")[0])
        if "Z" in date_str or "+" in date_str:
            return "YYYY-MM-DDTHH:mm:ss" + "S" * ms_length + "ZZ"
        else:
            return "YYYY-MM-DDTHH:mm:ss" + "S" * ms_length

    if "Z" in date_str or "+" in date_str:
        return "YYYY-MM-DDTHH:mm:ssSSSSSSZZ"

    raise ValueError(f"Unknown date format for {date_str}")
