from datetime import datetime, timedelta

import pandas as pd


def safe_get_article_field(article_data, field):
    value = article_data.get(field) or ""
    if isinstance(value, str):
        return value.strip()
    elif isinstance(value, list):
        return "\n".join(item.strip() for item in value)
    return value


def generate_weeks(start_date, end_date):
    mondays = pd.date_range(start_date, end_date, freq="W-MON").strftime("%Y-%m-%d").tolist()
    weeks = []
    for monday in mondays:
        sunday = datetime.strptime(monday, "%Y-%m-%d") + timedelta(days=6)
        sunday = sunday.strftime("%Y-%m-%d")
        weeks.append((monday, sunday))
    return weeks[::-1]
