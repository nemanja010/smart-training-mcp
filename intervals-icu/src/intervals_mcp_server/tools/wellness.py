"""
Wellness-related MCP tools for Intervals.icu.

This module contains tools for reading and writing athlete wellness data.
"""

from typing import Any

from intervals_mcp_server.api.client import make_intervals_request
from intervals_mcp_server.config import get_config
from intervals_mcp_server.utils.formatting import format_wellness_entry
from intervals_mcp_server.utils.validation import resolve_athlete_id, resolve_date_params

# Import mcp instance from shared module for tool registration
from intervals_mcp_server.mcp_instance import mcp  # noqa: F401

config = get_config()


@mcp.tool()
async def get_wellness_data(
    athlete_id: str | None = None,
    api_key: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    include_all_fields: bool = False,
) -> str:
    """Get wellness data for an athlete from Intervals.icu

    Returns training metrics (CTL, ATL), vitals (weight, resting HR, HRV),
    sleep, and subjective scores for the given date range.

    Args:
        athlete_id: The Intervals.icu athlete ID (optional, uses ATHLETE_ID from .env)
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
        start_date: Start date in YYYY-MM-DD format (optional, defaults to 30 days ago)
        end_date: End date in YYYY-MM-DD format (optional, defaults to today)
        include_all_fields: If True, include additional and custom fields (default: False)
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    start_date, end_date = resolve_date_params(start_date, end_date)

    result = await make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}/wellness",
        api_key=api_key,
        params={"oldest": start_date, "newest": end_date},
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error fetching wellness data: {result.get('message')}"

    if not result:
        return f"No wellness data found for athlete {athlete_id_to_use} in the specified date range."

    wellness_summary = "Wellness Data:\n\n"

    if isinstance(result, dict):
        for date_str, data in result.items():
            if isinstance(data, dict) and "date" not in data:
                data["date"] = date_str
            wellness_summary += format_wellness_entry(data, include_all_fields=include_all_fields) + "\n\n"

    elif isinstance(result, list):
        for entry in result:
            if isinstance(entry, dict):
                wellness_summary += format_wellness_entry(entry, include_all_fields=include_all_fields) + "\n\n"

    return wellness_summary


@mcp.tool()
async def update_wellness(
    date: str,
    athlete_id: str | None = None,
    api_key: str | None = None,
    weight: float | None = None,
    resting_hr: int | None = None,
    avg_sleeping_hr: int | None = None,
    hrv_sdnn: float | None = None,
    hrv_rmssd: float | None = None,
    sp_o2: float | None = None,
    systolic: int | None = None,
    diastolic: int | None = None,
    vo2max: float | None = None,
    respiration: float | None = None,
    sleep_secs: int | None = None,
    sleep_score: int | None = None,
    sleep_quality: int | None = None,
    body_fat: float | None = None,
    blood_glucose: float | None = None,
    lactate: float | None = None,
    calories: int | None = None,
    hydration: float | None = None,
    fatigue: int | None = None,
    mood: int | None = None,
    motivation: int | None = None,
    readiness: int | None = None,
    stress: int | None = None,
    soreness: int | None = None,
    injury: str | None = None,
    steps: int | None = None,
    comments: str | None = None,
) -> str:
    """Update (upsert) wellness data for a specific date on Intervals.icu

    Only the fields you provide will be updated — unspecified fields are left unchanged.
    Call this to log morning HRV, weight, sleep, blood pressure, glucose, subjective scores,
    or any other wellness metric from wearables or manual entry.

    Args:
        date: Date in YYYY-MM-DD format
        athlete_id: The Intervals.icu athlete ID (optional, uses ATHLETE_ID from .env)
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
        weight: Body weight in kg (optional)
        resting_hr: Resting heart rate in bpm (optional)
        avg_sleeping_hr: Average overnight heart rate in bpm (optional)
        hrv_sdnn: HRV SDNN in ms (optional)
        hrv_rmssd: HRV RMSSD in ms (optional)
        sp_o2: Blood oxygen saturation in % (optional)
        systolic: Systolic blood pressure in mmHg (optional)
        diastolic: Diastolic blood pressure in mmHg (optional)
        vo2max: Estimated VO2max (optional)
        respiration: Breathing rate in breaths/min (optional)
        sleep_secs: Total sleep in seconds — e.g. 27000 for 7.5h (optional)
        sleep_score: Sleep score 0–100 from wearable device (optional)
        sleep_quality: Subjective sleep quality 1–5 (optional)
        body_fat: Body fat percentage (optional)
        blood_glucose: Blood glucose in mg/dL (optional)
        lactate: Blood lactate in mmol/L (optional)
        calories: Calories consumed in kcal (optional)
        hydration: Hydration/fluid intake indicator (optional)
        fatigue: Subjective fatigue 1–10 (optional)
        mood: Subjective mood 1–5 (optional)
        motivation: Subjective motivation 1–5 (optional)
        readiness: Subjective readiness to train 1–10 (optional)
        stress: Stress level (optional)
        soreness: Muscle soreness (optional)
        injury: Injury status/notes (optional)
        steps: Daily step count (optional)
        comments: Free-text notes (optional)
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    # Build payload with only the provided fields
    data: dict[str, Any] = {"id": date}
    field_map = {
        "weight": weight,
        "restingHR": resting_hr,
        "avgSleepingHR": avg_sleeping_hr,
        "hrvSDNN": hrv_sdnn,
        "hrvRMSSD": hrv_rmssd,
        "spO2": sp_o2,
        "systolic": systolic,
        "diastolic": diastolic,
        "vo2max": vo2max,
        "respiration": respiration,
        "sleepSecs": sleep_secs,
        "sleepScore": sleep_score,
        "sleepQuality": sleep_quality,
        "bodyFat": body_fat,
        "bloodGlucose": blood_glucose,
        "lactate": lactate,
        "calories": calories,
        "hydration": hydration,
        "fatigue": fatigue,
        "mood": mood,
        "motivation": motivation,
        "readiness": readiness,
        "stress": stress,
        "soreness": soreness,
        "injury": injury,
        "steps": steps,
        "comments": comments,
    }
    for api_key_name, value in field_map.items():
        if value is not None:
            data[api_key_name] = value

    if len(data) == 1:  # only "id" key
        return "Error: At least one wellness field must be provided."

    result = await make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}/wellness/{date}",
        api_key=api_key,
        method="PUT",
        data=data,
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error updating wellness data: {result.get('message')}"

    updated_fields = [k for k in data if k != "id"]
    return f"Successfully updated wellness for {date}: {', '.join(updated_fields)}."


@mcp.tool()
async def update_wellness_bulk(
    entries: list[dict[str, Any]],
    athlete_id: str | None = None,
    api_key: str | None = None,
) -> str:
    """Bulk update wellness data for multiple dates on Intervals.icu

    Useful for importing data from a CSV export, wearable device sync, or
    backfilling historical wellness records.

    Each entry must have an "id" field with the date (YYYY-MM-DD) plus any
    wellness fields: weight, restingHR, hrvSDNN, hrvRMSSD, sleepSecs,
    sleepScore, sleepQuality, calories, fatigue, mood, motivation, readiness, steps.

    Args:
        entries: List of wellness dicts, each with "id" (date) and metric fields
        athlete_id: The Intervals.icu athlete ID (optional, uses ATHLETE_ID from .env)
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    if not entries:
        return "Error: entries list is empty."

    for i, entry in enumerate(entries):
        if not isinstance(entry, dict) or "id" not in entry:
            return f"Error: entry at index {i} must be a dict with an 'id' (date) field."

    result = await make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}/wellness-bulk",
        api_key=api_key,
        method="PUT",
        data=entries,
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error bulk-updating wellness data: {result.get('message')}"

    return f"Successfully updated wellness data for {len(entries)} dates."
