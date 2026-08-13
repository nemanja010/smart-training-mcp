"""
Event-related MCP tools for Intervals.icu.

This module contains tools for managing athlete events through the Intervals.icu API.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Optional

from intervals_mcp_server.api.client import make_intervals_request
from intervals_mcp_server.config import get_config
from intervals_mcp_server.utils.formatting import format_event_summary, format_activity_message
from intervals_mcp_server.utils.types import WorkoutDoc
from intervals_mcp_server.utils.validation import resolve_athlete_id

# Import mcp instance from shared module for tool registration
from intervals_mcp_server.mcp_instance import mcp  # noqa: F401

config = get_config()


def _prepare_event_data(
    event_name: str,
    event_type: str,
    scheduled_start: Optional[str],
    scheduled_end: Optional[str],
    scheduled_start_date: Optional[str],
    notes: Optional[str],
    description: Optional[str],
    location: Optional[str],
) -> dict[str, Any]:
    """Prepare event data for API request using the correct Intervals.icu field names."""
    data: dict[str, Any] = {
        "name": event_name,
        "type": event_type,
        "category": "WORKOUT",
    }

    if scheduled_start:
        data["start_date_local"] = scheduled_start
    elif scheduled_start_date:
        data["start_date_local"] = scheduled_start_date
    else:
        # Intervals.icu requires start_date_local; default to today.
        data["start_date_local"] = datetime.now().strftime("%Y-%m-%d")
    if scheduled_end:
        data["end_date_local"] = scheduled_end

    desc = description or notes
    if desc:
        data["description"] = desc
    if location:
        data["location"] = location

    return data


WORKOUT_SYNTAX_DOC = """
Structured workouts use Intervals.icu's workout builder text syntax in the description field.
Each step starts with '-'. The workout builder parses the description and creates the structured
workout automatically (with visual bars, pace/power targets, syncs to Garmin/Wahoo etc.).

Duration formats: '30s', '10m', '1m30', '90s', '45m'  (m = minutes, NOT meters! No alternative unit for minutes.)
Distance formats: '1.5km', '0.4km', '400mtr', '800meters'  (use mtr/meters for meter-based distances)
  CRITICAL: 'm' means minutes, never meters. Use 'mtr' or 'meters' for meter distances.
  '800m' would be interpreted as 800 minutes! Use '0.8km' or '800mtr' instead.
  Supported distance units: km, mi, mile, miles, mtr, meters, yrd, yards, y
Pace targets:
  - Percentage of threshold pace: '70% Pace', '55-65% Pace'
  - Absolute pace: '6:30/km Pace', '7:00-7:15/mi Pace'
  - Pace zones: 'Z2 Pace', 'Z4 Pace'
  - Pace units: /km, /mi, /100m, /500m, /250m, /400m, /100y
Power targets: '80%', '100-120%', '200w', 'Z3'
HR targets: '70% HR', 'Z2 HR', '100% LTHR'
Cadence: '90rpm', '90-100rpm'
Ramps: 'Ramp 60-80% Pace', 'Ramp 200-300w'
Repeats: 'Nx' on a header line before the repeated steps
Press lap: add 'Press lap' to end step by lap button or distance/duration, whichever comes first
Text prompts: text before duration/power becomes the step label (e.g. '- Recovery 30s 50%')
Headers: 'Warmup', 'Cooldown', 'Main Set', or any label — become step labels
Blank lines separate sections

Example running workout with repeats:
  Warmup
  - 10m 55-65% Pace

  Main Set 4x
  - 400mtr 6:30/km Pace
  - 60s 50% Pace

  Cooldown
  - 0.8km 55-65% Pace

Example cycling workout:
  Warmup
  - 10m Ramp 60-80%

  Main Set 5x
  - 3m 120%
  - 2m 50%

  Cooldown
  - 10m Ramp 80-50%
"""


@mcp.tool()
async def get_events(
    athlete_id: str | None = None,
    api_key: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Get events for an athlete from Intervals.icu

    Args:
        athlete_id: The Intervals.icu athlete ID (optional, will use ATHLETE_ID from .env if not provided)
        api_key: The Intervals.icu API key (optional, will use API_KEY from .env if not provided)
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    url = f"/athlete/{athlete_id_to_use}/events"
    params = {}
    if start_date:
        params["oldest"] = start_date
    if end_date:
        params["newest"] = end_date

    # If no date range specified, default to today through 42 days ahead
    # so the coach can see all upcoming planned workouts
    if not start_date and not end_date:
        params["oldest"] = datetime.now().strftime("%Y-%m-%d")
        params["newest"] = (datetime.now() + timedelta(days=42)).strftime("%Y-%m-%d")

    result = await make_intervals_request(url=url, api_key=api_key, params=params)

    if isinstance(result, dict) and "error" in result:
        return f"Error fetching events: {result.get('message')}"

    if not result:
        return f"No events found for athlete {athlete_id_to_use}."

    output = "Events:\n\n"
    for event in result:
        if isinstance(event, dict):
            output += format_event_summary(event) + "\n\n"
    return output


@mcp.tool()
async def get_event_by_id(
    event_id: int,
    athlete_id: str | None = None,
    api_key: str | None = None,
) -> str:
    """Get detailed information for a specific event from Intervals.icu

    Args:
        event_id: The event ID
        athlete_id: The Intervals.icu athlete ID (optional, will use ATHLETE_ID from .env if not provided)
        api_key: The Intervals.icu API key (optional, will use API_KEY from .env if not provided)
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    result = await make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}/events/{event_id}", api_key=api_key
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error fetching event: {result.get('message')}"

    if not result or not isinstance(result, dict):
        return f"No event found with ID {event_id}."

    return format_event_summary(result)


@mcp.tool()
async def delete_event(
    event_id: int,
    athlete_id: str | None = None,
    api_key: str | None = None,
) -> str:
    """Delete a single event from Intervals.icu

    Args:
        event_id: The event ID to delete
        athlete_id: The Intervals.icu athlete ID (optional, will use ATHLETE_ID from .env if not provided)
        api_key: The Intervals.icu API key (optional, will use API_KEY from .env if not provided)
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    result = await make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}/events/{event_id}",
        api_key=api_key,
        method="DELETE",
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error deleting event: {result.get('message')}"

    return f"Successfully deleted event {event_id}."


@mcp.tool()
async def delete_events_by_date_range(
    athlete_id: str | None = None,
    api_key: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> str:
    """Delete all events for an athlete within a date range from Intervals.icu

    Args:
        athlete_id: The Intervals.icu athlete ID (optional, will use ATHLETE_ID from .env if not provided)
        api_key: The Intervals.icu API key (optional, will use API_KEY from .env if not provided)
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    events_result = await make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}/events",
        api_key=api_key,
        params={"oldest": start_date, "newest": end_date},
    )

    if isinstance(events_result, dict) and "error" in events_result:
        return f"Error fetching events: {events_result.get('message')}"

    if not events_result:
        return f"No events found for athlete {athlete_id_to_use} in the specified date range."

    deleted_count = 0
    for event in events_result:
        if isinstance(event, dict) and "id" in event:
            result = await make_intervals_request(
                url=f"/athlete/{athlete_id_to_use}/events/{event['id']}",
                api_key=api_key,
                method="DELETE",
            )
            if not (isinstance(result, dict) and "error" in result):
                deleted_count += 1

    return f"Successfully deleted {deleted_count} events."


@mcp.tool()
async def add_or_update_event(
    event_name: str,
    event_type: str,
    athlete_id: str | None = None,
    api_key: str | None = None,
    event_id: int | None = None,
    scheduled_start: str | None = None,
    scheduled_end: str | None = None,
    scheduled_start_date: str | None = None,
    notes: str | None = None,
    description: str | None = None,
    location: str | None = None,
    workout_doc: dict[str, Any] | None = None,
    moving_time: int | None = None,
    distance: float | None = None,
    load: float | None = None,
) -> str:
    """Add or update a calendar event / planned workout on Intervals.icu

    IMPORTANT: To create a structured workout that shows up properly in the
    Intervals.icu workout builder (with visual bars, pace/power targets, and
    syncs to Garmin/Wahoo), use the description field with workout builder
    text syntax. The description is parsed by Intervals.icu to generate the
    structured workout. Do NOT use workout_doc directly — it is an internal
    format and will not render correctly in the UI.

    Workout builder text syntax (put in description field):

    - Each step starts with '-'
    - Duration: '30s', '10m', '1m30', '45m' (m = minutes, NOT meters! No alternative unit for minutes.)
    - Distance: '1.5km', '0.4km', '400mtr', '800meters'
      CRITICAL: 'm' means minutes. '800m' = 800 minutes! Use '0.8km' or '800mtr'.
      Units: km, mi, mile, miles, mtr, meters, yrd, yards, y
    - Pace targets:
        Percentage of threshold: '70% Pace', '55-65% Pace'
        Absolute pace: '6:30/km Pace', '7:00-7:15/mi Pace'
        Pace zones: 'Z2 Pace', 'Z4 Pace'
        Pace units: /km, /mi, /100m, /500m, /250m, /400m, /100y
    - Power targets: '80%', '100-120%', '200w', 'Z3'
    - HR targets: '70% HR', 'Z2 HR', '100% LTHR'
    - Cadence: '90rpm', '90-100rpm'
    - Ramps: 'Ramp 60-80% Pace', 'Ramp 200-300w'
    - Repeats: 'Nx' on a header line before the repeated steps
    - Press lap: add 'Press lap' to end step by lap button or distance/duration
    - Text prompts: text before duration/power becomes the step label
    - Section headers: 'Warmup', 'Cooldown', 'Main Set Nx' — become step labels
    - Blank lines between sections

    Example running workout:
      Warmup
      - 10m 55-65% Pace

      Main Set 4x
      - 400mtr 6:30/km Pace
      - 60s 50% Pace

      Cooldown
      - 0.8km 55-65% Pace

    Example cycling workout:
      Warmup
      - 10m Ramp 60-80%

      Main Set 5x
      - 3m 120%
      - 2m 50%

      Cooldown
      - 10m Ramp 80-50%

    Args:
        event_name: The name of the event or workout
        event_type: Activity type — Ride, Run, Swim, Walk, Row, WeightTraining, Yoga
        athlete_id: The Intervals.icu athlete ID (optional, uses ATHLETE_ID from .env)
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
        event_id: Event ID to update (omit to create a new event)
        scheduled_start: ISO 8601 datetime string — MUST include time, e.g. '2026-05-22T10:00:00'
        scheduled_end: ISO 8601 end datetime (optional)
        scheduled_start_date: Date in YYYY-MM-DD format (used if scheduled_start is not provided)
        notes: Short notes for the event (shown as description if description not provided)
        description: Long description or workout notes. For structured workouts, use the
                     workout builder text syntax described above. This is parsed by
                     Intervals.icu to create the visual workout builder.
        location: Location of the event
        workout_doc: DEPRECATED — Internal JSON format, does not render properly in the UI.
                     Use the description field with workout builder text syntax instead.
        moving_time: Planned duration in seconds
        distance: Planned distance in meters
        load: Planned training stress score
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    data = _prepare_event_data(
        event_name,
        event_type,
        scheduled_start,
        scheduled_end,
        scheduled_start_date,
        notes,
        description,
        location,
    )

    if moving_time is not None:
        data["moving_time"] = moving_time
    if distance is not None:
        data["distance"] = distance
    if load is not None:
        data["load"] = load

    if event_id is not None:
        # Updating existing event
        if workout_doc is not None:
            data["workout_doc"] = workout_doc
        result = await make_intervals_request(
            url=f"/athlete/{athlete_id_to_use}/events/{event_id}",
            api_key=api_key,
            data=data,
            method="PUT",
        )
        if isinstance(result, dict) and "error" in result:
            return f"Error updating event: {result.get('message')}"
        return format_event_summary(result) if isinstance(result, dict) else f"Successfully updated event {event_id}."

    # Creating new event
    result = await make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}/events",
        api_key=api_key,
        data=data,
        method="POST",
    )
    if isinstance(result, dict) and "error" in result:
        return f"Error creating event: {result.get('message')}"
    if not isinstance(result, dict) or "id" not in result:
        return "Error: Could not determine new event ID."

    new_id = result["id"]

    # If workout_doc was provided (deprecated path), apply via PUT
    if workout_doc is not None:
        update_data: dict[str, Any] = {"workout_doc": workout_doc}
        if moving_time is not None:
            update_data["moving_time"] = moving_time
        if distance is not None:
            update_data["distance"] = distance
        if load is not None:
            update_data["load"] = load
        update_result = await make_intervals_request(
            url=f"/athlete/{athlete_id_to_use}/events/{new_id}",
            api_key=api_key,
            data=update_data,
            method="PUT",
        )
        if isinstance(update_result, dict) and "error" in update_result:
            return f"Event {new_id} created, but error applying workout: {update_result.get('message')}"

    return f"Successfully created event {new_id}."


@mcp.tool()
async def add_or_update_note(
    note_text: str,
    date: str,
    athlete_id: str | None = None,
    api_key: str | None = None,
) -> str:
    """Add a plain-text note to the training calendar on Intervals.icu

    Args:
        note_text: The note text
        date: The date in YYYY-MM-DD format
        athlete_id: The Intervals.icu athlete ID (optional, uses ATHLETE_ID from .env)
        api_key: The Intervals.icu API key (optional, uses API_KEY from .env)
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    data: dict[str, Any] = {
        "name": note_text,
        "type": "note",
        "start_date_local": date,
    }

    result = await make_intervals_request(
        url=f"/athlete/{athlete_id_to_use}/events",
        api_key=api_key,
        data=data,
        method="POST",
    )

    if isinstance(result, dict) and "error" in result:
        return f"Error creating note: {result.get('message')}"


@mcp.tool()
async def batch_create_events(
    events: list[dict[str, Any]],
    athlete_id: str | None = None,
    api_key: str | None = None,
) -> str:
    """Create multiple planned workouts on the calendar in a single batch.
    
    Args:
        events: A list of event objects. Each object should contain:
                - event_name: Workout name
                - event_type: Ride, Run, Swim, Walk, WeightTraining, Yoga
                - scheduled_start: ISO datetime e.g. '2026-06-01T10:00:00' (optional)
                - scheduled_start_date: Date only e.g. '2026-06-01' (optional)
                - description: Workout builder text syntax (optional)
                - notes: Plain notes (optional)
                - load: Planned TSS (optional)
                - location: Location (optional)
                - scheduled_end: ISO datetime (optional)
        athlete_id: The Intervals.icu athlete ID
        api_key: The Intervals.icu API key
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    results = []
    for i, event_data in enumerate(events):
        try:
            # Extract fields to avoid passing extra junk to add_or_update_event
            res = await add_or_update_event(
                event_name=event_data.get("event_name"),
                event_type=event_data.get("event_type"),
                athlete_id=athlete_id_to_use,
                api_key=api_key,
                scheduled_start=event_data.get("scheduled_start"),
                scheduled_end=event_data.get("scheduled_end"),
                scheduled_start_date=event_data.get("scheduled_start_date"),
                notes=event_data.get("notes"),
                description=event_data.get("description"),
                location=event_data.get("location"),
                load=event_data.get("load"),
            )
            results.append({"index": i, "status": "success", "result": res})
        except Exception as e:
            results.append({"index": i, "status": "error", "message": str(e)})

    return json.dumps(results, indent=2)


@mcp.tool()
async def batch_update_events(
    updates: list[dict[str, Any]],
    athlete_id: str | None = None,
    api_key: str | None = None,
) -> str:
    """Update multiple existing calendar events in a single batch.
    
    Args:
        updates: A list of objects containing:
                 - event_id: The ID of the event to update (required)
                 - any other fields from add_or_update_event to change
        athlete_id: The Intervals.icu athlete ID
        api_key: The Intervals.icu API key
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    results = []
    for i, update_data in enumerate(updates):
        event_id = update_data.get("event_id")
        if event_id is None:
            results.append({"index": i, "status": "error", "message": "Missing event_id"})
            continue
        try:
            res = await add_or_update_event(
                event_id=int(event_id),
                event_name=update_data.get("event_name", ""), 
                event_type=update_data.get("event_type", ""),
                athlete_id=athlete_id_to_use,
                api_key=api_key,
                scheduled_start=update_data.get("scheduled_start"),
                scheduled_end=update_data.get("scheduled_end"),
                scheduled_start_date=update_data.get("scheduled_start_date"),
                notes=update_data.get("notes"),
                description=update_data.get("description"),
                location=update_data.get("location"),
                load=update_data.get("load"),
            )
            results.append({"index": i, "status": "success", "result": res})
        except Exception as e:
            results.append({"index": i, "status": "error", "message": str(e)})

    return json.dumps(results, indent=2)


@mcp.tool()
async def batch_delete_events(
    event_ids: list[int],
    athlete_id: str | None = None,
    api_key: str | None = None,
) -> str:
    """Delete multiple events from the calendar.
    
    Args:
        event_ids: List of event IDs to delete
        athlete_id: The Intervals.icu athlete ID
        api_key: The Intervals.icu API key
    """
    athlete_id_to_use, error_msg = resolve_athlete_id(athlete_id, config.athlete_id)
    if error_msg:
        return error_msg

    results = []
    for i, eid in enumerate(event_ids):
        try:
            res = await delete_event(
                event_id=eid,
                athlete_id=athlete_id_to_use,
                api_key=api_key,
            )
            results.append({"index": i, "event_id": eid, "status": "success", "result": res})
        except Exception as e:
            results.append({"index": i, "event_id": eid, "status": "error", "message": str(e)})

    return json.dumps(results, indent=2)
