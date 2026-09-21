"""
Main server module for Intervals.icu MCP Server.

This module initializes and runs the MCP server.
"""

import logging
import signal
import sys

from intervals_mcp_server.config import get_config
from intervals_mcp_server.mcp_instance import mcp
from intervals_mcp_server.server_setup import setup_transport, start_server
import intervals_mcp_server.prompts as _prompts  # noqa: F401  # register MCP prompts
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


def _signal_handler(signum, frame):
    """Clean exit on termination signals."""
    sys.exit(0)


_win_handler_ref = None


def _register_shutdown_handlers():
    """Register graceful termination handlers for clean process exit on all platforms."""
    global _win_handler_ref
    try:
        signal.signal(signal.SIGINT, _signal_handler)
        signal.signal(signal.SIGTERM, _signal_handler)
        if hasattr(signal, "SIGBREAK"):
            signal.signal(signal.SIGBREAK, _signal_handler)
    except (ValueError, AttributeError):
        pass

    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            _handler_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)

            def _win_ctrl_handler(ctrl_type):
                # Intercept all Windows console termination events and exit 0
                try:
                    ctypes.windll.kernel32.ExitProcess(0)
                except Exception:
                    sys.exit(0)
                return True

            _win_handler_ref = _handler_type(_win_ctrl_handler)
            ctypes.windll.kernel32.SetConsoleCtrlHandler(_win_handler_ref, True)
        except Exception:
            pass


def main():
    """Main entry point for the Intervals.icu MCP server."""
    _register_shutdown_handlers()

    config = get_config()

    if not config.athlete_id:
        logger.warning(
            "ATHLETE_ID is not set. Tools requiring an athlete ID will need the athlete_id parameter."
        )

    transport = setup_transport()
    logger.info("Starting Intervals.icu MCP server")
    try:
        start_server(mcp, transport)
    except (KeyboardInterrupt, SystemExit, BrokenPipeError, EOFError):
        sys.exit(0)
    except BaseException as exc:
        logger.info("Server stopped: %s", exc)
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        sys.exit(0)

