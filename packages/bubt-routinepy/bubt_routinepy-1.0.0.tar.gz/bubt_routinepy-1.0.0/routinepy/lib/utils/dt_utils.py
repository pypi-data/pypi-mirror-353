from datetime import datetime


def sort_key_datetime(time_range_str):
    start_time_str = time_range_str.split(" to ")[0]
    return datetime.strptime(start_time_str, "%I:%M %p")
