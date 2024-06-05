import re

import dateparser
from more_itertools import first
from scrapy import Selector


def parse_date(value: str, output_format: str = "%Y-%m-%d"):
    # Regular expression to find potential date patterns
    date_patterns = [
        r'\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b', # Dates with different delimiters: dd-mm-yyyy, mm-dd-yyyy, dd.mm.yyyy, dd/mm/yyyy
        r'\b\d{4}[./-]\d{2}[./-]\d{2}\b',  # ISO-like dates: yyyy-mm-dd, yyyy.mm.dd, yyyy/mm/dd
        r'\b\w+[.,\s]+\d{1,2}(?:st|nd|rd|th)?[.,\s]+\d{4}\b',  # Dates with month names and commas: March 3rd, 2023
        r'\b\d{1,2}(?:st|nd|rd|th)?[.,\s]+\w+[.,\s]+\d{4}\b',  # Dates with month names and commas: 3rd, March 2023
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


def parse_website(page_source: str, extract_patterns: dict) -> dict | None:

    sel = Selector(text=page_source)
    response_fields = ["title", "description", "raw_date", "parsed_date", "paragraphs"]
    response = {field: None for field in response_fields}

    title_pattern = extract_patterns.get("title")
    if title_pattern:
        title = sel.xpath(title_pattern).get()
        if title:
            response["title"] = title.strip()

    description_pattern = extract_patterns.get("description")
    if description_pattern:
        description = sel.xpath(description_pattern).get()
        if description:
            response["description"] = description.strip()

    date_pattern = extract_patterns.get("date")
    if date_pattern:
        raw_date = sel.xpath(date_pattern).get()
        if raw_date:
            raw_date = raw_date.strip()
            parsed_date = parse_date(raw_date, output_format="%Y-%m-%d")
            response["raw_date"] = raw_date
            response["parsed_date"] = parsed_date

    paragraphs_pattern = extract_patterns.get("paragraphs")
    if paragraphs_pattern:
        paragraphs = sel.xpath(paragraphs_pattern).getall()
        if paragraphs:
            response["paragraphs"] = paragraphs
    return response
