# Your Training Workspace

This folder is yours. Put your training plans, notes, exported data, and anything else here. It's gitignored — your files won't conflict when you `git pull` to update Smart Training.

## What to put here

- Training plans you've built with the AI coach
- Exported activities from Intervals.icu
- Personal notes, goals, race calendars
- Progress logs and training journals
- Anything else related to your training

## Your Training Profile — `profile.md`

**This is the single most important file you can create.** Create `workspace/profile.md` with your training context — agents read this to personalize every plan, workout, and recommendation.

Without it, agents have to ask you the same questions every time. With it, they jump straight into coaching.

### What to include

```markdown
# My Training Profile

## Goals
- [Primary goal, e.g., "Sub-25:00 5K by September 2026"]
- [Secondary goal, e.g., "Build general strength without hurting running"]

## Training Preferences
- **Frequency:** [e.g., "3-4 runs/week + 2 strength sessions"]
- **Time of day:** [e.g., "Late evenings only — no morning workouts"]
- **Session length:** [e.g., "Prefer ~30min, max 60min"]
- **Style:** [e.g., "Kettlebell complexes, minimal equipment, no gym"]
- **Constraints:** [e.g., "One workout per day — never double up"]

## Equipment
- [e.g., "20kg kettlebell"]
- [e.g., "2× adjustable dumbbells (max 10kg each)"]
- [e.g., "Pull-up bar, resistance bands"]

## Past Experience
- [e.g., "Ran a half marathon in 2024 (1:55)"]
- [e.g., "Used to do single-KB ABC workouts — liked them"]
- [e.g., "No structured strength training history"]

## Target Races / Events
| Date | Event | Goal |
|------|-------|------|
| Sep 10, 2026 | 5K time trial | 25:00 |
```

### How to update it

Just edit the file. Agents re-read it on every session. As your goals shift, your equipment changes, or your preferences evolve — keep the file current.

### Why it matters

Agents use this to:
- **Pick the right training split** — full body vs upper/lower depends on your frequency
- **Select appropriate exercises** — they won't prescribe barbell back squats if you only have a kettlebell
- **Schedule around your life** — they'll avoid morning slots if you train evenings, respect your session length limits
- **Phase strength around race dates** — periodization that protects your A-race

## Injury History — `injury-history.md`

**Create this if you have any past injuries, current niggles, or movement restrictions.** Coach and Titan read this before every workout analysis and every plan — it's what keeps a training plan from re-aggravating something. Titan in particular checks it before prescribing any exercise.

### What to include

```markdown
# Injury History

## Current
- [e.g., "Left Achilles tightness — started Jan 2026, worse after speed work"]

## Past
- [e.g., "Right knee patellar tendinopathy, 2024 — resolved with eccentric loading, avoid high-volume downhill running"]
- [e.g., "Lower back strain from deadlifting, 2023 — cleared by PT, comfortable with moderate loads now"]

## Movement restrictions / things to avoid
- [e.g., "No deep squats below 90° — surgeon's advice post-ACL, 2022"]
```

Update it as things change — resolved issues, new niggles, cleared restrictions.

## Health Reports — `health-reports/`

Drop any medical or health documentation here — bloodwork, PT/physio notes, sports-medicine assessments, DEXA scans, VO2max test results. Agents will read relevant files here before analyzing training or building a plan, e.g. to factor in an iron deficiency flagged in bloodwork, or a physio's return-to-run protocol after an injury.

## Research — `research/`

If the `paper-search` MCP server is set up, agents can search academic literature and turn it into coaching
knowledge. Create this folder when you first ask a research question — the agent will make it for you.

```
workspace/research/
├── papers/           # downloaded PDFs and extracted text
├── notes/            # claim tables (population, design, effect size, caveats)
└── skills-drafts/    # synthesized skills, yours to approve before promotion
```

Ask things like:

```text
Find research on taper length before a marathon.
What does the literature actually say about lifting twice a week while running?
Summarize recent studies on HRV-guided training.
Turn what you find about altitude training into a skill.
```

Everything lands here rather than in the repo, so you can review it freely and `git pull` will never conflict.
When a synthesized skill is worth keeping permanently, the agent moves it into `skills/` and records the
sources in that skill's `SOURCES.md`.

## Adding more context

You can add any other files to `workspace/` that help agents understand you better:

- `workspace/nutrition.md` — dietary preferences, restrictions, meal patterns
- `workspace/race-reports/` — post-race reflections agents can learn from
- `workspace/workout-library.md` — exercises you know and like (agents will prefer these)
- Any other Markdown file — agents read the workspace to build context

The more you put here, the less you'll have to repeat yourself.

## Why it's separate

Smart Training is a **template repo** — you pull updates for skills, agents, and tools, but your personal files stay safe here.
