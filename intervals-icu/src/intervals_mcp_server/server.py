"""
Main server module for Intervals.icu MCP Server.

This module initializes and runs the MCP server.
"""

import logging

from intervals_mcp_server.config import get_config
from intervals_mcp_server.mcp_instance import mcp
from intervals_mcp_server.server_setup import setup_transport, start_server
from intervals_mcp_server.tools import (
    # Activities
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
    # Events / Calendar
    add_or_update_event,
    add_or_update_note,
    delete_event,
    delete_events_by_date_range,
    get_event_by_id,
    get_events,
    # Wellness
    get_wellness_data,
    update_wellness,
    update_wellness_bulk,
    # Fitness / Load
    get_athlete_profile,
    get_fitness_metrics,
    # Power Curves
    get_athlete_power_curves,
    # Custom Items
    create_custom_item,
    delete_custom_item,
    get_custom_item_by_id,
    get_custom_items,
    update_custom_item,
)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("intervals_icu_mcp_server")


def main():
    """Main entry point for the Intervals.icu MCP server."""
    config = get_config()

    if not config.athlete_id:
        logger.warning(
            "ATHLETE_ID is not set. Tools requiring an athlete ID will need the athlete_id parameter."
        )

    transport = setup_transport()
    logger.info("Starting Intervals.icu MCP server")
    start_server(mcp, transport)


if __name__ == "__main__":
    main()
