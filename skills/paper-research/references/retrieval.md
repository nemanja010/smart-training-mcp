# Retrieval Playbook

Practical guidance for getting good results out of the `paper-search` MCP server.

## Source selection by discipline

| Domain | Start with | Add | Notes |
|---|---|---|---|
| Exercise physiology, training load, nutrition | `pubmed`, `europepmc`, `openalex` | `semantic` | Europe PMC gives open full text |
| Running / endurance coaching | `openalex`, `crossref` | `pubmed`, `semantic` | Coaching literature is thin and heavily cited — use `get_citing_papers` to find newer work |
| Resistance training / hypertrophy | `pubmed`, `openalex` | `semantic`, `pmc` | Strong RCT base, many OA |
| Sports science general | `openalex`, `crossref` | `pubmed`, `arxiv` | OpenAlex has the best multidisciplinary reach |
| Concurrent training / interference | `pubmed`, `semantic` | `openalex` | Highly cited core papers — follow citations forward |
| Sleep, HRV, recovery | `pubmed`, `biorxiv`, `medrxiv` | `pmc` | Many preprints; grade as P until reviewed |
| Methods, ML, data analysis | `arxiv` | `openalex`, `dblp` | arXiv is the right home |
| Anything paywalled | `unpaywall` (DOI lookup) | `download_with_fallback` | Unpaywall resolves a DOI to a legal OA copy |

**Starting points by coverage:**

- `openalex,crossref,pubmed,arxiv` — good default for a coaching question
- `semantic` — best when you need citation counts or want to walk the citation graph
- Broad sweep: omit `sources` to search everything (slower, noisier)

**Avoid:** `google_scholar` as a default. It rate-limits aggressively, triggers CAPTCHAs, and enters a
60-second cooldown (extending up to 15 minutes) after repeated blocks. Use it as a last-resort discovery
source, never as the backbone.

## Query construction

Search indexes respond to **specific technical phrasing**, not natural questions.

| Weak | Strong |
|---|---|
| "is intermittent fasting good for runners" | "time-restricted eating endurance exercise performance randomized trial" |
| "how often should I lift" | " resistance training frequency hypertrophy systematic review" |
| "best recovery method" | "sleep extension recovery muscle glycogen synthesis athletes" |

Rules:

1. Strip the interrogative frame. Keywords, not sentences.
2. Add a design term to bias toward strong evidence: `systematic review`, `meta-analysis`, `randomized controlled trial`, `randomised`.
3. Add a population term when it matters: `trained`, `elite`, `well-trained`, `masters`, `female`.
4. Quote exact technical terms: `"critical power"`, `"heart rate variability"`, `"ACWR"`.
5. Two or three focused queries beat one long one — then merge and deduplicate.

## Getting full text

1. Try the source-native reader first: `read_arxiv_paper`, `read_semantic_paper`, etc.
2. If it fails, use the fallback chain:

```
download_with_fallback(source="<source>", paper_id="<id>", doi="<doi>", save_path="workspace/research/papers/")
```

This tries publisher OA links, then OpenAIRE / CORE / Europe PMC / PMC, then Unpaywall by DOI. **Always pass
the DOI** when you have one — it unlocks the Unpaywall leg of the chain.

**Source support is uneven.** `openalex` and `crossref` are metadata-only: passing them as the `source`
fails immediately with `Unsupported source for primary download`. For those, go straight to a full-text
source (`arxiv`, `pmc`, `europepmc`, `biorxiv`, `medrxiv`, `zenodo`, `hal`, `iacr`) or rely on the Unpaywall
leg — which requires `PAPER_SEARCH_MCP_UNPAYWALL_EMAIL` to be set. Without that email the chain has nothing
to fall back to, and `download_with_fallback` reports failure even for papers that are freely available.

3. If you have only a DOI, resolve metadata first:

```
search_unpaywall(query="<doi>")     # OA location
get_crossref_paper_by_doi(doi="<doi>")   # canonical metadata
```

4. If nothing is reachable, the paper is **abstract-only**. Grade it X and do not build a prescription on it.

## Finding newer and contradicting work

The citation-graph tools (`get_citing_papers`, `get_referenced_papers`) appear in the upstream README but are
**not present in the released package** this repository uses (0.1.4). Verify against your active tool list
before relying on them — call `tools/list` if unsure.

Without them, approximate it through search:

- **"Has anyone updated this?"** — search the concept, not the citation. Add a recency term
  (`2023..2026`) or sort by date, then look for meta-analyses and systematic reviews, which by definition
  survey recent work.
- **"Does anyone disagree?"** — search the claim with a dissent framing
  (`"<claim>" no effect OR null result`). Null results rarely surface otherwise.
- **Foundational references** — read the reference list of a recent review instead.

## Knowing when a source failed

`search_papers` returns an `errors` object keyed by source. **Read it.** A successful result from three of
four requested sources is a partial answer, not a complete one — say which sources failed rather than
presenting thin results as exhaustive.

Common causes and responses:

| Symptom | Cause | Response |
|---|---|---|
| `unpaywall` missing entirely | `PAPER_SEARCH_MCP_UNPAYWALL_EMAIL` unset | See setup — this source is disabled without it |
| `search_semantic` returns `[]` | Anonymous rate limit — fails **silently**, with no entry in `errors` | Treat as a failed source, not as "no literature exists". Retry, add a free key, or use `search_papers` with other sources |
| `semantic` 429 | Anonymous rate limit | Add a free Semantic Scholar key |
| `openalex` 403/429 | Anonymous daily quota | Add a free OpenAlex key |
| `core` 500/timeout | Unauthenticated throttling | Add a free CORE key |
| `google_scholar` error | Bot detection | Skip it. Use `openalex` or `semantic`. |
| `citeseerx` empty | Endpoint intermittently down | Ignore; returns empty gracefully |

> [!IMPORTANT]
> An empty result set is not the same as a failed source. The direct `search_semantic` tool in particular can
> return `[]` on rate limit without recording anything in `errors`. **Never report "no research exists" from
> an empty result alone** — cross-check with `openalex` or `crossref` before making a claim about the state
> of the literature.

## Timing

Broad multi-source searches are slow. Narrow the source list rather than waiting:

```
search_papers(query="...", max_results=3, sources="openalex,crossref")
```

The CLI additionally supports a per-source deadline (`--source-timeout SECONDS`), which runs sources in
separate processes so one slow provider cannot stall the whole search. Use it only when scripting.

## Optional API keys

All optional except Unpaywall's email. Stored in `~/.config/paper-search-mcp/.env` and auto-loaded by the
server.

| Variable | Effect |
|---|---|
| `PAPER_SEARCH_MCP_UNPAYWALL_EMAIL` | **Required** for the Unpaywall source and the DOI fallback leg |
| `PAPER_SEARCH_MCP_CORE_API_KEY` | Recommended — removes throttling on CORE |
| `PAPER_SEARCH_MCP_SEMANTIC_SCHOLAR_API_KEY` | Raises Semantic Scholar rate limits |
| `PAPER_SEARCH_MCP_OPENALEX_API_KEY` | ~10× the keyless daily budget |
| `PAPER_SEARCH_MCP_DOAJ_API_KEY` | Raises DOAJ hourly limit |

See `paper-search/.env.example` in the repository.
