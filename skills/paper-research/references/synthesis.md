# From Evidence to Skill

How to turn retrieved papers into a file that is worth loading in a future session.

## Decide: extend or create?

The most common failure mode is creating a parallel skill that drifts from the installed ones. Check first.

| Situation | Action |
|---|---|
| Topic already covered in `skills/<x>/references/<topic>.md` | **Extend that file.** Add a section + `SOURCES.md` entry. |
| Topic is covered but the existing file is the wrong home | Extend, and add a cross-link |
| Genuinely new domain (e.g. altitude training, heat acclimation) | New `skills/<name>/` |
| Athlete-specific finding | **Not a skill.** Goes in `workspace/notes/`. |

Running, cycling, hypertrophy, strength, nutrition, programming, and assessment already have skills. Adding
a "periodization-research" skill next to `running-training` would be duplication. Extend
`skills/running-training/references/periodization.md` instead.

## Writing the description field

`description` is the only text the model sees when deciding whether to load the skill. It is a **trigger
specification**, not a summary. If it does not name the situations that should activate it, the skill will
sit there unused.

Good:

```yaml
description: >
  Altitude acclimation for endurance athletes — ascent protocols, live-high/train-low,
  hypoxic dose, and the hematological timeline. Use when the athlete trains or races above
  1500 m, is preparing for a high-altitude race, or asks about altitude camps, hypoxic
  training, or "how long does it take to acclimatize".
```

Bad — describes contents, names no trigger:

```yaml
description: A comprehensive guide to altitude training covering physiology and protocols.
```

Rules: third person, present tense, "Use when…", include the concrete phrases an athlete would actually type.

## Grading rubric

Carry the tier into the skill text — a reader must never have to guess how strong a claim is.

| Tier | Design | Use |
|---|---|---|
| **A** | Systematic review / meta-analysis of RCTs | Prescribe directly |
| **B** | Several consistent RCTs | Prescribe with stated confidence |
| **C** | One RCT or small trial | Suggest; flag as preliminary |
| **D** | Narrative review, expert opinion, mechanistic/in vitro | Mention; never the sole basis for a prescription |
| **P** | Preprint (bioRxiv/arXiv), unreviewed | Mention with explicit caveat |
| **X** | Abstract-only, full text unavailable | Do not prescribe from it |

Two extra modifiers worth stating in prose:

- **Not peer reviewed** — for preprints. Say it, every time.
- **Indirect evidence** — evidence from a population unlike the athlete's (mice, sedentary men, elite
  marathoners) applied to a recreational 40 km/week runner. Name the gap.

## Handling the messy parts

### Contradictory findings

Do not resolve conflicts silently. Present both, cite both, and say what would settle it:

> Two trials disagree on whether time-restricted eating impairs high-intensity work.
> [Nearcher et al., 2020, DOI] found no effect on time trial performance, while
> [López et al., 2021, DOI] reported a 4.3% decrement. Populations and protocols differ; neither
> used elite athletes. **Practical read:** not established either way for performance — treat it
> as neutral unless the athlete has a specific reason to adopt it.

*(Note: if you cannot verify a DOI, do not write it. Verify first, or drop the claim.)*

### Small-N and underpowered studies

Report the effect size with its confidence interval. If the interval crosses zero, the study did **not**
demonstrate an effect, regardless of how the p-value was framed.

### Preprints

Preprints are legitimate evidence and often the freshest. Label them Tier P and never let one be the
sole support for a prescription.

### Null results

Worth recording. "Three RCTs found no effect of X" is real evidence and prevents the athlete wasting time
on it.

### Famous papers that get overstated

Check whether the famous finding is in a small study with a wide confidence interval, and whether
replication has occurred. Many canonical training claims rest on n=8–12 studies from decades ago. Say so
when that is the case — it changes how the athlete should act on them.

## Skill body structure

```
---
name: <kebab-case, matches folder>
description: >
  <trigger spec: what it covers + when to use it>
---

# <Title>

<One paragraph: who this serves and what it decides.>

## <Core decision content — tables and rules, not prose>

## <Practical application>

## <Controversies / open questions>

## Companion skills

- **<other-skill>** — <what it covers that this does not>
```

Keep the body to what is needed on every load. Move depth to `references/`.

## Worked example

**Question:** "Does lifting two days a week hold back my running?"

1. **Scope** — recreational 45 km/week runner, Achilles tendinopathy. Claim: concurrent training at
   2 sessions/week impairs running adaptation.
2. **Retrieve** — `pubmed`, `semantic`, `openalex`; query
   `concurrent training interference endurance hypertrophy frequency systematic review`.
3. **Read full text** on the top 3–4. Save to `workspace/research/papers/`.
4. **Extract** into the claim table (see `SKILL.md` Step 4), with n, population, effect sizes.
5. **Grade** — 2024 meta-analysis is Tier A; three small trials are Tier C.
6. **Synthesize** — interference is real but modest at low frequency; the running-specific evidence is
   weaker than the lifting-specific evidence. Hedge accordingly.
7. **Write** — extend `skills/hypertrophy-training/references/concurrent-training.md` with a frequency
   section and a strength-loss-versus-running-loss tradeoff table. Add entries to its `SOURCES.md`.
8. **Verify** — every DOI resolves; every number matches the source; the new text does not contradict
   the athlete's `workspace/injury-history.md` restrictions.

## Citation format

Inline, short, resolvable:

```
**[Author et al., Year](https://doi.org/10.xxxx/xxxxx)** — one-line finding. (Tier B)
```

Mirror every one in `SOURCES.md`:

```markdown
### Concurrent training frequency and interference

**[Author, A., Author, B., et al. (Year). "Title." *Journal*.**
DOI: [10.xxxx/xxxxx](https://doi.org/10.xxxx/xxxxx)
- Design: systematic review / meta-analysis
- Population: n=..., trained adults, mixed sports
- Finding: ...
- Used for: frequency guidance in `concurrent-training.md`
```

The `Used for:` line is what makes the bibliography maintainable. When a claim is later removed or
corrected, that line tells you which citation to check.
