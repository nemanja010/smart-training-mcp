# Upstream Skill Sources

This repository vendors training skills from external, permissively licensed
repositories as plain files under `skills/`. They are **not** git submodules —
that keeps cloning simple (a single `git clone`, no `--recurse-submodules`) and
avoids nested-submodule complexity.

Each vendored skill is pinned to the upstream commit listed below. To update a
skill to a newer upstream revision, change the commit below and run
`scripts/sync-upstream.ps1` (or copy the changed files manually), then review
the diff and commit.

## Vendored skills

| Skill (in `skills/`) | Upstream repo | Upstream path | Pinned commit |
|----------------------|---------------|---------------|---------------|
| `cycling-training` | [disco-trooper/skills](https://github.com/disco-trooper/skills) | `cycling-training/` | `41bf668` |
| `hypertrophy-training` | [disco-trooper/skills](https://github.com/disco-trooper/skills) | `hypertrophy-training/` | `41bf668` |
| `schoenfeld-hypertrophy` | [borisghidaglia/science-based-lifter](https://github.com/borisghidaglia/science-based-lifter) | `skills/schoenfeld-hypertrophy/` | `3718ff9` |
| `sbs-training` | [borisghidaglia/science-based-lifter](https://github.com/borisghidaglia/science-based-lifter) | `skills/sbs-training/` | `3718ff9` |
| `rp-training` | [borisghidaglia/science-based-lifter](https://github.com/borisghidaglia/science-based-lifter) | `skills/rp-training/` | `3718ff9` |
| `rp-diet` | [borisghidaglia/science-based-lifter](https://github.com/borisghidaglia/science-based-lifter) | `skills/rp-diet/` | `3718ff9` |
| `program-creation` | [borisghidaglia/science-based-lifter](https://github.com/borisghidaglia/science-based-lifter) | `skills/program-creation/` | `3718ff9` |
| `assessment` | [borisghidaglia/science-based-lifter](https://github.com/borisghidaglia/science-based-lifter) | `skills/assessment/` | `3718ff9` |

## Own skills (not vendored)

These are developed in this repository and are not pulled from anywhere:

- `skills/running-training` — running coaching skill
- `skills/intervals-icu` — Intervals.icu coaching skill (pairs with the MCP server in `intervals-icu/`)

## How to update a vendored skill

**Option 1 — sync script (recommended):**

```powershell
# Windows (PowerShell)
.\scripts\sync-upstream.ps1
```

The script clones each upstream repo to a temporary directory, checks out the
pinned commit, copies the listed skill folders into `skills/`, and removes the
temporary clone. Review the git diff, then commit.

**Option 2 — manual copy:**

Clone or pull the upstream repo elsewhere on your machine, copy the changed
skill folder into `skills/`, review the diff, and commit. For markdown-only
skills this is usually a two-minute job.

## Licensing

All vendored skills are MIT-licensed:

- `disco-trooper/skills` — MIT
- `borisghidaglia/science-based-lifter` — MIT

`skills/running-training` is MIT and `intervals-icu/` (the MCP server) is
GPL-3.0-only. See the root README for full license details.
