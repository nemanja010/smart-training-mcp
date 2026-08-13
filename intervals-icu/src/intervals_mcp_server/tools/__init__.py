"""
MCP tools registry for Intervals.icu.

This module imports all available MCP tools to register them with the FastMCP server.
"""

from intervals_mcp_server.tools.activities import (
    add_activity_message,
    delete_activity,
    download_activity_file,
    get_activities,
    get_activity_details,
    get_activity_intervals,
    get_activity_messages,
    get_activity_power_curves,
    get_activity_streams,
    upload_activity,
)
from intervals_mcp_server.tools.custom_items import (
    create_custom_item,
    delete_custom_item,
    get_custom_item_by_id,
    get_custom_items,
    update_custom_item,
)
from intervals_mcp_server.tools.events import (
    add_or_update_event,
    add_or_update_note,
    delete_event,
    delete_events_by_date_range,
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
    update_wellness_bulk,
)

__all__ = [
    # Activities
    "get_activities",
    "get_activity_details",
    "get_activity_intervals",
    "get_activity_streams",
    "get_activity_power_curves",
    "get_activity_messages",
    "add_activity_message",
    "upload_activity",
    "delete_activity",
    "download_activity_file",
    # Events / Calendar
    "get_events",
    "get_event_by_id",
    "add_or_update_event",
    "add_or_update_note",
    "delete_event",
    "delete_events_by_date_range",
    # Wellness
    "get_wellness_data",
    "update_wellness",
    "update_wellness_bulk",
    # Fitness / Load
    "get_fitness_metrics",
    "get_athlete_profile",
    "update_sport_settings",
    # Power Curves
    "get_athlete_power_curves",
    # Custom Items
    "get_custom_items",
    "get_custom_item_by_id",
    "create_custom_item",
    "update_custom_item",
    "delete_custom_item",
]
