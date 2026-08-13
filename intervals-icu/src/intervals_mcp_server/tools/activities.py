"""
Activity-related MCP tools for Intervals.icu.

This module contains tools for retrieving, uploading, and managing athlete activities.
"""

from datetime import datetime, timedelta
from typing import Any

from intervals_mcp_server.api.client import (
    make_intervals_request,
    make_intervals_download_request,
    make_intervals_upload_request,
)
from intervals_mcp_server.config import get_config
from intervals_mcp_server.utils.formatting import (
    format_activity_message,
    format_activity_summary,
    format_duration,
    format_intervals,
    format_power_curves,
)
from intervals_mcp_server.utils.validation import resolve_athlete_id, resolve_date_params

# Import mcp instance from shared module for tool registration
from intervals_mcp_server.mcp_instance import mcp  # noqa: F401

config = get_config()


def _parse_activities_from_result(result: Any) -> list[dict[str, Any]]:
    """Extract a list of activity dictionaries from the API result."""
    activities: list[dict[str, Any]] = []

    if isinstance(result, list):
        activities = [item for item in result if isinstance(item, dict)]
    elif isinstance(result, dict):
        for _key, value in result.items():
            if isinstance(value, list):
                activities = [item for item in value if isinstance(item, dict)]
                break
        if not activities and any(key in result for key in ["name", "startTime", "distance"]):
            activities = [result]

    return activities


def _filter_named_activities(activities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter out unnamed activities from the list."""
    return [
        activity
        for activity in activities
        if activity.get("name") and activity.get("name") != "Unnamed"
    ]


async def _fetch_more_activities(
    athlete_id: str,
    start_date: str,
    api_key: str | None,
    api_limit: int,
) -> list[dict[str, Any]]:
    """Fetch additional activities from an earlier date range."""
    oldest_date = datetime.fromisoformat(start_date)
    older_start_date = (oldest_date - timedelta(days=60)).strftime("%Y-%m-%d")
    older_end_date = (oldest_date - timedelta(days=1)).strftime("%Y-%m-%d")

    if older_start_date >= older_end_date:
        return []

    more_params = {"oldest": older_start_date, "newest": older_end_date, "limit": api_limit}
    more_result = await make_intervals_request(
        url=f"/athlete/{athlete_id}/activities",
        api_key=api_key,
        params=more_params,
    )

    if isinstance(more_result, list):
        return _filter_named_activities(more_result)
    return []


@mcp.tool()
async def get_activities(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    athlete_id: str | None = None,
    api_key: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 10,
    include_unnamed: bool = False,
) -> str:
    """Get a list of activities for an athlete from Intervals.icu

    Args:
        athlete_id: The Intervals.icu athlete ID (optional, uses ATHLETE_ID from .env)
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
        start_date: Start date in YYYY-MM-DD format (optional, defaults to 30 days ago)
        end_date: End date in YYYY-MM-DD format (optional, defaults to today)
        limit: Maximum number of activities to return (default: 10)
        include_unnamed: Whether to include unnamed activities (default: False)
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    start_date, end_date = resolve_date_params(start_date, end_date)
    api_limit = limit * 3 if not include_unnamed else limit

    params = {"oldest": start_date, "newest": end_date, "limit": api_limit}
    result = await make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}/activities", api_key=api_key, params=params
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error fetching activities: {result.get('message', 'Unknown error')}"

    if not result:
        return f"No activities found for athlete {athlete_id_to_use} in the specified date range."

    activities = _parse_activities_from_result(result)

    if not activities:
        return f"No valid activities found for athlete {athlete_id_to_use} in the specified date range."

    if not include_unnamed:
        activities = _filter_named_activities(activities)
        if len(activities) < limit:
            more_activities = await _fetch_more_activities(
                athlete_id_to_use, start_date, api_key, api_limit
            )
            activities.extend(more_activities)

    activities = activities[:limit]

    if not activities:
        return (
            f"No named activities found for athlete {athlete_id_to_use} in the specified date range. "
            "Try with include_unnamed=True to see all activities."
        )

    activities_summary = "Activities:\n\n"
    for activity in activities:
        if isinstance(activity, dict):
            activities_summary += format_activity_summary(activity) + "\n\n"

    return activities_summary


@mcp.tool()
async def get_activity_details(activity_id: str, api_key: str | None = None) -> str:
    """Get detailed information for a specific activity from Intervals.icu

    Returns summary metrics including Max HR, Max Power, Avg HR, Avg Power, TSS, IF,
    distance, duration, elevation, and time-in-zone breakdowns. The max values here
    are the true peaks — NOT averaged or downsampled.

    Args:
        activity_id: The Intervals.icu activity ID
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
    """
    result = await make_intervals_request(url=f"/activity/{activity_id}", api_key=api_key)

    if isinstance(result, dict) and "error" in result:
        return f"Error fetching activity details: {result.get('message', 'Unknown error')}"

    if not result:
        return f"No details found for activity {activity_id}."

    activity_data = result[0] if isinstance(result, list) and result else result
    if not isinstance(activity_data, dict):
        return f"Invalid activity format for activity {activity_id}."

    detailed_view = format_activity_summary(activity_data)

    if "zones" in activity_data:
        zones = activity_data["zones"]
        detailed_view += "\nPower Zones:\n"
        for zone in zones.get("power", []):
            detailed_view += f"  Zone {zone.get('number')}: {zone.get('secondsInZone')} seconds\n"
        detailed_view += "\nHeart Rate Zones:\n"
        for zone in zones.get("hr", []):
            detailed_view += f"  Zone {zone.get('number')}: {zone.get('secondsInZone')} seconds\n"

    return detailed_view


@mcp.tool()
async def get_activity_intervals(activity_id: str, api_key: str | None = None) -> str:
    """Get interval data for a specific activity from Intervals.icu

    Returns detailed metrics for each interval: power, heart rate, cadence, speed,
    and environmental data, plus grouped intervals. Includes true max HR and max
    power per interval (NOT downsampled). Use this alongside get_activity_streams
    to capture peak values that may be smoothed by stream averaging.

    Args:
        activity_id: The Intervals.icu activity ID
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
    """
    result = await make_intervals_request(
        url=f"/activity/{activity_id}/intervals", api_key=api_key
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error fetching intervals: {result.get('message', 'Unknown error')}"

    if not result:
        return f"No interval data found for activity {activity_id}."

    if not isinstance(result, dict) or not any(
        key in result for key in ["icu_intervals", "icu_groups"]
    ):
        return f"No interval data or unrecognized format for activity {activity_id}."

    return format_intervals(result)


@mcp.tool()
async def get_activity_streams(
    activity_id: str,
    api_key: str | None = None,
    stream_types: str | None = None,
    interval_secs: int = 5,
) -> str:
    """Get time-series stream data for an activity, downsampled to interval_secs resolution.

    Returns arrays of power, heart rate, pace, cadence, altitude, and distance sampled
    every interval_secs seconds — suitable for pacing analysis, cardiac drift, aerobic
    decoupling, and fade detection.

    **IMPORTANT**: Values are averaged per bucket — short peaks may be smoothed.
    For true max/min values, see the Stream Summary section in the output, or use
    get_activity_intervals which returns per-interval max HR and max power.
    Use interval_secs=1 for near-raw data (large output) or higher values for
    compact trend analysis.

    Args:
        activity_id: The Intervals.icu activity ID
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
        stream_types: Comma-separated stream types (default: time,watts,heartrate,cadence,altitude,distance,velocity_smooth)
        interval_secs: Downsampling window in seconds (default: 5, use 1 for near-raw data)
    """
    params = {
        "types": stream_types or "time,watts,heartrate,cadence,altitude,distance,velocity_smooth"
    }

    result = await make_intervals_request(
        url=f"/activity/{activity_id}/streams",
        api_key=api_key,
        params=params,
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error fetching activity streams: {result.get('message', 'Unknown error')}"

    if not result or not isinstance(result, list):
        return f"No stream data found for activity {activity_id}."

    # Parse streams into a dict keyed by type
    raw: dict[str, list] = {}
    for stream in result:
        if not isinstance(stream, dict):
            continue
        stype = stream.get("type", "")
        data = stream.get("data", [])
        if stype and data:
            raw[stype] = data

    if "time" not in raw:
        return f"No time stream found for activity {activity_id}."

    time_data = raw["time"]
    total_duration = int(max(time_data)) if time_data else 0
    n_buckets = (total_duration // interval_secs) + 1

    # Downsample: compute avg, max, and min per interval_secs window
    downsampled: dict[str, list[float | None]] = {}  # avg
    max_per_bucket: dict[str, list[float | None]] = {}
    min_per_bucket: dict[str, list[float | None]] = {}
    # Per-stream overall stats from raw data (before downsampling)
    stream_stats: dict[str, dict[str, float]] = {}

    for stype, data in raw.items():
        if stype == "time":
            continue
        buckets_avg: list[list[float]] = [[] for _ in range(n_buckets)]
        buckets_max: list[list[float]] = [[] for _ in range(n_buckets)]
        buckets_min: list[list[float]] = [[] for _ in range(n_buckets)]
        for i, t in enumerate(time_data):
            if i >= len(data):
                break
            val = data[i]
            if val is not None:
                idx = min(int(t) // interval_secs, n_buckets - 1)
                fval = float(val)
                buckets_avg[idx].append(fval)
                buckets_max[idx].append(fval)
                buckets_min[idx].append(fval)

        downsampled[stype] = [
            sum(b) / len(b) if b else None
            for b in buckets_avg
        ]
        max_per_bucket[stype] = [
            max(b) if b else None
            for b in buckets_max
        ]
        min_per_bucket[stype] = [
            min(b) if b else None
            for b in buckets_min
        ]

        # Overall stream stats from raw data
        raw_vals = [float(v) for v in data if v is not None]
        if raw_vals:
            stream_stats[stype] = {
                "max": max(raw_vals),
                "min": min(raw_vals),
                "avg": sum(raw_vals) / len(raw_vals),
            }

    time_axis = [i * interval_secs for i in range(n_buckets)]

    LABELS: dict[str, str] = {
        "heartrate": "heartrate_bpm",
        "watts": "power_w",
        "cadence": "cadence_rpm",
        "altitude": "altitude_m",
        "distance": "distance_m",
        "velocity_smooth": "velocity_ms",
        "core_temperature": "core_temp_c",
        "skin_temperature": "skin_temp_c",
    }
    # Integer streams vs decimal streams
    INT_STREAMS = {"heartrate", "watts", "cadence", "distance"}

    lines = [
        f"Activity Streams for {activity_id} ({interval_secs}s intervals)",
        f"Duration: {format_duration(total_duration)} | {n_buckets} samples",
        "",
    ]

    # --- Stream Summary (true max/min/avg from raw data) ---
    lines.append("Stream Summary (true max/min/avg from raw data, NOT downsampled):")
    for stype in downsampled:
        label = LABELS.get(stype, stype)
        stats = stream_stats.get(stype)
        if stats:
            if stype in INT_STREAMS:
                lines.append(
                    f"  {label}: max={int(round(stats['max']))}, "
                    f"min={int(round(stats['min']))}, "
                    f"avg={stats['avg']:.1f}"
                )
            else:
                lines.append(
                    f"  {label}: max={stats['max']:.2f}, "
                    f"min={stats['min']:.2f}, "
                    f"avg={stats['avg']:.2f}"
                )
    lines.append("")

    # --- Downsampled arrays (averages per bucket) ---
    lines.append(f"time_s: {time_axis}")
    for stype, data in downsampled.items():
        label = LABELS.get(stype, stype)
        if stype in INT_STREAMS:
            values: list = [int(round(v)) if v is not None else None for v in data]
        else:
            values = [round(v, 2) if v is not None else None for v in data]
        lines.append(f"{label} (avg): {values}")

    return "\n".join(lines)


@mcp.tool()
async def get_activity_power_curves(activity_id: str, api_key: str | None = None) -> str:
    """Get power curve data for a specific activity from Intervals.icu

    Returns the mean maximal power (MMP) curve — best average power at each duration
    within this specific activity, useful for finding peak efforts.

    Args:
        activity_id: The Intervals.icu activity ID
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
    """
    result = await make_intervals_request(
        url=f"/activity/{activity_id}/power-curves", api_key=api_key
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error fetching activity power curves: {result.get('message', 'Unknown error')}"

    if not result:
        return f"No power curve data found for activity {activity_id}."

    output = f"Power Curves for activity {activity_id}:\n\n"

    if isinstance(result, dict):
        for duration, watts in result.items():
            if isinstance(watts, (int, float)):
                output += f"  {duration}: {watts:.0f}W\n"
            elif isinstance(watts, dict):
                w = watts.get("watts") or watts.get("value")
                w_kg = watts.get("wattsPerKg") or watts.get("watts_per_kg")
                if w is not None:
                    line = f"  {duration}: {w:.0f}W"
                    if w_kg is not None:
                        line += f" ({w_kg:.2f} W/kg)"
                    output += line + "\n"
    elif isinstance(result, list):
        for entry in result:
            if isinstance(entry, dict):
                duration = entry.get("duration") or entry.get("secs")
                watts = entry.get("watts") or entry.get("value")
                if duration and watts:
                    output += f"  {duration}s: {watts:.0f}W\n"

    return output


@mcp.tool()
async def upload_activity(
    file_path: str,
    athlete_id: str | None = None,
    api_key: str | None = None,
) -> str:
    """Upload a workout file to Intervals.icu

    Accepts FIT, GPX, TCX and compressed variants (.zip, .gz, .fit.gz, .gpx.gz).
    Duplicate uploads are silently ignored (HTTP 409 is not an error).

    Args:
        file_path: Local path to the activity file
        athlete_id: The Intervals.icu athlete ID (optional, uses ATHLETE_ID from .env)
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    result = await make_intervals_upload_request(
        url=f"/athlete/{athlete_id_to_use}/activities",
        file_path=file_path,
        api_key=api_key,
    )

    if isinstance(result, dict) and result.get("error"):
        status_code = result.get("status_code")
        # 409 = duplicate, not a real error
        if status_code == 409:
            return f"Activity already exists on Intervals.icu (duplicate upload skipped)."
        return f"Error uploading activity: {result.get('message', 'Unknown error')}"

    if isinstance(result, dict) and result.get("id"):
        activity = result
        name = activity.get("name", "Unnamed")
        activity_id = activity.get("id")
        date = activity.get("start_date_local", "")
        return f"Successfully uploaded activity '{name}' (ID: {activity_id}, Date: {date})."

    return f"Activity uploaded successfully."


@mcp.tool()
async def delete_activity(activity_id: str, api_key: str | None = None) -> str:
    """Delete an activity from Intervals.icu

    Args:
        activity_id: The Intervals.icu activity ID to delete
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
    """
    result = await make_intervals_request(
        url=f"/activity/{activity_id}",
        api_key=api_key,
        method="DELETE",
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error deleting activity: {result.get('message', 'Unknown error')}"

    return f"Successfully deleted activity {activity_id}."


@mcp.tool()
async def download_activity_file(
    activity_id: str,
    output_path: str,
    api_key: str | None = None,
    use_intervals_fit: bool = False,
) -> str:
    """Download the original activity file from Intervals.icu and save it locally

    Args:
        activity_id: The Intervals.icu activity ID
        output_path: Local file path where the downloaded file will be saved
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
        use_intervals_fit: If True, download the Intervals-generated FIT file (with added
                           metrics) instead of the original uploaded file (default: False)
    """
    endpoint = (
        f"/activity/{activity_id}/fit-file"
        if use_intervals_fit
        else f"/activity/{activity_id}/file"
    )

    result = await make_intervals_download_request(
        url=endpoint,
        output_path=output_path,
        api_key=api_key,
    )

    if isinstance(result, dict) and result.get("error"):
        return f"Error downloading activity file: {result.get('message', 'Unknown error')}"

    size_kb = result.get("size_bytes", 0) / 1024
    file_type = "Intervals-generated FIT" if use_intervals_fit else "original"
    return f"Downloaded {file_type} file for activity {activity_id} → {output_path} ({size_kb:.1f} KB)"


@mcp.tool()
async def get_activity_messages(activity_id: str, api_key: str | None = None) -> str:
    """Get messages (notes/comments) for a specific activity from Intervals.icu

    Args:
        activity_id: The Intervals.icu activity ID
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
    """
    result = await make_intervals_request(
        url=f"/activity/{activity_id}/messages",
        api_key=api_key,
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error fetching activity messages: {result.get('message', 'Unknown error')}"

    if not result:
        return f"No messages found for activity {activity_id}."

    messages = result if isinstance(result, list) else []
    if not messages:
        return f"No messages found for activity {activity_id}."

    output = f"Messages for activity {activity_id}:\n\n"
    for msg in messages:
        if isinstance(msg, dict):
            output += format_activity_message(msg) + "\n\n"

    return output


@mcp.tool()
async def add_activity_message(
    activity_id: str,
    content: str,
    api_key: str | None = None,
) -> str:
    """Add a message (note/comment) to an activity on Intervals.icu

    Args:
        activity_id: The Intervals.icu activity ID
        content: The message text to add
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
    """
    result = await make_intervals_request(
        url=f"/activity/{activity_id}/messages",
        api_key=api_key,
        method="POST",
        data={"content": content},
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error adding message to activity: {result.get('message', 'Unknown error')}"

    if not result or not isinstance(result, dict):
        return "Error: Unexpected response when adding message."

    msg_id = result.get("id")
    if msg_id is not None:
        return f"Successfully added message (ID: {msg_id}) to activity {activity_id}."
    return f"Message added to activity {activity_id}."
