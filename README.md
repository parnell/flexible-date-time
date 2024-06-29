
# FlexDateTime

`FlexDateTime` is a Python class that provides flexible and enhanced functionality for handling and comparing dates and times using the Arrow library and Pydantic. 

## Description

The `FlexDateTime` class allows you to:
- Parse dates and times from strings with various formats
- Mask specific components (year, month, day, hour, minute, second) for comparison purposes
- Serialize and deserialize dates and times with Pydantic V2
- Easily compare dates and times with masked components

## Installation

To use `FlexDateTime`, you need to install the dependencies: `arrow` and `pydantic`.

```bash
pip install flexible-datetime
```

## Usage

### Creating an Instance

You can create a `FlexDateTime` instance by providing a date string and an optional input format.

```python
from flexdatetime import FlexDateTime

# Create an instance with the current utc time
current_time = FlexDateTime()

# Create an instance from a date string
date_time = FlexDateTime.from_str("2023-06-28T15:30:00")

# Create an instance from a date string with only year month day
date_time = FlexDateTime.from_str("2023-06-28")

# Create an instance from a date string with only year and moth
date_time = FlexDateTime.from_str("2023-06")

# Create an instance from a date string with only year
date_time = FlexDateTime.from_str("2023")
```

### Masking Components

Masking is automatically determined at initialization, but can also be explicitly set.

Mask specific components of the date/time to exclude them from comparisons.

```python
# Mask the year and month
date_time.apply_mask(year=True, month=True)
```

### Comparing Instances

You can compare `FlexDateTime` instances while respecting the mask.

```python
date_time1 = FlexDateTime.from_str("2023-01-01T15:30:00")
date_time2 = FlexDateTime.from_str("2024-01-01")
date_time1.apply_mask(day=True, hour=True, second=True)
# Compare the two instances
print(date_time1 == date_time2)  # True, because only the year, month, day have not been masked
```

### String Representation

Get the string representation of the date/time considering the mask.

```python
date_time = FlexDateTime.from_str("2000-01")
print(str(date_time))  # Output: "2000-01"
```

## Example

Here's a complete example demonstrating the usage of `FlexDateTime`:

```python
from flexdatetime import FlexDateTime

# Create an instance from a date string
date_time1 = FlexDateTime.from_str("2000-01-01")
date_time2 = FlexDateTime.from_str("2024-01-01")

# Mask the year
date_time2.apply_mask(year=True)

# Compare the two instances
print(date_time == another_date_time)  # True, because the year is masked
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
