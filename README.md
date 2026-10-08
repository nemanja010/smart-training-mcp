# Smart Training

Smart Training is a local AI coaching workspace for running, cycling, strength, hypertrophy, and concurrent training. It provides:

- AI orchestration through `AGENTS.md`
- Coach and Titan agents in `.opencode/agents/`
- Evidence-based skills for endurance, strength, nutrition, and programming
- A local Intervals.icu MCP server with read/write tools for activities, wellness, fitness metrics, power curves, and calendar events
- An academic literature MCP server (`paper-search`) covering 20+ sources, plus a `paper-research` skill that turns retrieved papers into new skills
- A private `workspace/` for the athlete's profile, injury history, plans, notes, and exports

Everything runs through Claude Code or OpenCode on the user's computer. There is no hosted application or remote service in this repository.

## Prerequisites

You need Git, Python 3.12 or newer, and [uv](https://docs.astral.sh/uv/getting-started/installation/) (for the paper-search MCP server). Verify them before installing:

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

### uv (optional — for the paper-search MCP server)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh     # Linux/macOS
winget install --id=astral-sh.uv -e                 # Windows
```

```bash
uv --version
```

Skip `uv` if you do not want academic literature search.

## Quick Start

### 1. Clone

```bash
git clone https://github.com/nemanja010/smart-training-mcp.git
cd smart-training-mcp
```

This repository is self-contained — nothing outside its folder is required at any point.

### 2. Install

Linux/macOS:

```bash
bash install.sh
```

Windows PowerShell:

```powershell
.\install.ps1
```

The installer links all training skills into `~/.agents/skills/`, asks for the Intervals.icu API key and athlete ID, creates `intervals-icu/.env`, installs the `intervals-mcp` command, verifies `uv`, and writes optional paper-search keys to `~/.config/paper-search-mcp/.env`.

| Flag | Effect |
|---|---|
| `--skip-mcp` / `-SkipMcp` | Install only the skills |
| `--skip-intervals` / `-SkipIntervals` | Set up paper search only |
| `--skip-paper-search` / `-SkipPaperSearch` | Set up Intervals.icu only |

### 3. Configure the MCP servers manually

If Intervals.icu setup was skipped:

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

### 4. Configure paper search manually

Paper search needs no credentials. It runs through `uvx`:

```bash
uvx --from paper-search-mcp --with "mcp<2" paper-search-mcp
```

> [!IMPORTANT]
> **The `mcp<2` pin is required.** The published `paper-search-mcp` release does not constrain the `mcp`
> dependency, and `mcp` 2.x removed `mcp.server.fastmcp`, which the server imports. Without the pin the
> server fails at startup with `ModuleNotFoundError: No module named 'mcp.server.fastmcp'`. Both
> `.mcp.json` and `.opencode/opencode.json` already include the pin.

Optional API keys go in `~/.config/paper-search-mcp/.env`, which the server loads automatically:

```bash
cp paper-search/.env.example ~/.config/paper-search-mcp/.env
```

The only key that changes behaviour rather than rate limits is `PAPER_SEARCH_MCP_UNPAYWALL_EMAIL` — without
it the Unpaywall source and the Unpaywall leg of the open-access fallback chain are disabled. CORE,
Semantic Scholar, and OpenAlex keys are free and remove rate limiting.

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
What does the research say about two-week taper length before a marathon?
Find recent studies on sleep and HRV recovery, and tell me what's actually established.
```

The assistant may read Intervals.icu data freely. It must ask for confirmation before creating, updating, or deleting Intervals.icu data.

## Research and Skill Synthesis

The `paper-research` skill combines the `paper-search` MCP server with a synthesis workflow that turns
retrieved papers into durable skills.

**Retrieval.** The server exposes 57 tools over 20+ sources — arXiv, PubMed, PMC, Europe PMC, bioRxiv,
medRxiv, OpenAlex, Crossref, Semantic Scholar, CORE, OpenAIRE, DOAJ, Zenodo, HAL, SSRN, CiteSeerX,
Unpaywall, and more. It searches, downloads PDFs, extracts full text, and resolves DOIs to legal open-access
copies via a layered fallback chain.

> [!NOTE]
> Some tools the upstream README describes (`get_citing_papers`, `get_referenced_papers`, `extract_sections`)
> are not in the current PyPI release. `skills/paper-research/SKILL.md` documents the verified surface.

```text
Find me research on polarized intensity distribution in trained runners.
```

**Synthesis.** When asked to turn research into a skill, the assistant runs:

```
Scope → Retrieve → Read full text → Extract claims → Grade evidence → Synthesize → Write skill → Verify
```

Claims are graded A–X (meta-analysis through abstract-only) and every prescription in the resulting skill
carries its grade and a resolvable DOI. Drafts land in `workspace/research/` for review before being promoted
into `skills/`. Citations are never fabricated — an unverifiable claim gets cut rather than softened.

Read `skills/paper-research/SKILL.md` for the full workflow, `references/retrieval.md` for source selection
and failure modes, and `references/synthesis.md` for the evidence grading rubric.

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

This repository is usable **standalone** — open `mcp/` directly in any client.

```text
smart-training-mcp/
├── AGENTS.md                       # Main coaching orchestrator
├── GEMINI.md                       # Antigravity rules (kept in sync with AGENTS.md)
├── .mcp.json                       # Claude Code local MCP config
├── .opencode/
│   ├── opencode.json               # OpenCode local MCP config
│   └── agents/                     # Coach and Titan agents
├── .agents/                        # Antigravity project-level customizations
│   ├── skills/                     #   Links to skills/* (gitignored, regenerate)
│   └── plugins/                    #   MCP server definitions (checked in)
│       ├── intervals-icu/
│       └── paper-search/
├── skills/                         # All 11 skills (vendored + own)
├── intervals-icu/                  # Local Intervals.icu MCP server package
├── paper-search/                   # paper-search MCP config (.env.example)
├── scripts/
│   └── sync-upstream.ps1           # Update vendored skills from upstream
├── workspace/                      # Personal training context template
│   └── research/                   # Papers, claim notes, skill drafts
├── UPSTREAMS.md                    # Vendored skill sources + update how-to
├── install.sh                      # Linux/macOS installer
└── install.ps1                     # Windows installer
```

## Client Support

Each client reads customizations from a different place, so the installer writes all of them:

| Client | Skills | MCP servers | Rules |
|---|---|---|---|
| OpenCode | `.opencode/agents/` + linked `skills/` | `.opencode/opencode.json` | `AGENTS.md` |
| Claude Code | linked `skills/` | `.mcp.json` | `AGENTS.md` |
| Antigravity (IDE + CLI) | `.agents/skills/` | `.agents/plugins/*/mcp_config.json` + `agy mcp add` | `AGENTS.md` / `GEMINI.md` |

Antigravity does **not** read `.mcp.json`, `.opencode/opencode.json`, or the global `~/.agents/skills/`.
It discovers everything from `.agents/` inside the workspace root, which is why this repo ships its own
`.agents/` tree. Run the installer to create the `skills/` links and plugin files.

> [!NOTE]
> On Windows the installer creates **directory junctions** in `.agents/skills/` because symlinks need
> Developer Mode or admin. On Linux/macOS it creates normal symlinks. Both resolve identically.

## Updating

```bash
git pull
```

Re-run the installer after skill or configuration changes.

## Vendored skills

Cycling, hypertrophy, strength, and nutrition skills under `skills/` are
vendored from permissively licensed upstream repositories. See
[UPSTREAMS.md](UPSTREAMS.md) for the sources, pinned commits, and how to update
them (`scripts/sync-upstream.ps1`).

## License

- `skills/running-training/` — MIT
- `skills/paper-research/` — MIT
- `skills/intervals-icu/` (coaching skill) — see `intervals-icu/`
- `intervals-icu/` (MCP server) — GPL-3.0-only
- Vendored skills (`cycling-training`, `hypertrophy-training`, `schoenfeld-hypertrophy`, `sbs-training`, `rp-training`, `rp-diet`, `program-creation`, `assessment`) — MIT
- `paper-search-mcp` (MCP server, installed via `uvx`, not vendored) — MIT
