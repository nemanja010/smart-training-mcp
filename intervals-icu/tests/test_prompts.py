from intervals_mcp_server.prompts import (
    analyze_last_week,
    build_training_week,
    create_calendar_workout,
    set_up_training_profile,
)
from intervals_mcp_server.mcp_instance import mcp


def test_set_up_training_profile_is_guided_and_safe():
    prompt = set_up_training_profile()

    assert "one question at a time" in prompt
    assert "workspace/profile.md" in prompt
    assert "workspace/injury-history.md" in prompt
    assert "Do not begin personalized planning" in prompt


def test_analyze_last_week_requests_personal_context_and_read_only_analysis():
    prompt = analyze_last_week()

    assert "last seven days" in prompt
    assert "workspace/profile.md" in prompt
    assert "planned versus completed" in prompt
    assert "Do not modify any Intervals.icu data" in prompt


def test_build_training_week_includes_date_range_and_write_confirmation():
    prompt = build_training_week("2026-09-07 to 2026-09-13")

    assert "2026-09-07 to 2026-09-13" in prompt
    assert "Do not add anything to my calendar until I approve" in prompt


def test_create_calendar_workout_requires_workout_and_explicit_confirmation():
    prompt = create_calendar_workout("2026-09-10", "4 x 5 minutes at threshold")

    assert "2026-09-10" in prompt
    assert "4 x 5 minutes at threshold" in prompt
    assert "Do not write it until I explicitly confirm" in prompt


def test_all_starter_prompts_are_registered_with_fastmcp():
    registered = mcp._prompt_manager._prompts

    assert {
        "set_up_training_profile",
        "get_training_baseline",
        "explain_training_data",
        "analyze_last_week",
        "assess_readiness",
        "review_training_load",
        "analyze_key_workout",
        "build_training_week",
        "prepare_for_race",
        "coordinate_strength_and_endurance",
        "create_calendar_workout",
        "import_wellness_data",
    } <= set(registered)
