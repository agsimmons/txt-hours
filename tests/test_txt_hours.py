from datetime import date, time, timedelta
from pathlib import Path

import txt_hours


def read_hours_text(path):
    with open(path) as f:
        hours_text = f.read()

    return hours_text


BASE_DIR = Path(__file__).parent

VALID_TEXT_PATH = read_hours_text(BASE_DIR / Path("res/valid.txt"))


def test_parse_hours_text_valid():
    hours_data = txt_hours.parse_hours_text(VALID_TEXT_PATH)

    assert hours_data == {
        date(year=2020, month=1, day=1): [
            txt_hours.TimeEntry("Task 1", timedelta(hours=2, minutes=30)),
            txt_hours.TimeEntry("Task 2", timedelta(hours=1, minutes=0)),
            txt_hours.TimeEntry("Task 3", timedelta(hours=4, minutes=30)),
        ],
        date(year=2020, month=1, day=2): [
            txt_hours.TimeEntry("Task 1", timedelta(hours=4, minutes=0)),
            txt_hours.TimeEntry("Task 2", timedelta(hours=2, minutes=30)),
            txt_hours.TimeEntry("Task 1", timedelta(hours=1, minutes=0)),
        ],
        date(year=2020, month=1, day=3): [
            txt_hours.TimeEntry("Task 1", timedelta(hours=12, minutes=0)),
        ],
        date(year=2020, month=1, day=5): [
            txt_hours.TimeEntry("Task 3", timedelta(hours=2, minutes=59)),
            txt_hours.TimeEntry("Task 4", timedelta(hours=0, minutes=1)),
        ],
        date(year=2020, month=1, day=6): [],
        date(year=2020, month=1, day=7): [
            txt_hours.TimeEntry("Task 3", timedelta(hours=12, minutes=0)),
        ],
    }

