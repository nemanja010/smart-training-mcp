"""
Fitness and athlete profile MCP tools for Intervals.icu.

This module adds tools for daily training load metrics (CTL/ATL/TSB) and
athlete profile/settings that are not covered by other tool modules.
"""

import re

from intervals_mcp_server.api.client import make_intervals_request
from intervals_mcp_server.config import get_config
from intervals_mcp_server.utils.formatting import format_fitness_entry, format_athlete_profile
from intervals_mcp_server.utils.validation import resolve_athlete_id, resolve_date_params

# Import mcp instance from shared module for tool registration
from intervals_mcp_server.mcp_instance import mcp  # noqa: F401

config = get_config()


@mcp.tool()
async def get_fitness_metrics(
    athlete_id: str | None = None,
    api_key: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Get daily training load metrics (CTL, ATL, TSB) for an athlete from Intervals.icu

    CTL (Chronic Training Load) = fitness — your long-term training accumulation.
    ATL (Acute Training Load) = fatigue — your recent training stress.
    TSB (Training Stress Balance) = CTL - ATL — your form/freshness.

    Positive TSB means you are fresh/recovered. Negative means you are building
    fitness but carrying fatigue. A TSB between -10 and +5 is the optimal training
    zone. Below -25 risks overtraining.

    Fetches from the wellness endpoint which contains these fields.

    Args:
        athlete_id: The Intervals.icu athlete ID (optional, uses ATHLETE_ID from .env)
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
        start_date: Start date in YYYY-MM-DD format (optional, defaults to 42 days ago)
        end_date: End date in YYYY-MM-DD format (optional, defaults to today)
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    start_date, end_date = resolve_date_params(start_date, end_date, default_start_days_ago=42)

    result = await make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}/wellness",
        api_key=api_key,
        params={"oldest": start_date, "newest": end_date},
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error fetching fitness metrics: {result.get('message')}"

    if not result:
        return f"No fitness data found for athlete {athlete_id_to_use} in the specified date range."

    output = "Fitness Metrics (CTL / ATL / TSB):\n\n"

    entries = []
    if isinstance(result, dict):
        for date_str, data in result.items():
            if isinstance(data, dict):
                if "id" not in data:
                    data["id"] = date_str
                entries.append(data)
    elif isinstance(result, list):
        entries = [e for e in result if isinstance(e, dict)]

    # Only show entries that have at least CTL or ATL data
    fitness_entries = [e for e in entries if e.get("ctl") is not None or e.get("atl") is not None]

    if not fitness_entries:
        return (
            f"No CTL/ATL data found for athlete {athlete_id_to_use} in the specified date range. "
            "Fitness metrics require at least one logged activity or wellness record with training load."
        )

    for entry in sorted(fitness_entries, key=lambda e: e.get("id", "")):
        output += format_fitness_entry(entry) + "\n\n"

    return output


@mcp.tool()
async def get_athlete_profile(
    athlete_id: str | None = None,
    api_key: str | None = None,
) -> str:
    """Get athlete profile and sport settings from Intervals.icu

    Returns the athlete's name, sport settings (FTP, LTHR, max HR, threshold pace
    for each sport), and power/HR zones.

    Args:
        athlete_id: The Intervals.icu athlete ID (optional, uses ATHLETE_ID from .env)
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    result = await make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}",
        api_key=api_key,
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error fetching athlete profile: {result.get('message')}"

    if not result or not isinstance(result, dict):
        return f"No profile found for athlete {athlete_id_to_use}."

    return format_athlete_profile(result)


def _parse_pace_to_ms(value: str | float | int, pace_units: str) -> float:
    """Convert a pace string to m/s using the sport's pace_units.

    For MINS_KM:     '6:00' = 6:00/km   → 1000 / 360 = 2.7778 m/s
    For MINS_MILE:   '6:00' = 6:00/mi   → 1609.344 / 360 = 4.4704 m/s
    For SECS_100M:   '2:10' = 2:10/100m → 100 / 130 = 0.7692 m/s
    For SECS_500M:   '2:10' = 2:10/500m → 500 / 130 = 3.8462 m/s
    """
    if isinstance(value, (int, float)):
        return float(value)

    match = re.match(r"^(\d+):(\d{2})$", value.strip())
    if not match:
        raise ValueError(
            f"Invalid pace format: '{value}'. Expected 'MM:SS' (e.g. '6:00') or a raw m/s float."
        )
    mins, secs = int(match.group(1)), int(match.group(2))
    total_secs = mins * 60 + secs
    if total_secs <= 0:
        raise ValueError(f"Pace must be positive: '{value}'")

    units = (pace_units or "").upper()
    if units in ("MINS_MILE", "MINS_MI", "MIN_MILE"):
        return 1609.344 / total_secs
    if units in ("SECS_100M",):
        return 100.0 / total_secs
    if units in ("SECS_500M",):
        return 500.0 / total_secs
    # MINS_KM or unknown — default to per-km
    return 1000.0 / total_secs


def _find_sport_setting_id(
    sport_settings: list[dict], sport_type: str
) -> tuple[int | None, str | None]:
    """Find the sport settings ID matching the given sport type.

    Matches if sport_type is a case-insensitive substring of any type in the
    types array (e.g. 'run' matches ['Run', 'VirtualRun', 'TrailRun']).

    Returns (setting_id, matched_types_label) or (None, error_msg).
    """
    sport_lower = sport_type.strip().lower()
    for settings in sport_settings:
        types = settings.get("types", [])
        matched = [t for t in types if sport_lower in t.lower()]
        if matched:
            return settings["id"], "/".join(types)
    available = []
    for settings in sport_settings:
        types = settings.get("types", [])
        if types:
            available.append("/".join(types))
    return None, f"Sport type '{sport_type}' not found. Available: {', '.join(available)}"


@mcp.tool()
async def update_sport_settings(
    sport_type: str,
    athlete_id: str | None = None,
    api_key: str | None = None,
    threshold_pace: str | float | None = None,
    ftp: int | None = None,
    lthr: int | None = None,
    max_hr: int | None = None,
    pace_units: str | None = None,
    pace_zones: list[float] | None = None,
    pace_zone_names: list[str] | None = None,
    hr_zones: list[float] | None = None,
    hr_zone_names: list[str] | None = None,
    power_zones: list[float] | None = None,
    power_zone_names: list[str] | None = None,
    data: dict | None = None,
) -> str:
    """Update sport-specific settings for an athlete on Intervals.icu.

    Updates settings for a specific sport type. Only the fields you provide
    will be updated — all other fields are left unchanged. Zones are
    recalculated automatically.

    Use the named convenience parameters for common fields, or pass `data`
    with a dict of any raw JSON fields from the sport settings object
    (power_zones, hr_zones, warmup_time, cooldown_time, zone names,
    display preferences, etc.). Named params and `data` are merged — if
    the same key appears in both, `data` wins.

    Zone arrays use a FLAT LIST format — a list of upper-bound values
    plus a matching list of names. This is the native Intervals.icu API format.

    Pace zones — list of percentages of threshold pace (Intervals.icu
    computes actual pace ranges from % of threshold speed):
      pace_zones: [81.0, 89.0, 99.0, 106.0, 999.0]
      pace_zone_names: ["Z1 Recovery", "Z2 Endurance", "Z3 Tempo",
                         "Z4 Threshold", "Z5 VO2max"]
    
    HR zones — list of absolute bpm values:
      hr_zones: [129, 143, 159, 169, 185]
      hr_zone_names: ["Z1 Recovery", "Z2 Endurance", "Z3 Tempo",
                       "Z4 Threshold", "Z5 VO2max"]
    
    Power zones — list of percentages of FTP:
      power_zones: [55, 75, 90, 105, 120]
      power_zone_names: ["Z1 Recovery", "Z2 Endurance", "Z3 Tempo",
                          "Z4 Threshold", "Z5 VO2max", "Z6 Anaerobic"]

    Args:
        sport_type: Sport to update — e.g. 'Run', 'Ride', 'Swim' (case-insensitive
                    substring match against Intervals.icu type labels).
        athlete_id: The Intervals.icu athlete ID (optional, uses ATHLETE_ID from .env)
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
        threshold_pace: Threshold pace as 'MM:SS' (e.g. '6:00' = 6:00/km)
                        or raw m/s float.
        ftp: FTP in watts (cycling) or critical power (running/Stryd).
        lthr: Lactate threshold heart rate in bpm.
        max_hr: Maximum heart rate in bpm.
        pace_units: 'MINS_KM', 'MINS_MILE', 'SECS_100M', or 'SECS_500M'.
        pace_zones: List of upper-bound % threshold pace (e.g. [81, 89, 99, 106, 999]).
        pace_zone_names: Matching zone name strings.
        hr_zones: List of upper-bound bpm values (e.g. [129, 143, 159, 169, 185]).
        hr_zone_names: Matching HR zone name strings.
        power_zones: List of upper-bound % FTP (e.g. [55, 75, 90, 105, 120]).
        power_zone_names: Matching power zone name strings.
        data: Dict of any additional/raw sport settings fields to update
              (e.g. {"warmup_time": 600}). Named zone params take precedence
              over zone data in this dict.
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    # Fetch athlete profile to find the sport settings ID and current pace_units
    profile = await make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}",
        api_key=api_key,
    )
    if isinstance(profile, dict) and "error" in profile:
        return f"Error fetching athlete profile: {profile.get('message')}"
    if not isinstance(profile, dict):
        return f"Invalid profile response for athlete {athlete_id_to_use}."

    sport_settings = profile.get("sportSettings", [])
    if not isinstance(sport_settings, list):
        return "No sportSettings found in athlete profile."

    setting_id, label_or_error = _find_sport_setting_id(sport_settings, sport_type)
    if setting_id is None:
        return label_or_error

    # Determine current pace_units for this sport (needed to interpret pace strings)
    current_pace_units = None
    for settings in sport_settings:
        if settings.get("id") == setting_id:
            current_pace_units = settings.get("pace_units", "MINS_KM")
            break

    # Build update payload from named params (pace conversion uses sport's pace_units)
    update_data: dict = {}
    if threshold_pace is not None:
        update_data["threshold_pace"] = _parse_pace_to_ms(threshold_pace, current_pace_units or "MINS_KM")
    if ftp is not None:
        update_data["ftp"] = ftp
    if lthr is not None:
        update_data["lthr"] = lthr
    if max_hr is not None:
        update_data["max_hr"] = max_hr
    if pace_units is not None:
        update_data["pace_units"] = pace_units.upper()
    if pace_zones is not None:
        update_data["pace_zones"] = pace_zones
    if pace_zone_names is not None:
        update_data["pace_zone_names"] = pace_zone_names
    if hr_zones is not None:
        update_data["hr_zones"] = hr_zones
    if hr_zone_names is not None:
        update_data["hr_zone_names"] = hr_zone_names
    if power_zones is not None:
        update_data["power_zones"] = power_zones
    if power_zone_names is not None:
        update_data["power_zone_names"] = power_zone_names
    if data is not None:
        update_data.update(data)

    if not update_data:
        return "No settings provided to update. Specify at least one named param or pass a `data` dict."

    # Update the sport settings
    result = await make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}/sport-settings/{setting_id}?recalcHrZones=true",
        api_key=api_key,
        method="PUT",
        data=update_data,
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error updating {label_or_error} settings: {result.get('message')}"

    # Format the response using the sport's pace_units
    lines = [f"Updated {label_or_error} settings:"]
    for key, value in update_data.items():
        if key == "threshold_pace":
            final_units = update_data.get("pace_units", current_pace_units or "MINS_KM").upper()
            if final_units in ("MINS_MILE", "MINS_MI", "MIN_MILE"):
                secs_per_mile = 1609.344 / value
                mins = int(secs_per_mile // 60)
                secs = int(secs_per_mile % 60)
                lines.append(f"  threshold_pace: {mins}:{secs:02d}/mi ({value:.4f} m/s)")
            elif final_units in ("SECS_100M",):
                secs_per_100m = 100.0 / value
                lines.append(f"  threshold_pace: {secs_per_100m:.1f}s/100m ({value:.4f} m/s)")
            elif final_units in ("SECS_500M",):
                secs_per_500m = 500.0 / value
                mins = int(secs_per_500m // 60)
                secs = int(secs_per_500m % 60)
                lines.append(f"  threshold_pace: {mins}:{secs:02d}/500m ({value:.4f} m/s)")
            else:
                secs_per_km = 1000.0 / value
                mins = int(secs_per_km // 60)
                secs = int(secs_per_km % 60)
                lines.append(f"  threshold_pace: {mins}:{secs:02d}/km ({value:.4f} m/s)")
        else:
            lines.append(f"  {key}: {value}")
    return "\n".join(lines)
