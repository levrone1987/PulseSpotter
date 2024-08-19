from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class DateRangeRequest(BaseModel):
    start_date: str
    end_date: str

    @field_validator("start_date", "end_date", mode="before")
    def validate_date_format(cls, value):
        return validate_date(value)


class ArticleSearchRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    site_name: Optional[str] = None
    phrase: Optional[str] = None
    limit: int = 5

    @field_validator("start_date", "end_date", mode="before")
    def validate_date_format(cls, value):
        return validate_date(value)


class SimilaritySearchRequest(BaseModel):
    article_id: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: int = 5
    min_similarity: float = 0.9

    @field_validator("start_date", "end_date", mode="before")
    def validate_date_format(cls, value):
        return validate_date(value)


def validate_date(date_string: str, date_format: str = "%Y-%m-%d") -> str:
    try:
        datetime.strptime(date_string, date_format)
        return date_string
    except ValueError:
        raise ValueError(f"Date '{date_string}' is not in the correct format '{date_format}'")
