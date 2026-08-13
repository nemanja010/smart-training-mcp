# Smart Training

Smart Training is a local AI coaching workspace for running, cycling, strength, hypertrophy, and concurrent training. It provides:

- AI orchestration through `AGENTS.md`
- Coach and Titan agents in `.opencode/agents/`
- Evidence-based skills for endurance, strength, nutrition, and programming
- A local Intervals.icu MCP server with read/write tools for activities, wellness, fitness metrics, power curves, and calendar events
- A private `workspace/` for the athlete's profile, injury history, plans, notes, and exports

Everything runs through Claude Code or OpenCode on the user's computer. There is no hosted application or remote service in this repository.

## Prerequisites

You need Git and Python 3.12 or newer. Verify them before installing:

```bash
git --version
python3 --version
```

### Windows

Install Git from [git-scm.com](https://git-scm.com/download/win) and Python from [python.org](https://www.python.org/downloads/). During Python installation, enable **Add Python to PATH**. Then verify in PowerShell:

```powershell
git --version
python --version
```

### macOS

Install Git and Python with Homebrew:

```bash
brew install git python@3.12
```

If Homebrew is not installed, follow the instructions at [brew.sh](https://brew.sh). Verify:

```bash
git --version
python3.12 --version
```

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y git python3.12 python3.12-venv python3-pip
```

Verify:

```bash
git --version
python3.12 --version
```

### Fedora

```bash
sudo dnf install -y git python3.12 python3-pip
```

Verify:

```bash
git --version
python3.12 --version
```

## Quick Start

### 1. Clone with submodules

```bash
git clone --recurse-submodules https://github.com/nemanja010/smart-training.git
cd smart-training
```

If the repository was cloned without submodules:

```bash
git submodule update --init --recursive
```

### 2. Install

Linux/macOS:

```bash
bash install.sh
```

Windows PowerShell:

```powershell
.\install.ps1
```

The installer links all training skills into `~/.agents/skills/`, asks for the Intervals.icu API key and athlete ID, creates `intervals-icu/.env`, and installs the `intervals-mcp` command. Use `--skip-mcp` or `-SkipMcp` to install only the skills.

### 3. Configure the MCP server manually

If MCP setup was skipped:

```bash
cd intervals-icu
cp .env.example .env
pip install .
```

Edit `.env`:

```text
API_KEY=your_intervals_api_key
ATHLETE_ID=i123456
```

The project already includes MCP configurations for both supported clients:

- Claude Code: `.mcp.json`
- OpenCode: `.opencode/opencode.json`

Restart the client after installing the server. The configuration uses the `API_KEY` and `ATHLETE_ID` environment variables.

## Using It

Open this repository as the project in Claude Code or OpenCode. `AGENTS.md` acts as the orchestrator:

- Coach handles running, cycling, workout design, race preparation, training analysis, and recovery.
- Titan handles strength, hypertrophy, concurrent training, exercise selection, and nutrition timing.

Example prompts:

```text
How was my training this week?
Build me a 5K training week.
Should I lift on my run days?
What is my current CTL, ATL, and TSB?
Plan a threshold workout for Thursday and put it on my calendar.
```

The assistant may read Intervals.icu data freely. It must ask for confirmation before creating, updating, or deleting Intervals.icu data.

## First User Setup

On the first session, start with the athlete's context before asking for a training plan. The assistant should guide the athlete through this sequence:

1. **Confirm the connection:** In OpenCode or Claude Code, run `/mcp` and confirm that `intervals-icu` is connected. If it is not, check the API key, athlete ID, and `intervals-mcp` installation.
2. **Set goals:** Record primary and secondary goals, target races or events, dates, and measurable targets.
3. **Describe training reality:** Record sports, experience, current fitness, weekly frequency, available days, preferred time of day, session duration, and scheduling constraints.
4. **Record resources:** List available equipment, terrain, facilities, devices, and preferred or disliked training styles.
5. **Record health context:** Describe current pain or symptoms, past injuries, movement restrictions, and relevant clinician or health reports. Pain or suspected injury requires professional assessment rather than a prescribed workout.
6. **Save the context:** Put the information in `workspace/profile.md` and `workspace/injury-history.md`. Put medical or clinician documents in `workspace/health-reports/` when appropriate.
7. **Review before planning:** Summarize the saved context, ask the athlete to correct anything inaccurate, and only then build a plan or analyze training.

The athlete can begin with:

```text
I'm new here. Help me set up my training profile, goals, schedule, equipment,
injury history, and relevant health context before we plan anything.
```

## Personal Workspace

The `workspace/` directory is the athlete's personal area. Keep goals, preferences, equipment, injury history, plans, notes, and exports there. It is intended to remain separate from the reusable project files.

Before planning or analyzing training, the agents read:

- `workspace/profile.md`
- `workspace/injury-history.md`
- `workspace/health-reports/`, if present

Use the files in `workspace/` as templates and replace the example content with the athlete's own information.

## Repository Layout

```text
smart-training-mcp/
├── AGENTS.md                       # Main coaching orchestrator
├── .mcp.json                       # Claude Code local MCP config
├── .opencode/
│   ├── opencode.json               # OpenCode local MCP config
│   └── agents/                     # Coach and Titan agents
├── skills/                         # All 10 training skills (vendored + own)
├── intervals-icu/                  # Local Intervals.icu MCP server package
├── scripts/
│   └── sync-upstream.ps1           # Update vendored skills from upstream
├── workspace/                      # Personal training context template
├── UPSTREAMS.md                    # Vendored skill sources + update how-to
├── install.sh                      # Linux/macOS installer
└── install.ps1                     # Windows installer
```

## Updating

```bash
git pull
git submodule update --remote --merge
```

Re-run the installer after skill or configuration changes.

## Vendored skills

Cycling, hypertrophy, strength, and nutrition skills under `skills/` are
vendored from permissively licensed upstream repositories. See
[UPSTREAMS.md](UPSTREAMS.md) for the sources, pinned commits, and how to update
them (`scripts/sync-upstream.ps1`).

## License

- `skills/running-training/` — MIT
- `skills/intervals-icu/` (coaching skill) — see `intervals-icu/`
- `intervals-icu/` (MCP server) — GPL-3.0-only
- Vendored skills (`cycling-training`, `hypertrophy-training`, `schoenfeld-hypertrophy`, `sbs-training`, `rp-training`, `rp-diet`, `program-creation`, `assessment`) — MIT
