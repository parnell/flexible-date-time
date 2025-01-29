
# Flexible Datetime

A Python library providing flexible datetime creation and handling with masked comparison capabilities, built on Arrow and Pydantic.

## Features

Parse dates and times from:
- ISO format strings
- Partial dates ("2023-06", "2023")
- Natural language ("June 15th, 2023", "next thursday")
- Component dictionaries ({"year": 2023, "month": 6})
- Python datetime/date objects
- Arrow objects
- Component masking for selective comparisons
- Multiple serialization formats

## Installation

```bash
pip install flexible-datetime
```

## Usage

```python

from flexible_datetime import flex_datetime

# Parse various formats
ft = flex_datetime("2023-06")                      # Partial date
ft = flex_datetime({"year": 2023, "month": 6})     # From components
ft = flex_datetime("next thursday at 2pm")         # Natural language
ft = flex_datetime("2023-06-15T14:30:45")          # ISO format

print(ft) 
# Output: 2023-06-15T14:30:45
```

### Output Formats

```python
ft = flex_datetime("2023-06-15")          # ISO format

# Choose output formats
print(ft) # default: Serialize as shortest possible datetime format.                      
# Output: 2023-06-15
print(ft.to_str("flex")) # JSON with mask           
# Output: {'dt': '2023-06-15T00:00:00+00:00', 'mask': '0001111'}

print(ft.to_str("datetime")) # Full ISO format
# Output: 2023-06-15T00:00:00+00:00
print(ft.to_str("components")) # Component dict
# Output {'year': 2023, 'month': 6, 'day': 15}
```


### Component Masking

Mask specific components for flexible comparisons:

```python
# Mask specific components
ft = flex_datetime("2023-06-15T14:30")
ft.apply_mask(hour=True, minute=True)  # Mask time components
print(ft)                              # "2023-06-15"

# Clear all masks
ft.clear_mask()

# Use only specific components
ft.use_only("year", "month")           # Only use year and month
print(ft)                              # "2023-06"

# Use masking for flexible comparisons
ft1 = flex_datetime("2023-01-15")
ft2 = flex_datetime("2024-01-15")
ft1.apply_mask(year=True) # Mask the year
ft2.apply_mask(year=True) # Mask the year
print(ft1 == ft2) # True - years are masked
```

### Component Access

Access individual components directly:

```python
ft = flex_datetime("2023-06-15T14:30")
print(ft.year)                          # 2023
print(ft.month)                         # 6
print(ft.day)                           # 15
print(ft.hour)                          # 14
print(ft.minute)                        # 30
```

## Output Format Specific Classes

The library provides specialized classes for when you know you'll consistently need a specific output format:

```python
from flexible_datetime import dict_datetime, minimal_time, iso_datetime, mask_datetime

# Component format - outputs as dictionary of datetime components
ct = dict_datetime("2023-06-15T14:30")
print(ct)  
# {"year": 2023, "month": 6, "day": 15, "hour": 14, "minute": 30}

# Minimal format - outputs shortest possible datetime representation
mt = short_datetime("2023-06-15T14:30")
print(mt)  
# "2023-06-15T14:30"

# ISO format - outputs full ISO8601 datetime
it = iso_datetime("2023-06-15T14:30")
print(it)  
# "2023-06-15T14:30:00+00:00"

# Masked format - outputs datetime with mask information
ft = mask_datetime("2023-06")
print(ft)  
# {"dt": "2023-06-01T00:00:00+00:00", "mask": "0011111"}
```

Each class inherits all functionality from `flex_datetime` but provides a consistent output format:

- `dict_datetime`: Best for when you need to access individual components programmatically
- `minimal_time`: Best for human-readable output showing only specified components
- `iso_datetime`: Best for standardized datetime strings and interoperability
- `mask_datetime`: Best for scenarios where mask information needs to be preserved

All methods and features (masking, comparison, component access) work the same way:

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
