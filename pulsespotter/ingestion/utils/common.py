from typing import List
from more_itertools import first


def generate_batches(lst, n):
    if n <= 0:
        raise ValueError("Batch size must be a positive integer.")
    for i in range(0, len(lst), n):
        yield lst[i:i+n]


def join_strings(strings: str | List[str]):
    if isinstance(strings, str):
        return strings
    return " ".join([x.strip() for x in strings if len(x.strip()) > 0])
