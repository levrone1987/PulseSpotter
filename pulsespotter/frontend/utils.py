from datetime import datetime, timedelta

import pandas as pd


def safe_get_article_field(article_data, field):
    value = article_data.get(field) or ""
    if isinstance(value, str):
        return value.strip()
    elif isinstance(value, list):
        return "\n\n".join(group_text_chunks(value))
    return value


def generate_weeks(start_date, end_date):
    mondays = pd.date_range(start_date, end_date, freq="W-MON").strftime("%Y-%m-%d").tolist()
    weeks = []
    for monday in mondays:
        sunday = datetime.strptime(monday, "%Y-%m-%d") + timedelta(days=6)
        sunday = sunday.strftime("%Y-%m-%d")
        weeks.append((monday, sunday))
    return weeks[::-1]


def group_text_chunks(chunks):
    if not chunks:
        return []

    # List to store the grouped chunks
    grouped_chunks = []
    current_group = ""

    # Set of punctuation marks indicating the end of a sentence
    punctuation_set = {'.', '!', '?'}

    for chunk in chunks:
        chunk = chunk.strip()  # Strip leading/trailing whitespace

        if current_group:
            # Check if the last character of the current group is a punctuation mark
            if current_group[-1] in punctuation_set:
                # If it is, finalize the current group and start a new one
                grouped_chunks.append(current_group)
                current_group = chunk
            else:
                # If it's not, add the current chunk to the current group
                current_group += " " + chunk
        else:
            # Initialize the current group with the first chunk
            current_group = chunk

    # Add the final group to the result
    if current_group:
        grouped_chunks.append(current_group)
    return grouped_chunks


def truncate_text_content(text: str, max_len: int):
    punctuation_set = {".", "!", "?"}
    truncated = text[:max_len]
    last_sentence_stop_idx = max((i for i, char in enumerate(text) if char in punctuation_set), default=-1)
    return truncated[:last_sentence_stop_idx + 1]
