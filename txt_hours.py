import argparse
from collections import namedtuple
from datetime import date, datetime, time, timedelta
from pathlib import Path
import re


TimeEntry = namedtuple("TimeEntry", ["description", "duration"])


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("hours_file", type=Path)

    return parser.parse_args()


def parse_time_entry(hour_line):
    start_time_string = hour_line.split(" - ")[0]
    start_time = datetime(
        year=1970,
        month=1,
        day=1,
        hour=int(start_time_string.split(":")[0]),
        minute=int(start_time_string.split(":")[1]),
    )

    end_time_string = hour_line.split(" - ")[1].split(" : ")[0]
    end_time = datetime(
        year=1970,
        month=1,
        day=1,
        hour=int(end_time_string.split(":")[0]),
        minute=int(end_time_string.split(":")[1]),
    )

    # 12h -> 24h if needed
    if end_time <= start_time:
        end_time += timedelta(hours=12)

    description = hour_line.split(" - ")[1].split(" : ")[1]

    elapsed_minutes = (end_time.timestamp() - start_time.timestamp()) // 60
    duration = timedelta(minutes=elapsed_minutes)

    return TimeEntry(description, duration)


def parse_hours_text(hours_text):
    """Convers hours_text to a format that can be processed"""

    hours_data = {}

    date_obj = None
    date_time_entries = []
    for line_num, line in enumerate(hours_text.splitlines(), 1):
        if re.match(r"^\d{4}-\d{2}-\d{2}$", line):
            date_obj = datetime.strptime(line, r"%Y-%m-%d").date()
        elif re.match(r"^\d{1,2}:\d{2} - \d{1,2}:\d{2} : .*$", line):
            try:
                date_time_entries.append(parse_time_entry(line))
            except Exception:
                raise Exception(f"Could not parse line {line_num}")
        elif re.match(r"^$", line):
            if date_obj in hours_data:
                raise Exception(
                    f"Duplicate date in text: {date_obj.strftime(r'%Y-%m-%d')}"
                )

            hours_data[date_obj] = date_time_entries
            date_obj = None
            date_time_entries = []
        else:
            raise Exception(f"Could not parse line {line_num}")

    if date_obj:
        if date_obj in hours_data:
            raise Exception(f"Duplicate date in text: {date_obj.strftime(r'%Y-%m-%d')}")

        hours_data[date_obj] = date_time_entries
        date_obj = None
        date_time_entries = []

    return hours_data


def main(args):
    with open(args.hours_file) as f:
        hours_text = f.read()

    hours_data = parse_hours_text(hours_text)


if __name__ == "__main__":
    args = parse_args()
    main(args)
