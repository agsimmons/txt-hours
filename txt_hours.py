import argparse
from collections import defaultdict
from datetime import timedelta, time
from pathlib import Path
import re


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("hours_file")

    return parser.parse_args()


def hours_minutes(td):
    return f"{td.seconds//3600}:{(td.seconds//60)%60:02}"


def parse_hour_line(hour_line):
    # 5:30 - 6:10 : IF/THEN CMS

    start_time_string = hour_line.split(" - ")[0]
    start_time = time(
        hour=int(start_time_string.split(":")[0]),
        minute=int(start_time_string.split(":")[1]),
    )

    end_time_string = hour_line.split(" - ")[1].split(" : ")[0]
    end_time = time(
        hour=int(end_time_string.split(":")[0]),
        minute=int(end_time_string.split(":")[1]),
    )

    description = hour_line.split(" - ")[1].split(" : ")[1]

    # Test for and correct AM/PM
    if end_time < start_time:
        end_time = time(hour=end_time.hour + 12, minute=end_time.minute)

    elapsed_hours = end_time.hour - start_time.hour
    elapsed_minutes = end_time.minute - start_time.minute

    duration = timedelta(hours=elapsed_hours, minutes=elapsed_minutes)

    return {
        "start_time": start_time,
        "end_time": end_time,
        "duration": duration,
        "description": description,
    }


def main(args):
    # 1. Find locations of ISO 8601 dates
    # 2. Separate file into chunks starting at the date and going to the blank line
    # 3. For each chunk, split each line into start time, and time, and description
    # 4. Determine if start/end times are in AM or PM (assume AM if noon is not crossed)
    # 5. Calculate timedelta between start time and end time
    # 6. Group based on description, and sum timedeltas

    with open(args.hours_file) as f:
        hours_txt_lines = f.read().splitlines()

    data_blocks = []
    structured_data = {}

    for line_num, line in enumerate(hours_txt_lines):
        if re.match(r"^\d{4}-\d{2}-\d{2}$", line):
            structured_data = {
                "date": line,
                "hours": [],
            }
        elif re.match(r"^\d{1,2}:\d{2} - \d{1,2}:\d{2} : .*$", line):
            structured_data["hours"].append(parse_hour_line(line))
        elif re.match(r"^$", line):
            data_blocks.append(structured_data)
        else:
            raise ValueError(f"Formatting error on line {line_num}")
    if structured_data:
        data_blocks.append(structured_data)

    # NOTE: This won't work until I re-do structure
    # # Make sure timeline is consistant
    # for date in data_blocks:

    #     check_hour = None
    #     for hour_entry in date["hours"]:
    #         if check_hour:
    #             print(f"Check hour: {check_hour}")
    #             print(f"Start time: {hour_entry['start_time']}")
    #             if hour_entry["start_time"] != check_hour:
    #                 raise ValueError(
    #                     f"Error in timeline on {date['date']} for hour entry {hour_entry}"
    #                 )

    #         check_hour = hour_entry["end_time"]

    for date in data_blocks:
        merged_hours = defaultdict(timedelta)
        for hour_line in date["hours"]:
            merged_hours[hour_line["description"]] += hour_line["duration"]

        ordered_hours = sorted(
            (description, duration) for description, duration in merged_hours.items()
        )

        print(date["date"])
        for ordered_hour_line in ordered_hours:
            print(f"{hours_minutes(ordered_hour_line[1])} : {ordered_hour_line[0]}")
        print()


def _main():
    args = parse_args()
    main(args)


if __name__ == "__main__":
    _main()
