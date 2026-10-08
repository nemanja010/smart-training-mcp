# Sources and References — Paper Research Skill

This file records every academic source retrieved and cited while building or updating skills in this
repository. It is the audit trail: if a claim in a skill is wrong, start here.

## How to use this file

When synthesizing a skill:

1. Retrieve papers via the `paper-search` MCP server (see `SKILL.md` and `references/retrieval.md`).
2. Read full text and extract claims with population, design, effect size, and caveats.
3. Cite inline in the skill as a linked DOI with an evidence tier.
4. Add a matching entry below with a **`Used for:`** line naming the file and section it supports.

The `Used for:` line is what keeps this maintainable. When a claim is revised or removed, it tells you
which citation to re-check.

## Evidence tiers

| Tier | Design | Use |
|---|---|---|
| A | Systematic review / meta-analysis of RCTs | Prescribe directly |
| B | Several consistent RCTs | Prescribe with stated confidence |
| C | Single RCT or small trial | Suggest; flag as preliminary |
| D | Narrative review, expert opinion, mechanistic | Mention only |
| P | Preprint, unreviewed | Mention with explicit caveat |
| X | Abstract-only, full text unobtainable | Do not prescribe |

---

## Sources

_No sources recorded yet._

### Template — copy for each paper

```markdown
### [Topic grouping, e.g. "Concurrent training frequency"]

**[Author, A., Author, B., & Author, C. (Year). "Full paper title." *Journal Name*, volume(issue), pages.**
DOI: [10.xxxx/xxxxx](https://doi.org/10.xxxx/xxxxx)
- **Design:** systematic review / meta-analysis / RCT / crossover / narrative review / preprint
- **Population:** n=..., training status, sex, age, sport
- **Finding:** the actual result, with numbers
- **Effect size:** value and confidence interval if reported
- **Caveats:** stated limitations, plus population gaps
- **Tier:** A
- **Used for:** `skills/<name>/references/<file>.md` — <section>
- **Retrieved:** YYYY-MM-DD via `paper-search` MCP
```

---

## Retrieval log

Append a line per synthesis run so it is auditable which searches produced which skills.

| Date | Question | Sources queried | Skill written/updated |
|------|----------|-----------------|------------------------|
| | | | |
