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


def _add_strava_activity_id(list_dict: list):
    for d_ in list_dict:
        d_["activity_id"] = d_.pop("id", None)


def _add_athlete_id(list_dict: list):
    for d_ in list_dict:
        d_["athlete_id"] = d_.pop("athlete", {}).get("id", None)


def _clean_segment_efforts(list_dict: list):
    for d_ in list_dict:
        d_["segment_id"] = d_.get("segment", {}).get("id", None)
        d_["segment_distance"] = (
            d_.get("segment", {}).get("distance", 0) / 1000
        )  # Convert to km
        d_["segment_elevation_high"] = d_.get("segment", {}).get("elevation_high", 0)
        d_["segment_elevation_low"] = d_.pop("segment", {}).get("elevation_low", 0)


def _enrich_with_avg_slope(list_dict: list):
    """
    Enriches the list of dictionaries with average slope.
    The average slope is calculated as (elevation_high - elevation_low) / distance.
    """
    for d_ in list_dict:
        if d_["segment_distance"] > 0:
            d_["avg_slope"] = (
                (d_["segment_elevation_high"] - d_["segment_elevation_low"])
                * 0.001
                / d_["segment_distance"]
            )
        else:
            d_["avg_slope"] = 0


def _return_only_top_n_segment_efforts(list_dict: list, n_segments: int = 10):
    """
    Returns only the top N segment efforts based on the 'slope'.
    Otherwise, LLM free tier does not allow this.
    """
    return sorted(list_dict, key=lambda x: x["avg_slope"], reverse=True)[:n_segments]
