"""Starter prompt templates for common Intervals.icu coaching workflows."""

from intervals_mcp_server.mcp_instance import mcp


@mcp.prompt()
def set_up_training_profile() -> str:
    """Guide a new athlete through profile and injury-history setup."""
    return (
        "I'm new to Smart Training. Check whether my Intervals.icu connection works, then "
        "help me create my training profile. Ask me one question at a time about my goals, "
        "target events, sports, experience, weekly availability, session preferences, "
        "equipment, and injury history. Summarize everything before saving it to "
        "workspace/profile.md and workspace/injury-history.md. Do not begin personalized "
        "planning until I have reviewed and confirmed the summary."
    )


@mcp.prompt()
def get_training_baseline() -> str:
    """Summarize an athlete's current fitness and training baseline."""
    return (
        "Review my athlete profile, recent activities, fitness metrics, wellness data, and "
        "power or pace curves. Give me a concise baseline covering current fitness, recent "
        "training load, strengths, weaknesses, recovery status, and the three most useful "
        "next steps. Read workspace/profile.md and workspace/injury-history.md first. Do not "
        "modify any Intervals.icu data."
    )


@mcp.prompt()
def explain_training_data() -> str:
    """Explain key Intervals.icu metrics in plain English."""
    return (
        "Explain my current CTL, ATL, TSB, recent training load, zones, and key fitness "
        "metrics in plain English. Identify anything unusual or potentially concerning, "
        "but do not diagnose medical conditions. Do not modify any Intervals.icu data."
    )


@mcp.prompt()
def analyze_last_week() -> str:
    """Analyze the previous seven days of training."""
    return (
        "Analyze my training over the last seven days. Read workspace/profile.md and "
        "workspace/injury-history.md first. Compare planned versus completed workouts, "
        "summarize volume and intensity by sport, assess recovery and fatigue, identify "
        "missed or excessive training, and recommend how next week should be adjusted. Do "
        "not modify any Intervals.icu data."
    )


@mcp.prompt()
def assess_readiness() -> str:
    """Assess whether an athlete is ready for a hard session today."""
    return (
        "Assess whether I should do a hard workout today. Review my recent training, "
        "CTL/ATL/TSB, recent activities, wellness data, sleep, resting HR, HRV if "
        "available, and planned workout. Give me a hard, easy, and rest option and explain "
        "the decision. Do not modify any Intervals.icu data."
    )


@mcp.prompt()
def review_training_load(period: str = "the last six weeks") -> str:
    """Review load progression and recovery across a time period."""
    return (
        f"Review my training load over {period}. Look for rapid changes, excessive intensity, "
        "insufficient recovery, sport imbalance, and signs that my current load is "
        "inappropriate for my goal. Present the findings chronologically and recommend a "
        "sustainable next step. Read workspace/profile.md and workspace/injury-history.md "
        "first. Do not modify any Intervals.icu data."
    )


@mcp.prompt()
def analyze_key_workout(activity: str = "my most recent race or key workout") -> str:
    """Analyze execution of a race or important workout."""
    return (
        f"Analyze {activity} in detail. Examine pacing or power distribution, heart-rate "
        "response, decoupling or cardiac drift where possible, interval consistency, fade, "
        "and execution against the intended workout. Finish with specific lessons and one "
        "or two changes for future sessions. Do not modify any Intervals.icu data."
    )


@mcp.prompt()
def build_training_week(date_range: str = "the next seven days") -> str:
    """Design a training week without writing it to the calendar."""
    return (
        f"Design my training week for {date_range} using my profile, injury history, target "
        "events, recent Intervals.icu training, current fatigue, and calendar commitments. "
        "Include each session's purpose, duration, intensity targets, recovery rationale, "
        "and alternatives if I am not recovered. Do not add anything to my calendar until I "
        "approve the complete week."
    )


@mcp.prompt()
def prepare_for_race(event: str = "my next target event") -> str:
    """Create a race-preparation plan from current data."""
    return (
        f"Build a race-preparation plan for {event}. First inspect my profile, target date, "
        "recent training, current fitness, and calendar. Explain the phases, weekly "
        "priorities, key workouts, taper, and success metrics. Ask any essential questions "
        "before finalizing the plan. Do not write to my calendar without my confirmation."
    )


@mcp.prompt()
def coordinate_strength_and_endurance(date_range: str = "the next seven days") -> str:
    """Coordinate strength training with endurance training."""
    return (
        f"Review my upcoming endurance workouts for {date_range} and design a strength "
        "schedule that complements them. Account for interference, recovery, hard-day "
        "clustering, equipment, session duration, and my injury history. Do not create "
        "calendar events until I approve the schedule."
    )


@mcp.prompt()
def create_calendar_workout(
    date: str,
    workout: str,
    sport: str = "the appropriate sport",
) -> str:
    """Format a workout for the calendar and require confirmation before writing."""
    return (
        f"Design a structured {sport} workout for {date} based on: {workout}. Format it "
        "using Intervals.icu workout-builder syntax. Use one primary metric so it syncs "
        "reliably to my watch. Show me the complete workout, event name, duration, and "
        "targets first. Do not write it until I explicitly confirm."
    )


@mcp.prompt()
def import_wellness_data(date_range: str) -> str:
    """Prepare a wellness-data import with validation and confirmation."""
    return (
        f"Help me backfill my Intervals.icu wellness data for {date_range}. First show me "
        "the fields and values you intend to write, validate dates and units, and ask for "
        "confirmation before saving anything."
    )
