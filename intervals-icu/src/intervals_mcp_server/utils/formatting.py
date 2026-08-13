"""
Formatting utilities for Intervals.icu MCP Server.

This module provides functions to format data from the Intervals.icu API into readable text.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import math


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable format."""
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    secs = seconds % 60
    if minutes < 60:
        if secs == 0:
            return f"{minutes}m"
        return f"{minutes}m{secs}s"
    hours = minutes // 60
    mins = minutes % 60
    if secs == 0 and mins == 0:
        return f"{hours}h"
    if secs == 0:
        return f"{hours}h{mins}m"
    return f"{hours}h{mins}m{secs}s"


def _format_date(timestamp: Optional[int]) -> str:
    """Format timestamp to human-readable date."""
    if timestamp is None:
        return "N/A"
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
        return "N/A"


def format_activity_summary(activity: Dict[str, Any]) -> str:
    """Format an activity summary for display."""
    output = []

    if "name" in activity:
        output.append(f"Name: {activity['name']}")
    if "type" in activity:
        output.append(f"Type: {activity['type']}")
    if "start_date_local" in activity:
        output.append(f"Date: {activity['start_date_local']}")
    elif "start_time" in activity:
        output.append(f"Date: {_format_date(activity.get('start_time'))}")

    if "moving_time" in activity and activity["moving_time"] is not None:
        output.append(f"Duration: {format_duration(int(activity['moving_time']))}")
    if "distance" in activity and activity["distance"] is not None:
        output.append(f"Distance: {activity['distance'] / 1000:.1f} km")

    if "average_watts" in activity and activity["average_watts"] is not None:
        output.append(f"Avg Power: {activity['average_watts']:.0f}W")
    if "icu_training_load" in activity and activity["icu_training_load"] is not None:
        output.append(f"Training Load: {activity['icu_training_load']:.0f}")
    if "icu_intensity" in activity and activity["icu_intensity"] is not None:
        output.append(f"Intensity Factor: {activity['icu_intensity']:.2f}")
    if "icu_eftp" in activity and activity["icu_eftp"] is not None:
        output.append(f"eFTP: {activity['icu_eftp']}W")

    if "average_heartrate" in activity and activity["average_heartrate"] is not None:
        output.append(f"Avg HR: {activity['average_heartrate']:.0f} bpm")
    if "max_heartrate" in activity and activity["max_heartrate"] is not None:
        output.append(f"Max HR: {activity['max_heartrate']:.0f} bpm")

    if "total_elevation_gain" in activity and activity["total_elevation_gain"] is not None:
        output.append(f"Elevation: {activity['total_elevation_gain']:.0f}m")

    if "id" in activity:
        output.append(f"ID: {activity['id']}")

    return "\n".join(output)


def format_wellness_entry(entry: Dict[str, Any], include_all_fields: bool = False) -> str:
    """Format a wellness entry for display."""
    # Helper: try camelCase first, fall back to snake_case
    def _get(*keys: str):
        for k in keys:
            v = entry.get(k)
            if v is not None:
                return v
        return None

    output = []

    date = entry.get("id") or entry.get("date", "Unknown")
    output.append(f"Date: {date}")

    # Training load metrics
    ctl = entry.get("ctl")
    atl = entry.get("atl")
    if ctl is not None:
        output.append(f"CTL (Fitness): {ctl:.1f}")
    if atl is not None:
        output.append(f"ATL (Fatigue): {atl:.1f}")
    if ctl is not None and atl is not None:
        tsb = ctl - atl
        output.append(f"TSB (Form): {tsb:.1f}")

    # Vitals
    resting_hr = _get("restingHR", "resting_hr")
    if resting_hr is not None:
        output.append(f"Resting HR: {resting_hr} bpm")
    if entry.get("weight") is not None:
        output.append(f"Weight: {float(entry['weight']):.1f} kg")

    hrv_sdnn = _get("hrvSDNN", "hrv_sdnn")
    hrv_rmssd = _get("hrvRMSSD", "hrv_rmssd")
    hrv_generic = _get("hrv")
    if hrv_sdnn is not None:
        output.append(f"HRV (SDNN): {float(hrv_sdnn):.1f} ms")
    if hrv_rmssd is not None:
        output.append(f"HRV (RMSSD): {float(hrv_rmssd):.1f} ms")
    if hrv_generic is not None and hrv_rmssd is None and hrv_sdnn is None:
        output.append(f"HRV: {float(hrv_generic):.1f} ms")

    # Sleep
    sleep_secs = _get("sleepSecs", "sleep_secs")
    if sleep_secs is not None:
        output.append(f"Sleep: {float(sleep_secs) / 3600:.1f}h")
    sleep_score = _get("sleepScore", "sleep_score")
    if sleep_score is not None:
        output.append(f"Sleep Score: {sleep_score}")
    sleep_quality = _get("sleepQuality", "sleep_quality")
    if sleep_quality is not None:
        output.append(f"Sleep Quality: {sleep_quality}/5")

    # Subjective scores
    if entry.get("fatigue") is not None:
        output.append(f"Fatigue: {entry['fatigue']}/10")
    if entry.get("mood") is not None:
        output.append(f"Mood: {entry['mood']}/5")
    if entry.get("motivation") is not None:
        output.append(f"Motivation: {entry['motivation']}/5")
    if entry.get("readiness") is not None:
        output.append(f"Readiness: {entry['readiness']}/10")

    if entry.get("steps") is not None:
        output.append(f"Steps: {entry['steps']}")

    # Calories — API uses "kcalConsumed"
    kcal = _get("kcalConsumed", "calories")
    if kcal is not None:
        output.append(f"Calories: {kcal} kcal")

    # Additional vitals and metrics
    avg_sleeping_hr = _get("avgSleepingHR", "avg_sleeping_hr")
    if avg_sleeping_hr is not None:
        output.append(f"Avg Sleeping HR: {avg_sleeping_hr} bpm")
    sp_o2 = _get("spO2", "spo2", "sp_o2")
    if sp_o2 is not None:
        output.append(f"SpO2: {sp_o2}%")
    systolic = entry.get("systolic")
    diastolic = entry.get("diastolic")
    if systolic is not None and diastolic is not None:
        output.append(f"Blood Pressure: {systolic}/{diastolic}")
    elif systolic is not None:
        output.append(f"Systolic BP: {systolic}")
    vo2max = entry.get("vo2max")
    if vo2max is not None:
        output.append(f"VO2max: {vo2max}")
    blood_glucose = entry.get("bloodGlucose")
    if blood_glucose is not None:
        output.append(f"Blood Glucose: {blood_glucose} mg/dL")
    lactate = entry.get("lactate")
    if lactate is not None:
        output.append(f"Lactate: {lactate} mmol/L")
    stress_val = entry.get("stress")
    if stress_val is not None:
        output.append(f"Stress: {stress_val}")
    hydration_val = entry.get("hydration")
    if hydration_val is not None:
        output.append(f"Hydration: {hydration_val}")
    soreness = entry.get("soreness")
    if soreness is not None:
        output.append(f"Soreness: {soreness}")
    respiration = entry.get("respiration")
    if respiration is not None:
        output.append(f"Respiration: {respiration}")
    body_fat = entry.get("bodyFat")
    if body_fat is not None:
        output.append(f"Body Fat: {body_fat}%")
    baevsky = entry.get("baevskySI")
    if baevsky is not None:
        output.append(f"Baevsky Stress Index: {baevsky}")
    comments = entry.get("comments")
    if comments is not None:
        output.append(f"Comments: {comments}")
    injury = entry.get("injury")
    if injury is not None:
        output.append(f"Injury: {injury}")

    # Training load breakdown
    ctl_load = entry.get("ctlLoad")
    atl_load = entry.get("atlLoad")
    if ctl_load is not None:
        output.append(f"CTL Load Contribution: {float(ctl_load):.1f}")
    if atl_load is not None:
        output.append(f"ATL Load Contribution: {float(atl_load):.1f}")

    # Flags
    if entry.get("locked") is not None:
        output.append(f"Locked: {entry['locked']}")
    temp_weight = entry.get("tempWeight")
    temp_hr = entry.get("tempRestingHR")
    if temp_weight is not None and temp_hr is not None:
        output.append(f"Temp Measurements: weight={temp_weight}, HR={temp_hr}")
    elif temp_weight is not None:
        output.append(f"Temp Weight: {temp_weight}")
    elif temp_hr is not None:
        output.append(f"Temp Resting HR: {temp_hr}")

    # Menstrual phase (female athletes)
    menstrual = entry.get("menstrualPhase")
    if menstrual is not None:
        output.append(f"Menstrual Phase: {menstrual}")

    # Sport info (nested object from activities contributing to this day)
    sport_info = entry.get("sportInfo")
    if isinstance(sport_info, dict):
        si = sport_info
        parts = []
        if si.get("type"):
            parts.append(str(si["type"]))
        if si.get("eFTP") is not None:
            parts.append(f"eFTP={si['eFTP']}W")
        if si.get("wPrime") is not None:
            parts.append(f"w'={si['wPrime']}")
        if si.get("tSport") is not None:
            parts.append(f"TSS={si['tSport']}")
        if parts:
            output.append(f"Sport Info: {', '.join(parts)}")

    if include_all_fields:
        known_keys = {
            "id", "date", "ctl", "atl",
            "restingHR", "resting_hr", "weight",
            "hrv", "hrvSDNN", "hrvRMSSD", "hrv_sdnn", "hrv_rmssd",
            "sleepSecs", "sleep_secs", "sleepScore", "sleep_score",
            "sleepQuality", "sleep_quality",
            "fatigue", "mood", "motivation", "readiness",
            "steps", "calories", "kcalConsumed",
            "avgSleepingHR", "avg_sleeping_hr",
            "spO2", "spo2", "sp_o2",
            "systolic", "diastolic",
            "vo2max",
            "bloodGlucose",
            "lactate",
            "stress",
            "hydration",
            "soreness",
            "respiration",
            "bodyFat",
            "baevskySI",
            "comments",
            "injury",
            "ctlLoad", "atlLoad",
            "locked",
            "tempWeight", "tempRestingHR",
            "menstrualPhase",
            "sportInfo",
            "abdomen", "carbohydrates", "fatTotal", "protein",
        }
        for key, val in entry.items():
            if key not in known_keys and val is not None:
                output.append(f"{key}: {val}")

    return "\n".join(output)


def format_fitness_entry(entry: Dict[str, Any]) -> str:
    """Format a daily fitness/load entry (CTL, ATL, TSB, HRV) for display."""
    def _get(*keys: str):
        for k in keys:
            v = entry.get(k)
            if v is not None:
                return v
        return None

    output = []

    date = entry.get("id") or entry.get("date", "Unknown")
    output.append(f"Date: {date}")

    ctl = entry.get("ctl")
    atl = entry.get("atl")

    if ctl is not None:
        output.append(f"CTL (Fitness): {ctl:.1f}")
    if atl is not None:
        output.append(f"ATL (Fatigue): {atl:.1f}")
    if ctl is not None and atl is not None:
        tsb = ctl - atl
        if tsb > 5:
            form = "Fresh / Recovered"
        elif tsb >= -10:
            form = "Optimal Training Zone"
        elif tsb >= -25:
            form = "Fatigued / Overreaching"
        else:
            form = "Heavily Overreached"
        output.append(f"TSB (Form): {tsb:.1f}  → {form}")

    ramp_rate = _get("rampRate", "ramp_rate")
    if ramp_rate is not None:
        output.append(f"Ramp Rate: {float(ramp_rate):.1f} CTL/week")

    hrv_rmssd = _get("hrvRMSSD", "hrv_rmssd")
    hrv_sdnn = _get("hrvSDNN", "hrv_sdnn")
    hrv_generic = _get("hrv")
    if hrv_rmssd is not None:
        output.append(f"HRV (RMSSD): {float(hrv_rmssd):.1f} ms")
    if hrv_sdnn is not None:
        output.append(f"HRV (SDNN): {float(hrv_sdnn):.1f} ms")
    if hrv_generic is not None and hrv_rmssd is None and hrv_sdnn is None:
        output.append(f"HRV: {float(hrv_generic):.1f} ms")

    return "\n".join(output)


def _format_pace(threshold_pace_ms: float, pace_units: str | None = None) -> str:
    """Convert threshold pace from m/s to human-readable format."""
    if threshold_pace_ms <= 0:
        return f"{threshold_pace_ms}"

    pace_units = (pace_units or "").upper()

    if pace_units in ("MINS_KM", "MIN_KM"):
        secs_per_km = 1000.0 / threshold_pace_ms
        mins = int(secs_per_km // 60)
        secs = int(secs_per_km % 60)
        return f"{mins}:{secs:02d}/km"
    elif pace_units in ("MINS_MILE", "MIN_MILE", "MINS_MI"):
        secs_per_mile = 1609.344 / threshold_pace_ms
        mins = int(secs_per_mile // 60)
        secs = int(secs_per_mile % 60)
        return f"{mins}:{secs:02d}/mi"
    elif pace_units in ("SECS_100M",):
        secs_per_100m = 100.0 / threshold_pace_ms
        return f"{secs_per_100m:.1f}s/100m"
    elif pace_units in ("SECS_500M",):
        secs_per_500m = 500.0 / threshold_pace_ms
        mins = int(secs_per_500m // 60)
        secs = int(secs_per_500m % 60)
        return f"{mins}:{secs:02d}/500m"
    else:
        secs_per_km = 1000.0 / threshold_pace_ms
        mins = int(secs_per_km // 60)
        secs = int(secs_per_km % 60)
        return f"{mins}:{secs:02d}/km"


def format_athlete_profile(profile: Dict[str, Any]) -> str:
    """Format athlete profile data for display."""
    output = []

    if profile.get("name"):
        output.append(f"Name: {profile['name']}")
    if profile.get("id"):
        output.append(f"Athlete ID: {profile['id']}")
    if profile.get("email"):
        output.append(f"Email: {profile['email']}")

    sport_settings = profile.get("sportSettings")
    if isinstance(sport_settings, list):
        for settings in sport_settings:
            if not isinstance(settings, dict):
                continue
            types = settings.get("types", [])
            sport_label = "/".join(types) if types else "Other"
            output.append(f"\n{sport_label}:")

            if settings.get("ftp") is not None:
                output.append(f"  FTP: {settings['ftp']}W")
            if settings.get("lthr") is not None:
                output.append(f"  LTHR: {settings['lthr']} bpm")
            if settings.get("max_hr") is not None:
                output.append(f"  Max HR: {settings['max_hr']} bpm")
            if settings.get("threshold_pace") is not None:
                pace_str = _format_pace(settings["threshold_pace"], settings.get("pace_units"))
                output.append(f"  Threshold Pace: {pace_str}")
            if settings.get("pace_units") is not None:
                output.append(f"  Pace Units: {settings['pace_units']}")

            power_zones = settings.get("power_zones")
            if power_zones:
                zone_names = settings.get("power_zone_names", [])
                output.append("  Power Zones:")
                for i, boundary in enumerate(power_zones):
                    zone_name = zone_names[i] if i < len(zone_names) else f"Z{i + 1}"
                    if i < len(power_zones) - 1:
                        output.append(f"    {zone_name}: up to {boundary}% FTP")
                    else:
                        output.append(f"    {zone_name}: >{power_zones[-2]}% FTP")

            hr_zones = settings.get("hr_zones")
            if hr_zones:
                zone_names = settings.get("hr_zone_names", [])
                output.append("  HR Zones:")
                for i, boundary in enumerate(hr_zones):
                    zone_name = zone_names[i] if i < len(zone_names) else f"Z{i + 1}"
                    output.append(f"    {zone_name}: up to {boundary} bpm")

            pace_zones = settings.get("pace_zones")
            if pace_zones:
                zone_names = settings.get("pace_zone_names", [])
                output.append("  Pace Zones:")
                for i, boundary in enumerate(pace_zones):
                    zone_name = zone_names[i] if i < len(zone_names) else f"Z{i + 1}"
                    output.append(f"    {zone_name}: up to {boundary}% threshold pace")
    elif isinstance(sport_settings, dict):
        for sport_name, settings in sport_settings.items():
            if not isinstance(settings, dict):
                continue
            output.append(f"\n{sport_name}:")
            if settings.get("ftp") is not None:
                output.append(f"  FTP: {settings['ftp']}W")
            if settings.get("lthr") is not None:
                output.append(f"  LTHR: {settings['lthr']} bpm")
            if settings.get("threshold_pace") is not None:
                pace_str = _format_pace(settings["threshold_pace"], settings.get("pace_units"))
                output.append(f"  Threshold Pace: {pace_str}")

    return "\n".join(output)


def format_event_summary(event: Dict[str, Any]) -> str:
    """Format an event summary for display."""
    output = []

    if "name" in event:
        output.append(f"Event: {event['name']}")
    if "id" in event:
        output.append(f"ID: {event['id']}")
    if "type" in event:
        output.append(f"Type: {event['type']}")
    if "start_date_local" in event:
        output.append(f"Date: {event['start_date_local']}")
    elif "scheduled_start" in event:
        output.append(f"Date: {_format_date(event.get('scheduled_start'))}")
    elif "scheduled_start_date" in event:
        output.append(f"Date: {event['scheduled_start_date']}")

    if event.get("description"):
        output.append(f"Description: {event['description']}")
    if event.get("moving_time") is not None:
        output.append(f"Planned Duration: {format_duration(int(event['moving_time']))}")
    if event.get("load") is not None:
        output.append(f"Planned Load: {event['load']}")

    return "\n".join(output)


def format_activity_message(message: Dict[str, Any]) -> str:
    """Format an activity message for display."""
    output = []

    if "timestamp" in message:
        output.append(f"Date: {_format_date(message.get('timestamp'))}")
    if "content" in message:
        output.append(f"Content: {message['content']}")
    elif "note" in message:
        output.append(f"Note: {message['note']}")
    if "id" in message:
        output.append(f"ID: {message['id']}")

    return "\n".join(output)


def format_custom_item_details(item: Dict[str, Any]) -> str:
    """Format custom item details for display."""
    output = []

    if "id" in item:
        output.append(f"ID: {item['id']}")
    if "name" in item:
        output.append(f"Name: {item['name']}")
    if "type" in item:
        output.append(f"Type: {item['type']}")
    if "description" in item:
        output.append(f"Description: {item['description']}")
    if "content" in item and item["content"]:
        output.append(f"Content: {item['content']}")
    if "visibility" in item:
        output.append(f"Visibility: {item['visibility']}")

    return "\n".join(output)


def format_intervals(data: Dict[str, Any]) -> str:
    """Format interval data for display."""
    output = []

    intervals = data.get("icu_intervals", [])
    groups = data.get("icu_groups", [])

    if groups:
        output.append(f"Interval Groups: {len(groups)}")

    if not intervals:
        return "No interval data available."

    output.append(f"Intervals ({len(intervals)} total):\n")

    for i, interval in enumerate(intervals, 1):
        if not isinstance(interval, dict):
            continue
        label = interval.get("label") or interval.get("name") or f"Interval {i}"
        output.append(f"[{label}]")

        if interval.get("start_index") is not None and interval.get("end_index") is not None:
            duration_s = interval["end_index"] - interval["start_index"]
            output.append(f"  Duration: {format_duration(duration_s)}")

        for field, label_str in [
            ("average_watts", "Avg Power"),
            ("max_watts", "Max Power"),
            ("average_heartrate", "Avg HR"),
            ("max_heartrate", "Max HR"),
            ("average_cadence", "Avg Cadence"),
        ]:
            val = interval.get(field)
            if val is not None:
                unit = "W" if "watts" in field else (" bpm" if "heartrate" in field else " rpm")
                output.append(f"  {label_str}: {val:.0f}{unit}")

        if interval.get("intensity") is not None:
            output.append(f"  Intensity: {interval['intensity']:.0f}%")

        output.append("")

    return "\n".join(output)


def format_power_curves(curves: Dict[str, Any]) -> str:
    """Format power curve data for display."""
    output = []

    if "activity_type" in curves:
        output.append(f"Activity Type: {curves['activity_type']}")

    if "curves" in curves:
        for period, data in curves["curves"].items():
            output.append(f"\n{period}:")
            if isinstance(data, dict):
                for duration, watts in sorted(data.items()):
                    if isinstance(watts, (int, float)):
                        output.append(f"  {duration}: {watts:.0f}W")
                    elif isinstance(watts, dict) and "watts" in watts:
                        w = watts["watts"]
                        w_kg = watts.get("watts_per_kg")
                        if w_kg is not None:
                            output.append(f"  {duration}: {w:.0f}W ({w_kg:.2f}W/kg)")
                        else:
                            output.append(f"  {duration}: {w:.0f}W")

    return "\n".join(output)
