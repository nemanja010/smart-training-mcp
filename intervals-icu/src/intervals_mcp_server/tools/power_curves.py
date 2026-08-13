"""
Power curve MCP tools for Intervals.icu.

This module contains tools for retrieving power curve data from the Intervals.icu API.
"""

from typing import Any, Optional
from intervals_mcp_server.api.client import make_intervals_request
from intervals_mcp_server.config import get_config
from intervals_mcp_server.utils.formatting import format_power_curves
from intervals_mcp_server.utils.validation import resolve_athlete_id

# Import mcp instance from shared module for tool registration
from intervals_mcp_server.mcp_instance import mcp  # noqa: F401

config = get_config()

DEFAULT_DURATIONS = "5s, 15s, 30s, 1min, 2min, 5min, 10min, 20min, 60min"


def _build_curves_param(use_current: bool = True, use_previous: bool = False) -> str:
    """Build the curves parameter for the API request."""
    curves = []
    if use_current:
        curves.append("current")
    if use_previous:
        curves.append("previous")
    return ",".join(curves)


def _validate_dates(start_date: Optional[str], end_date: Optional[str]) -> tuple[bool, str]:
    """Validate date format and logical consistency."""
    if start_date and end_date:
        if start_date > end_date:
            return False, "start_date must be before or equal to end_date"
    return True, ""


def _extract_curve_data(
    response: dict[str, Any],
    durations: list[str],
) -> dict[str, Any]:
    """Extract power curve data from API response."""
    output: dict[str, Any] = {}

    if "curves" in response:
        curves_data = response["curves"]
        for period, period_data in curves_data.items():
            output[period] = {}
            if isinstance(period_data, dict):
                for duration in durations:
                    if duration in period_data:
                        output[period][duration] = period_data[duration]
    return output


@mcp.tool()
async def get_athlete_power_curves(
    athlete_id: str | None = None,
    api_key: str | None = None,
    activity_type: str | None = None,
    durations: str | None = None,
    use_current: bool = True,
    use_previous: bool = False,
    indoor: bool | None = None,
    outdoor: bool | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Get athlete all-time power curves from Intervals.icu

    Args:
        athlete_id: The Intervals.icu athlete ID (optional, uses ATHLETE_ID from .env)
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
        activity_type: Filter by activity type (e.g. 'Ride', 'Run', 'VirtualRide')
        durations: Comma-separated durations (default: "5s, 15s, 30s, 1min, 2min, 5min, 10min, 20min, 60min")
        use_current: Include current season data (default: True)
        use_previous: Include previous season data (default: False)
        indoor: Filter for indoor activities (optional)
        outdoor: Filter for outdoor activities (optional)
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    valid_dates, date_error = _validate_dates(start_date, end_date)
    if not valid_dates:
        return f"Error: {date_error}"

    durations_str = durations or DEFAULT_DURATIONS
    durations_list = [d.strip() for d in durations_str.split(",")]
    curves_param = _build_curves_param(use_current, use_previous)

    params: dict[str, Any] = {"curves": curves_param, "durations": durations_str}

    if activity_type:
        params["activity_type"] = activity_type
    if indoor is not None:
        params["indoor"] = indoor
    if outdoor is not None:
        params["outdoor"] = outdoor
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    result = await make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}/power-curves", api_key=api_key, params=params
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error fetching power curves: {result.get('message')}"

    if not result:
        return f"No power curve data found for athlete {athlete_id_to_use}."

    extracted_data = _extract_curve_data(result, durations_list)

    output: dict[str, Any] = {
        "activity_type": activity_type or "all",
        "curves": extracted_data,
    }

    return format_power_curves(output)
