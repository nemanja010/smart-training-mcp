"""
FastAPI web server exposing Intervals.icu MCP tools as HTTP REST endpoints.

Deploy on Render, Railway, or any platform, then import the OpenAPI spec
(/openapi.json) into Dify, n8n, or any AI tool platform.

Auth: pass credentials via headers (preferred) or query params:
  X-API-Key    / ?api_key=...      — your Intervals.icu API key
  X-Athlete-ID / ?athlete_id=...   — your athlete ID (e.g. iXXXXXX)

Or set API_KEY and ATHLETE_ID env vars as defaults for single-user deployments.
"""

import os
from contextlib import asynccontextmanager
from typing import Any, Optional

import uvicorn
from fastapi import Depends, FastAPI, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import intervals_mcp_server.api.client as _client_module
from intervals_mcp_server.tools.activities import (
    get_activities,
    get_activity_details,
    get_activity_intervals,
    get_activity_power_curves,
    get_activity_streams,
    get_activity_messages,
    add_activity_message,
)
from intervals_mcp_server.tools.events import (
    add_or_update_event,
    add_or_update_note,
    batch_create_events,
    batch_delete_events,
    batch_update_events,
    delete_event,
    get_event_by_id,
    get_events,
)
from intervals_mcp_server.tools.fitness import (
    get_athlete_profile,
    get_fitness_metrics,
    update_sport_settings,
)
from intervals_mcp_server.tools.power_curves import get_athlete_power_curves
from intervals_mcp_server.tools.wellness import (
    get_wellness_data,
    update_wellness,
)
from intervals_mcp_server.mcp_instance import mcp as mcp_instance
import intervals_mcp_server.tools as _tools_registry  # noqa: F401 — trigger @mcp.tool() registration


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    if _client_module.httpx_client and not _client_module.httpx_client.is_closed:
        await _client_module.httpx_client.aclose()


app = FastAPI(
    title="Intervals.icu Training API",
    description=(
        "REST API wrapping Intervals.icu tools for use with Dify, n8n, or custom AI apps. "
        "Also serves an MCP SSE endpoint at /mcp for Claude Desktop. "
        "Pass credentials via X-API-Key and X-Athlete-ID headers, or as query params."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the MCP SSE app for Claude Desktop connections.
# Claude config URL: https://your-app.onrender.com/mcp/sse
# Auth: set API_KEY and ATHLETE_ID env vars, or pass as query params on initial connect.
mcp_sse_app = mcp_instance.sse_app()
app.mount("/mcp", mcp_sse_app)


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------

class _Auth:
    def __init__(
        self,
        x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
        x_athlete_id: Optional[str] = Header(None, alias="X-Athlete-ID"),
        api_key: Optional[str] = Query(None, include_in_schema=False),
        athlete_id: Optional[str] = Query(None, include_in_schema=False),
    ):
        self.api_key = x_api_key or api_key
        self.athlete_id = x_athlete_id or athlete_id


def _r(text: str) -> dict[str, str]:
    """Wrap a text result in a JSON envelope."""
    return {"result": text}


@app.get("/health", tags=["Health"], include_in_schema=False)
async def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Request body models
# ---------------------------------------------------------------------------

class CreateEventBody(BaseModel):
    event_name: str
    event_type: str
    scheduled_start: Optional[str] = None
    scheduled_end: Optional[str] = None
    scheduled_start_date: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    location: Optional[str] = None
    moving_time: Optional[int] = None
    distance: Optional[float] = None
    load: Optional[float] = None


class UpdateEventBody(BaseModel):
    event_name: str
    event_type: str
    scheduled_start: Optional[str] = None
    scheduled_end: Optional[str] = None
    scheduled_start_date: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    location: Optional[str] = None
    moving_time: Optional[int] = None
    distance: Optional[float] = None
    load: Optional[float] = None


class UpdateWellnessBody(BaseModel):
    weight: Optional[float] = None
    resting_hr: Optional[int] = None
    avg_sleeping_hr: Optional[int] = None
    hrv_sdnn: Optional[float] = None
    hrv_rmssd: Optional[float] = None
    sp_o2: Optional[float] = None
    systolic: Optional[int] = None
    diastolic: Optional[int] = None
    vo2max: Optional[float] = None
    respiration: Optional[float] = None
    sleep_secs: Optional[int] = None
    sleep_score: Optional[int] = None
    sleep_quality: Optional[int] = None
    body_fat: Optional[float] = None
    blood_glucose: Optional[float] = None
    lactate: Optional[float] = None
    calories: Optional[int] = None
    hydration: Optional[float] = None
    fatigue: Optional[int] = None
    mood: Optional[int] = None
    motivation: Optional[int] = None
    readiness: Optional[int] = None
    stress: Optional[int] = None
    soreness: Optional[int] = None
    injury: Optional[str] = None
    steps: Optional[int] = None
    comments: Optional[str] = None


class UpdateSportSettingsBody(BaseModel):
    threshold_pace: Optional[str] = None
    ftp: Optional[int] = None
    lthr: Optional[int] = None
    max_hr: Optional[int] = None
    pace_units: Optional[str] = None
    pace_zones: Optional[list[float]] = None
    pace_zone_names: Optional[list[str]] = None
    hr_zones: Optional[list[float]] = None
    hr_zone_names: Optional[list[str]] = None
    power_zones: Optional[list[float]] = None
    power_zone_names: Optional[list[str]] = None
    data: Optional[dict[str, Any]] = None


class AddMessageBody(BaseModel):
    content: str


class AddNoteBody(BaseModel):
    note_text: str
    date: str


class BatchCreateEventsBody(BaseModel):
    events: list[dict[str, Any]]


class BatchUpdateEventsBody(BaseModel):
    updates: list[dict[str, Any]]


class BatchDeleteEventsBody(BaseModel):
    event_ids: list[int]


# ---------------------------------------------------------------------------
# Activities
# ---------------------------------------------------------------------------

@app.get("/activities", tags=["Activities"], summary="List recent activities")
async def api_get_activities(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD, defaults to 30 days ago"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD, defaults to today"),
    limit: int = Query(10, description="Max activities to return"),
    include_unnamed: bool = Query(False),
    auth: _Auth = Depends(_Auth),
):
    return _r(await get_activities(
        athlete_id=auth.athlete_id, api_key=auth.api_key,
        start_date=start_date, end_date=end_date,
        limit=limit, include_unnamed=include_unnamed,
    ))


@app.get("/activities/{activity_id}", tags=["Activities"], summary="Get activity details")
async def api_get_activity_details(activity_id: str, auth: _Auth = Depends(_Auth)):
    return _r(await get_activity_details(activity_id=activity_id, api_key=auth.api_key))


@app.get("/activities/{activity_id}/intervals", tags=["Activities"], summary="Get activity intervals")
async def api_get_activity_intervals(activity_id: str, auth: _Auth = Depends(_Auth)):
    return _r(await get_activity_intervals(activity_id=activity_id, api_key=auth.api_key))


@app.get("/activities/{activity_id}/streams", tags=["Activities"], summary="Get activity time-series streams (downsampled)")
async def api_get_activity_streams(
    activity_id: str,
    stream_types: Optional[str] = Query(
        None,
        description="Comma-separated: time,watts,heartrate,cadence,altitude,distance,velocity_smooth",
    ),
    interval_secs: int = Query(5, description="Downsampling window in seconds (default: 5, use 1 for near-raw data)"),
    auth: _Auth = Depends(_Auth),
):
    return _r(await get_activity_streams(
        activity_id=activity_id, api_key=auth.api_key,
        stream_types=stream_types, interval_secs=interval_secs,
    ))


@app.get("/activities/{activity_id}/power-curves", tags=["Activities"], summary="Get activity power curves")
async def api_get_activity_power_curves(activity_id: str, auth: _Auth = Depends(_Auth)):
    return _r(await get_activity_power_curves(activity_id=activity_id, api_key=auth.api_key))


@app.get("/activities/{activity_id}/messages", tags=["Activities"], summary="Get activity messages")
async def api_get_activity_messages(activity_id: str, auth: _Auth = Depends(_Auth)):
    return _r(await get_activity_messages(activity_id=activity_id, api_key=auth.api_key))


@app.post("/activities/{activity_id}/messages", tags=["Activities"], summary="Add a message to an activity")
async def api_add_activity_message(
    activity_id: str, body: AddMessageBody, auth: _Auth = Depends(_Auth),
):
    return _r(await add_activity_message(
        activity_id=activity_id, content=body.content, api_key=auth.api_key,
    ))


# ---------------------------------------------------------------------------
# Fitness & profile
# ---------------------------------------------------------------------------

@app.get("/fitness", tags=["Fitness"], summary="Get CTL / ATL / TSB fitness metrics")
async def api_get_fitness_metrics(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD, defaults to 42 days ago"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD, defaults to today"),
    auth: _Auth = Depends(_Auth),
):
    return _r(await get_fitness_metrics(
        athlete_id=auth.athlete_id, api_key=auth.api_key,
        start_date=start_date, end_date=end_date,
    ))


@app.get("/profile", tags=["Fitness"], summary="Get athlete profile and sport settings")
async def api_get_athlete_profile(auth: _Auth = Depends(_Auth)):
    return _r(await get_athlete_profile(athlete_id=auth.athlete_id, api_key=auth.api_key))


@app.put("/sport-settings/{sport_type}", tags=["Fitness"], summary="Update sport settings (FTP, LTHR, threshold pace)")
async def api_update_sport_settings(
    sport_type: str, body: UpdateSportSettingsBody, auth: _Auth = Depends(_Auth),
):
    return _r(await update_sport_settings(
        sport_type=sport_type,
        athlete_id=auth.athlete_id, api_key=auth.api_key,
        threshold_pace=body.threshold_pace,
        ftp=body.ftp, lthr=body.lthr, max_hr=body.max_hr,
        pace_units=body.pace_units,
        pace_zones=body.pace_zones, pace_zone_names=body.pace_zone_names,
        hr_zones=body.hr_zones, hr_zone_names=body.hr_zone_names,
        power_zones=body.power_zones, power_zone_names=body.power_zone_names,
        data=body.data,
    ))


@app.get("/power-curves", tags=["Fitness"], summary="Get athlete all-time power curves")
async def api_get_athlete_power_curves(
    activity_type: Optional[str] = Query(None, description="e.g. Ride, Run, VirtualRide"),
    durations: Optional[str] = Query(None, description="e.g. '5s,1min,5min,20min'"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    auth: _Auth = Depends(_Auth),
):
    return _r(await get_athlete_power_curves(
        athlete_id=auth.athlete_id, api_key=auth.api_key,
        activity_type=activity_type, durations=durations,
        start_date=start_date, end_date=end_date,
    ))


# ---------------------------------------------------------------------------
# Wellness
# ---------------------------------------------------------------------------

@app.get("/wellness", tags=["Wellness"], summary="Get wellness data (HRV, sleep, weight, mood)")
async def api_get_wellness(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD, defaults to 30 days ago"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD, defaults to today"),
    include_all_fields: bool = Query(False),
    auth: _Auth = Depends(_Auth),
):
    return _r(await get_wellness_data(
        athlete_id=auth.athlete_id, api_key=auth.api_key,
        start_date=start_date, end_date=end_date,
        include_all_fields=include_all_fields,
    ))


@app.put("/wellness/{date}", tags=["Wellness"], summary="Log wellness data for a date (YYYY-MM-DD)")
async def api_update_wellness(
    date: str, body: UpdateWellnessBody, auth: _Auth = Depends(_Auth),
):
    return _r(await update_wellness(
        date=date,
        athlete_id=auth.athlete_id, api_key=auth.api_key,
        weight=body.weight, resting_hr=body.resting_hr,
        avg_sleeping_hr=body.avg_sleeping_hr,
        hrv_sdnn=body.hrv_sdnn, hrv_rmssd=body.hrv_rmssd,
        sp_o2=body.sp_o2, systolic=body.systolic, diastolic=body.diastolic,
        vo2max=body.vo2max, respiration=body.respiration,
        sleep_secs=body.sleep_secs, sleep_score=body.sleep_score,
        sleep_quality=body.sleep_quality, body_fat=body.body_fat,
        blood_glucose=body.blood_glucose, lactate=body.lactate,
        calories=body.calories, hydration=body.hydration,
        fatigue=body.fatigue, mood=body.mood,
        motivation=body.motivation, readiness=body.readiness,
        stress=body.stress, soreness=body.soreness,
        injury=body.injury, steps=body.steps,
        comments=body.comments,
    ))


# ---------------------------------------------------------------------------
# Events / calendar
# ---------------------------------------------------------------------------

@app.get("/events", tags=["Events"], summary="Get calendar events")
async def api_get_events(
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    auth: _Auth = Depends(_Auth),
):
    return _r(await get_events(
        athlete_id=auth.athlete_id, api_key=auth.api_key,
        start_date=start_date, end_date=end_date,
    ))


@app.post("/events", tags=["Events"], summary="Create a planned workout or event on the calendar")
async def api_create_event(body: CreateEventBody, auth: _Auth = Depends(_Auth)):
    return _r(await add_or_update_event(
        event_name=body.event_name, event_type=body.event_type,
        athlete_id=auth.athlete_id, api_key=auth.api_key,
        scheduled_start=body.scheduled_start, scheduled_end=body.scheduled_end,
        scheduled_start_date=body.scheduled_start_date,
        description=body.description, notes=body.notes,
        location=body.location, moving_time=body.moving_time,
        distance=body.distance, load=body.load,
    ))


@app.post("/events/batch", tags=["Events"], summary="Create multiple events in batch")
async def api_batch_create_events(body: BatchCreateEventsBody, auth: _Auth = Depends(_Auth)):
    return _r(await batch_create_events(
        events=body.events, athlete_id=auth.athlete_id, api_key=auth.api_key,
    ))


@app.put("/events/batch-update", tags=["Events"], summary="Update multiple events in batch")
async def api_batch_update_events(body: BatchUpdateEventsBody, auth: _Auth = Depends(_Auth)):
    return _r(await batch_update_events(
        updates=body.updates, athlete_id=auth.athlete_id, api_key=auth.api_key,
    ))


@app.put("/events/{event_id}", tags=["Events"], summary="Update an existing calendar event")
async def api_update_event(
    event_id: int, body: UpdateEventBody, auth: _Auth = Depends(_Auth),
):
    return _r(await add_or_update_event(
        event_name=body.event_name, event_type=body.event_type,
        athlete_id=auth.athlete_id, api_key=auth.api_key,
        event_id=event_id,
        scheduled_start=body.scheduled_start, scheduled_end=body.scheduled_end,
        scheduled_start_date=body.scheduled_start_date,
        description=body.description, notes=body.notes,
        location=body.location, moving_time=body.moving_time,
        distance=body.distance, load=body.load,
    ))


@app.delete("/events/batch-delete", tags=["Events"], summary="Delete multiple events in batch")
async def api_batch_delete_events(body: BatchDeleteEventsBody, auth: _Auth = Depends(_Auth)):
    return _r(await batch_delete_events(
        event_ids=body.event_ids, athlete_id=auth.athlete_id, api_key=auth.api_key,
    ))


@app.delete("/events/{event_id}", tags=["Events"], summary="Delete a calendar event")
async def api_delete_event(event_id: int, auth: _Auth = Depends(_Auth)):
    return _r(await delete_event(
        event_id=event_id, athlete_id=auth.athlete_id, api_key=auth.api_key,
    ))


@app.get("/events/{event_id}", tags=["Events"], summary="Get a specific event")
async def api_get_event(event_id: int, auth: _Auth = Depends(_Auth)):
    return _r(await get_event_by_id(
        event_id=event_id, athlete_id=auth.athlete_id, api_key=auth.api_key,
    ))


@app.post("/notes", tags=["Events"], summary="Add a plain-text note to the training calendar")
async def api_add_note(body: AddNoteBody, auth: _Auth = Depends(_Auth)):
    return _r(await add_or_update_note(
        note_text=body.note_text, date=body.date,
        athlete_id=auth.athlete_id, api_key=auth.api_key,
    ))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    uvicorn.run("intervals_mcp_server.web_server:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
