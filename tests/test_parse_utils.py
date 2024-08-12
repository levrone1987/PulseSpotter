import json
import unittest

from config import TESTS_DIR
from pulsespotter.ingestion.utils.parse_functions import parse_date


class TestParseUtils(unittest.TestCase):
    def test_parse_date(self):
        test_cases = json.load(open(TESTS_DIR.joinpath("test_cases/dates.json")))
        for test_case in test_cases:
            value, expected = test_case["value"], test_case["expected"]
            response = parse_date(value)
            assert response == expected, f"{value=}, {response=}, {expected=}"


if __name__ == "__main__":
    unittest.main()
