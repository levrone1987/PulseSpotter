import re

import dateparser
from more_itertools import first


def parse_date(value: str, output_format: str = "%Y-%m-%d"):
    # Regular expression to find potential date patterns
    date_patterns = [
        r'\d{1,2}[./-]\d{1,2}[./-]\d{2,4}', # Dates with different delimiters: dd-mm-yyyy, mm-dd-yyyy, dd.mm.yyyy, dd/mm/yyyy
        r'\d{4}[./-]\d{2}[./-]\d{2}',  # ISO-like dates: yyyy-mm-dd, yyyy.mm.dd, yyyy/mm/dd
        r'\w+[.,\s]+\d{1,2}(?:st|nd|rd|th)?[.,\s]+\d{4}',  # Dates with month names and commas: March 3rd, 2023
        r'\d{1,2}(?:st|nd|rd|th)?[.,\s]+\w+[.,\s]+\d{4}',  # Dates with month names and commas: 3rd, March 2023
    ]

    # Combine all patterns into a single regex pattern
    combined_pattern = re.compile('|'.join(date_patterns))
    potential_dates = combined_pattern.findall(value)

    extracted_dates = []
    for date_str in potential_dates:
        # Check for ISO-like formats (yyyy-mm-dd, yyyy.mm.dd, yyyy/mm/dd)
        if re.match(r'\d{4}[./-]\d{2}[./-]\d{2}', date_str):
            date = dateparser.parse(date_str, settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'YMD'})
        else:
            # Parse other date strings using DMY order
            date = dateparser.parse(date_str, settings={'PREFER_DAY_OF_MONTH': 'first', 'DATE_ORDER': 'DMY'})

        if date:
            extracted_dates.append(date)

    result = first(extracted_dates, default=None)
    if result is None:
        return
    return result.strftime(output_format)


def string_join(items: list, strip_items: bool = True, strip_result: bool = True):
    if strip_items:
        data = (x.strip() for x in items)
    else:
        data = (x for x in items)
    res = " ".join(data)
    if strip_result:
        res = res.strip()
    return res
