import time

from datetime import datetime


def _convert_speed_to_kmh(list_dict: list):
    for d_ in list_dict:
        if d_["average_speed"]:
            d_["average_speed"] = d_["average_speed"] * 3.6
        if d_["max_speed"]:
            d_["max_speed"] = d_["max_speed"] * 3.6


def _convert_moving_time_to_str(list_dict: list):
    for d_ in list_dict:
        moving_time = d_["moving_time"]
        n_hours = moving_time // 3600
        remaining_seconds = moving_time % 3600
        n_minutes = remaining_seconds // 60
        d_["moving_time"] = f"{n_hours}:{n_minutes}"


def _convert_distance_to_km(list_dict: list):
    for d_ in list_dict:
        d_["distance"] = d_["distance"] / 1000


def _convert_str_date_to_timestamp(date_str: str) -> int:
    return time.mktime(datetime.strptime(date_str, "%Y-%m-%d").timetuple())
