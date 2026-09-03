# Intervals.icu MCP Server

Local MCP server and coaching skill for [Intervals.icu](https://intervals.icu). Claude Code and OpenCode can use it to analyze training, read wellness and fitness data, upload activities, and manage planned workouts on the athlete's calendar.

## Requirements

- Python 3.12 or newer
- An Intervals.icu account
- An Intervals.icu API key from Settings -> Developer Settings
- Your athlete ID from the Intervals.icu profile URL

## Install

From the repository root:

```bash
cd intervals-icu
python3.12 -m venv .venv
source .venv/bin/activate
pip install .
cp .env.example .env
```

Windows PowerShell:

```powershell
cd intervals-icu
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install .
Copy-Item .env.example .env
```

Edit `.env`:

```text
API_KEY=your_intervals_api_key
ATHLETE_ID=i123456
```

Verify the installation:

```bash
which intervals-mcp        # Linux / macOS
where intervals-mcp        # Windows PowerShell
```

## Client Configuration

The repository includes ready-to-use local MCP configuration:

- Claude Code: `.mcp.json`
- OpenCode: `.opencode/opencode.json`

Both start the installed `intervals-mcp` command and pass `API_KEY` and `ATHLETE_ID` from the shell environment. The server also loads `intervals-icu/.env` at startup when `python-dotenv` is installed. Restart the client after installation, then use `/mcp` to confirm that `intervals-icu` is connected.

If the command is not found, activate the virtual environment before starting the client or install the package into an environment on your `PATH`. The root `install.sh` / `install.ps1` install without a virtual environment, so `intervals-mcp` is available on your `PATH` directly.

## Available Tools

- Activities: list, inspect, upload, download, delete, messages, intervals, streams, and power curves
- Calendar: list, inspect, create/update, notes, and delete planned events
- Wellness: read and update daily data, including bulk imports
- Fitness: CTL, ATL, TSB, athlete profile, sport settings, and zones
- Power curves: all-time curves with season and indoor/outdoor filters
- Custom items: charts, fields, zones, and dashboards

## Coaching Skill

The Intervals.icu coaching guidance lives at `skills/intervals-icu/SKILL.md` (see the repo root). The root install scripts link it, along with the running, cycling, strength, nutrition, assessment, and programming skills, into `~/.agents/skills/`.

## Starter Prompts

The server exposes guided MCP prompts for common workflows, including:

- `set_up_training_profile` — onboard a new athlete and collect personal context
- `get_training_baseline` — summarize current fitness, load, and recovery
- `analyze_last_week` — compare planned and completed training
- `assess_readiness` — decide between a hard, easy, or rest day
- `review_training_load` — inspect load progression over a selected period
- `analyze_key_workout` — review race or workout execution
- `build_training_week` — design a week without writing to the calendar
- `prepare_for_race` — create a race-preparation outline
- `coordinate_strength_and_endurance` — coordinate concurrent training
- `create_calendar_workout` — format a workout and request confirmation before writing
- `import_wellness_data` — validate a wellness import before saving

Write-oriented prompts explicitly require athlete confirmation before changing Intervals.icu data.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_KEY` | Yes | Intervals.icu developer API key |
| `ATHLETE_ID` | Yes | Athlete identifier such as `i123456` |
| `INTERVALS_API_BASE_URL` | No | API override; defaults to `https://intervals.icu/api/v1` |

## Development

Install the package in editable mode while working on the server:

```bash
pip install -e .
python -m compileall src
```

## License

This module is licensed under the GNU General Public License v3.0 only. See `LICENSE` and `NOTICE` for attribution details.
