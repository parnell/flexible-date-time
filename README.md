
# FlexDateTime

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
from flexible_datetime import flextime

# Parse various formats
ft = flextime("2023-06")                      # Partial date
ft = flextime({"year": 2023, "month": 6})     # From components
ft = flextime("next thursday at 2pm")         # Natural language
ft = flextime("2023-06-15T14:30:45")          # ISO format

# Choose output formats
print(ft)                                     # Default: 2023-06-15 14:30:45
print(ft.to_str("flex"))                      # JSON with mask
print(ft.to_str("datetime"))                  # Full ISO format
print(ft.to_str("components"))                # Component dict

# Use masking for flexible comparisons
ft1 = flextime("2023-01-15")
ft2 = flextime("2024-01-15")
ft1.apply_mask(year=True)                     # Mask the year
print(ft1 == ft2)                             # True - years are masked
```

### Output Formats

Control how your datetime is represented:

```python
ft = flextime("2023-06-15T14:30")

# Use to_str() for one-off format changes
print(ft.to_str("minimal_datetime"))   # "2023-06-15 14:30"
print(ft.to_str("datetime"))           # "2023-06-15T14:30:00+00:00"
print(ft.to_str("flex"))               # {"dt": "2023-06-15T14:30:00+00:00", "mask": "0000011"}
print(ft.to_str("components"))         # {"year": 2023, "month": 6, "day": 15, "hour": 14, "minute": 30}

# Or set a default format
ft._output_format = "flex"              # All future str() calls use this format
```

### Component Masking

Mask specific components for flexible comparisons:

```python
# Mask specific components
ft = flextime("2023-06-15T14:30")
ft.apply_mask(hour=True, minute=True)  # Mask time components
print(ft)                              # "2023-06-15"

# Clear all masks
ft.clear_mask()

# Use only specific components
ft.use_only("year", "month")           # Only use year and month
print(ft)                              # "2023-06"
```

### Component Access

Access individual components directly:

```python
ft = flextime("2023-06-15T14:30")
print(ft.year)                          # 2023
print(ft.month)                         # 6
print(ft.day)                           # 15
print(ft.hour)                          # 14
print(ft.minute)                        # 30
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
