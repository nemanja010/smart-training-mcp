---
name: paper-research
description: >
  Evidence acquisition and skill synthesis — searches academic literature (arXiv, PubMed, OpenAlex, Crossref, Semantic Scholar, Europe PMC, and 20+ more)
  via the paper-search MCP server, reads full text, extracts citable findings, and converts them into
  repository-conformant coaching skills. Use when the user asks to find research or papers ("what does the
  evidence say about...", "find studies on...", "is there research on..."), asks to update a skill from the
  literature, requests an evidence review or literature summary, or asks whether a training claim is
  evidence-based. Also trigger when a coaching answer would rest on an empirical claim the installed skills
  do not cover.
---

# Paper Research & Skill Synthesis

You have access to a live academic literature search server via MCP. This skill turns raw papers into
durable, citable coaching skills.

**Two jobs, do not confuse them:**

1. **Answer a research question** — retrieve and report. Stop when the answer is supported.
2. **Build or update a skill** — retrieve, then write files that persist. Only when explicitly asked.

Do not create or modify skill files unless the user asked for a skill. Reporting findings in chat is not
the same as writing a skill.

---

## Tool Discovery (do this first)

Tool names vary by runtime. Never hardcode a prefix:

| Runtime | Invocation |
|---|---|
| OpenCode / Claude Code | `paper-search_search_papers`, `paper-search_read_arxiv_paper`, … (native `tools["paper-search"].<tool>`) |
| Antigravity | `call_mcp_tool(ServerName="paper-search", ToolName="search_papers", Arguments={...})` |
| DSH | `mcp__paper-search__search_papers` |

Match against active tool declarations or `<mcp_servers>`. The server exposes **57 tools**: `search_papers`,
`download_with_fallback`, per-source `search_*` / `download_*` / `read_*` pairs,
`get_crossref_paper_by_doi`, and more. Call `tools/list` if unsure what is available.

Verified tool surface (release 0.1.4, 57 tools): `search_papers`, `download_with_fallback`,
`search_{arxiv,base,biorxiv,citeseerx,crossref,core,dblp,doaj,europepmc,google_scholar,hal,iacr,medrxiv,openaire,openalex,pmc,pubmed,semantic,ssrn,unpaywall,zenodo}`, matching `download_*` / `read_*` pairs, and `get_crossref_paper_by_doi`.

The upstream README also documents `get_citing_papers`, `get_referenced_papers`, `extract_sections`, and
`acm`/`ieee` tools — **these are not in the released package**. Do not call them; if a tool is unknown,
check your active tool list rather than assuming it exists.

The server also ships a CLI (`uvx --from paper-search-mcp --with "mcp<2" paper-search`) with
`search`, `download`, `read`, and `sources` subcommands. Prefer MCP tools; the CLI is a fallback
for batch scripting and when MCP is unavailable.

---

## The Pipeline

```
Scope → Retrieve → Read full text → Extract claims → Grade evidence → Synthesize → Write skill → Verify
```

Never skip from Retrieve to Write. A skill built from abstracts alone is a skill full of guesses.

### 1. Scope

Before searching, pin down:
- **The claim to resolve** — one sentence, falsifiable.
- **Population** — humans? runners vs. cyclists? trained vs. untrained? trained athletes matter enormously.
- **Population context** — read `workspace/profile.md` and `workspace/injury-history.md`. If the athlete is a
  45 km/week runner with Achilles tendinopathy, "does eccentric calf work help" is a different search than the
  generic question.
- **Discipline** — this determines which sources to use (see below).

State the question in one line and get agreement before a large search. A five-minute scoping check saves
a twenty-minute wrong search.

### 2. Retrieve

See `references/retrieval.md` for source selection, query construction, and timeouts.

The fast path for most coaching questions:

```
search_papers(query="<plain-language question>", max_results=5, sources="openalex,crossref,pubmed,arxiv")
```

Use `semantic` for citation counts, `pubmed`/`pmc`/`europepmc`/`biorxiv`/`medrxiv` for physiology and
biomedicine, `arxiv` for methods and ML, `openalex`/`crossref` for broad multidisciplinary coverage.

**Present results before reading.** Show a compact table — title, authors, year, source, DOI — and let the
user pick. Do not silently read twenty papers.

### 3. Read Full Text

Abstracts are marketing copy. The effect size, the confidence interval, the population, and the limitations
live in the body.

- `read_<source>_paper(paper_id, save_path="workspace/research/papers/")` → extracted text
- `download_with_fallback(...)` → tries publisher OA, then OpenAIRE/CORE/Europe PMC/PMC, then Unpaywall
  by DOI. **Use this** when a source-specific download fails — it is the whole point of the fallback chain.

**Always save under `workspace/research/papers/`.** Never write PDFs to the repo root or `skills/`.

Track what you actually read. If only the abstract was available, the claim is abstract-only and must be
labelled as such (see grading).

### 4. Extract Claims

For each paper, extract into a fixed shape. This is the raw material for the skill:

```markdown
### <short claim, e.g. "Polarized distribution outperforms threshold-heavy in trained runners">
- **Source:** <Author et al. (Year)>. *Title*. <DOI>
- **Design:** meta-analysis / RCT / crossover / narrative review / preprint / abstract-only
- **Population:** n=…, trained/untrained, sex, age, sport
- **Finding:** <the actual result, with numbers>
- **Effect size:** <value and CI if reported>
- **Caveats:** <stated limitations, or your own read>
- **Bearing on coaching:** <what an athlete or coach should actually do differently>
```

Numbers are not optional. "Improved VO2max" is not a finding; "VO2max +3.2 mL·kg⁻¹·min⁻¹ (95% CI 1.1–5.4)"
is.

### 5. Grade Evidence

Label every extracted claim with a tier, and carry that tier into the skill:

| Tier | Means | How it may be used |
|---|---|---|
| **A** | Systematic review / meta-analysis of RCTs | Prescribe directly |
| **B** | Multiple RCTs, consistent | Prescribe with stated confidence |
| **C** | Single RCT or small trial | Suggest; flag as preliminary |
| **D** | Narrative review, expert opinion, mechanistic study | Mention; do not prescribe from it alone |
| **P** | Preprint (bioRxiv/arXiv), not peer reviewed | Mention only with explicit caveat |
| **X** | Abstract-only, full text unobtainable | Do not build a prescription on it |

Disagreement is data. When trials conflict, say so and cite both. Do not average them into a false consensus.

### 6. Synthesize

Only now write prose. The synthesis is the *judgment*, and it must be traceable to Step 4 rows:

- **What is well established** (Tier A/B) → prescriptive language.
- **What is promising but unsettled** (C/P) → hedged language, explicitly provisional.
- **What is contested** → present both sides.
- **What the literature does not answer** → say so. This is often the most useful output, because it tells
  the athlete what nobody knows.

### 7. Write the Skill

Only on explicit request. Draft to `workspace/research/skills-drafts/<name>/` first. Show the user the
diff and the source table. Promote into `skills/<name>/` only after they approve.

Skill format contract for this repository:

```
skills/<name>/
├── SKILL.md          # required: YAML frontmatter (name, description) + body
├── references/       # one topic per file, loaded on demand
└── SOURCES.md        # every paper cited, with DOI
```

Rules:

- **`description` is the trigger.** It must state *when to use the skill*, not what it contains. This is the
  only text the model sees when deciding to load it. Include concrete trigger phrases.
- **Keep `SKILL.md` short** — routing, core rules, decision tables. Push detail into `references/`. The body
  is always loaded; the references are not.
- **Cite inline** with author-year and DOI, and mirror every one in `SOURCES.md`.
- **Grade every prescription inline** — `(Tier A, meta-analysis of 12 RCTs)`. A reader must never have to
  guess how strong a claim is.
- **Write to the athlete.** Imperative, specific, coach-to-athlete. Not journal-ese.
- **Include the counter-evidence** if the literature has any. A skill that only ever confirms the athlete is
  a confirmation-bias engine.

### 8. Verify

Before declaring a skill done:

- [ ] Every citation resolves to a paper that was actually retrieved in this session
- [ ] Every DOI checked; authors, year, and title match the record
- [ ] Numbers match the source text, not memory
- [ ] Abstract-only and preprint sources labelled
- [ ] Frontmatter is valid YAML with `name` and `description`
- [ ] Skill placed under `workspace/` or `skills/`, never the repo root
- [ ] No PDFs, caches, or scratch files left in `skills/`

If you cannot verify a citation, cut the claim. A smaller skill with real citations beats a large one with
invented ones.

---

## Guardrails

**Never fabricate a citation.** No plausible-looking DOI, no "Smith et al. (2019)" you did not retrieve. If
the literature is thin, say the evidence is thin.

**Never present a preprint as settled.** bioRxiv and arXiv are unreviewed.

**Distinguish correlation from causation**, and association from mechanism. If the paper does not establish
the mechanism it proposes, do not present the mechanism as fact.

**Respect access boundaries.** The server is OA-first and lawful by default. Leave `use_scihub` off unless
the user explicitly opts in and understands the legal exposure.

**Do not overfit to one athlete.** A skill serves all athletes who load it. Athlete-specific advice belongs
in `workspace/`, not in `skills/`.

**Do not duplicate existing skills.** Before writing a new skill, check whether `skills/running-training`
or another installed skill already covers the topic. The right move is often to extend an existing
`references/` file, not to create a parallel skill that will drift.

---

## Working Directory

```
workspace/research/
├── papers/           # downloaded PDFs + extracted text
├── notes/            # claim extraction tables (Step 4)
└── skills-drafts/    # synthesized skills awaiting approval
```

Create subdirectories on demand. Everything here is gitignored, so drafts stay private and `git pull` never
conflicts. Never write outside the project folder.
