import argparse
from collections import defaultdict, namedtuple
from datetime import timedelta, time, date
import json
from pathlib import Path
import re

import pandas as pd


NOON = time(hour=12)

DayBlock = namedtuple("DayBlock", ["date", "time_entries"])
TimeEntry = namedtuple("TimeEntry", ["task_name", "duration"])


def hours_minutes(obj):
    return f"{obj.seconds//3600}:{(obj.seconds//60)%60:02}"


class TimeDeltaJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, timedelta):
            return hours_minutes(obj)

        return super().default(self, obj)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("hours_file", type=Path)

    return parser.parse_args()


def parse_time_entry(time_entry):
    start_time_string = time_entry.split(" - ")[0]
    start_time = time(
        hour=int(start_time_string.split(":")[0]),
        minute=int(start_time_string.split(":")[1]),
    )

    end_time_string = time_entry.split(" - ")[1].split(" : ")[0]
    end_time = time(
        hour=int(end_time_string.split(":")[0]),
        minute=int(end_time_string.split(":")[1]),
    )

    task_name = time_entry.split(" - ")[1].split(" : ")[1]

    # Test for and correct AM/PM
    if start_time == NOON and end_time == NOON:
        start_time = time(hour=end_time.hour - 12, minute=end_time.minute)
    elif end_time <= start_time:
        end_time = time(hour=end_time.hour + 12, minute=end_time.minute)

    elapsed_hours = end_time.hour - start_time.hour
    elapsed_minutes = end_time.minute - start_time.minute

    duration = timedelta(hours=elapsed_hours, minutes=elapsed_minutes)

    return TimeEntry(
        task_name=task_name,
        duration=duration,
    )


def parse_day_block(day_block):
    lines = day_block.splitlines()

    date = lines[0]
    time_entries = lines[1:]

    day_block = DayBlock(
        date=lines[0],
        time_entries=[parse_time_entry(time_entry) for time_entry in lines[1:]],
    )

    return day_block


def parse_hours_file(path):
    with open(path) as f:
        text = f.read()

    day_blocks = {}

    for day_block in text.split("\n\n"):
        day_block = parse_day_block(day_block)

        day_blocks[day_block.date] = {}
        for time_entry in day_block.time_entries:
            if time_entry.task_name not in day_blocks[day_block.date]:
                day_blocks[day_block.date][time_entry.task_name] = timedelta()

            day_blocks[day_block.date][time_entry.task_name] += time_entry.duration

    return day_blocks


def main():
    args = parse_args()

    parsed_file = parse_hours_file(args.hours_file)
    parsed_file_as_json = json.dumps(parsed_file, cls=TimeDeltaJSONEncoder)

    df = pd.read_json(parsed_file_as_json, orient="index")
    df = df.transpose()

    print(df)


if __name__ == "__main__":
    main()
