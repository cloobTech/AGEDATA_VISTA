from datetime import datetime

# Define the desired output format
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

# Define fallback formats for parsing unknown date strings
FALLBACK_FORMATS = [
    "%Y-%m-%dT%H:%M:%S.%f",          # ISO format with seconds/milliseconds
    "%Y-%m-%dT%H:%M:%S",       # ISO format with seconds
    "%Y-%m-%dT%H:%M",          # ISO format without seconds/milliseconds
    "%Y-%m-%d %H:%M:%S",       # Common format with space
    "%Y/%m/%d %H:%M:%S",       # Slash-separated
    "%Y-%m-%d",                # Date only
    "%d-%m-%Y",                # European-style day-month-year
]


def parse_and_format_datetime(input_date: str) -> datetime:
    """
    Parses a date string of unknown format into a datetime object
    and converts it to the desired format.

    Args:
        input_date (str): The date string to parse.

    Returns:
        datetime: A datetime object normalized to the desired format.

    Raises:
        ValueError: If no fallback format matches the input string.
    """

    try:
        # First, check if the input already matches the desired format
        return datetime.strptime(input_date, TIME_FORMAT)
    except ValueError:
        # If it doesn't match, proceed to fallback formats
        pass

    for fmt in FALLBACK_FORMATS:
        try:
            # Attempt to parse the date string using each format
            parsed_date = datetime.strptime(input_date, fmt)
            # Return the normalized datetime object
            return datetime.strptime(parsed_date.strftime(TIME_FORMAT), TIME_FORMAT)
        except ValueError:
            continue

    # If all formats fail, raise an exception
    raise ValueError(f"Invalid date format: {input_date}")
