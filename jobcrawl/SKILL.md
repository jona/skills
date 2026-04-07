---
name: jobcrawl
description: "CLI tool for crawling career pages and job aggregators. Use when the user asks to search for jobs, crawl career pages, find job listings, configure jobcrawl, add companies to config, run aggregator searches (YC), detect ATS providers, discover career page URLs, filter saved jobs, or any task involving the jobcrawl CLI. Triggers on: 'crawl jobs', 'find jobs', 'search careers', 'jobcrawl', 'add company', 'crawl aggregators', 'YC jobs', 'detect provider', 'discover career pages', 'match jobs', 'job search config'."
---

# jobcrawl CLI

Job search CLI that crawls career pages and aggregators. Located at `/Users/jona/Code/jobcrawl`.

## Running

```bash
# Development (from project root)
npx tsx src/entrypoints/cli/index.ts <command> [options]

# Built (after `npm run build`)
node dist/entrypoints/cli/index.js <command> [options]

# If globally linked
jobcrawl <command> [options]
```

## Commands

### `init` — Create config files

Creates `~/.jobcrawl/config.yaml`, `credentials.json`, and `raw/` directory.

```bash
jobcrawl init             # Create default config (2800+ companies)
jobcrawl init --force     # Overwrite existing
```

### `crawl` — Crawl multiple career pages

```bash
# From default config (~/.jobcrawl/config.yaml)
jobcrawl crawl --keywords "engineer"

# From inline URLs
jobcrawl crawl --urls https://boards.greenhouse.io/anthropic https://jobs.ashbyhq.com/openai \
  --keywords "senior" "engineer" --remote

# From config file
jobcrawl crawl --file config.yaml --keywords "engineer"

# With aggregators in parallel
jobcrawl crawl --aggregators yc --keywords "engineer" --company-stage seed

# Pipe to jq
jobcrawl crawl --keywords "staff" | jq '.[].title'
```

**Target resolution order:** `--urls` > `--file` > `~/.jobcrawl/config.yaml` > stdin

**Crawl-specific flags:**
- `--urls <urls...>` — Inline URLs
- `--file <path>` — Config file (YAML/JSON)
- `--aggregators <names...>` — Also run aggregators (e.g. `yc`)
- `--concurrency <n>` — Max parallel crawls (default: 5)
- `--network-timeout <ms>` — Browser timeout
- `--max-bubble-levels <n>` — Max parent levels for click-capture

### `crawl-url <url>` — Crawl single URL

```bash
jobcrawl crawl-url https://boards.greenhouse.io/anthropic --keywords "engineer" --output table
```

### `crawl-aggregators <names...>` — Search aggregators only

```bash
jobcrawl crawl-aggregators yc --keywords "engineer" --role engineering --role-type backend \
  --company-stage seed --has-salary --visa-sponsorship
```

Requires Algolia credentials in `~/.jobcrawl/credentials.json` or env vars `YC_ALGOLIA_APP_ID` / `YC_ALGOLIA_API_KEY`.

### `discover` — Find career page URLs

```bash
jobcrawl discover --companies "Anthropic" "OpenAI" "Mistral AI"
jobcrawl discover --companies "Anthropic" --output yaml -o config.yaml
jobcrawl discover --file companies.txt --verify
```

Flags: `--companies <names...>`, `--file <path>`, `--output urls|yaml|json`, `--verify`, `--concurrency <n>`

### `detect <url>` — Identify ATS provider

```bash
jobcrawl detect https://boards.greenhouse.io/anthropic
# { "provider": "greenhouse", "boardToken": "anthropic" }
```

### `match <file>` — Filter saved jobs JSON

```bash
jobcrawl match jobs.json --keywords "senior" --remote --output table
```

## Search Criteria Flags (all crawl commands)

| Flag | Description |
|------|-------------|
| `--keywords <terms...>` | Job title keywords (any match) |
| `--exclude <terms...>` | Exclude matching keywords |
| `--location <location>` | Location substring filter |
| `--remote` / `--onsite` / `--hybrid` | Work mode filters |
| `--department <depts...>` | Department filter |
| `--role <roles...>` | engineering, design, product, science, sales, marketing |
| `--role-type <types...>` | backend, frontend, full-stack, ML, DevOps |
| `--job-type <types...>` | fulltime, internship, contract |
| `--min-experience <years...>` | Min years (e.g. 0, 3) |
| `--company-stage <stages...>` | seed, series-a, growth, scale |
| `--industry <industries...>` | Industry filter |
| `--company-size <sizes...>` | 1-10, 11-50, 51-300, 301+ |
| `--has-salary` | Only with salary |
| `--has-equity` | Only with equity |
| `--has-interview-process` | Only with interview process |
| `--visa-sponsorship` | Only with visa sponsorship |

**Note:** `--role`, `--role-type`, `--job-type`, `--company-stage`, `--industry`, `--company-size`, `--min-experience` are only effective with aggregators (YC). Direct career page crawls use `--keywords`, `--exclude`, `--location`, `--remote`/`--onsite`/`--hybrid`, and `--department` for filtering.

## Output Flags (all commands)

- `--output json|table|markdown|csv` (default: `json`)
- `-o, --out <file>` — Write to file
- `--save-raw` — Save raw API responses to `~/.jobcrawl/raw/`

## Config Format (`~/.jobcrawl/config.yaml`)

```yaml
aggregators:
  - type: yc
    enabled: true

companies:
  # Slug-based (recommended) — auto-probes Greenhouse > Ashby > Lever
  - company: Anthropic
    slug: anthropic
    provider: greenhouse        # optional — skip probing
    fallback: https://...       # optional — fallback URL

  # URL-based
  - url: https://example.com/careers
    company: Company Name

defaults:
  concurrency: 5
  browser:
    networkTimeout: 120000
    maxBubbleLevels: 5
```

## Credentials (`~/.jobcrawl/credentials.json`)

```json
{
  "yc": {
    "algoliaAppId": "YOUR_APP_ID",
    "algoliaApiKey": "YOUR_API_KEY"
  }
}
```

Or env vars: `YC_ALGOLIA_APP_ID`, `YC_ALGOLIA_API_KEY`.

## Architecture

**Three-tier extraction:**
1. **API-first** — HTTP probe detects ATS (Greenhouse/Ashby/Lever), calls public JSON API. Sub-second, no browser.
2. **Browser rendering** — Falls back to agent-browser (Chrome via CDP) + DOM heuristics for JS-rendered pages.
3. **Aggregators** — Cross-company search (YC Algolia). Runs in parallel with targets. Results deduplicated.

**Supported providers:** Greenhouse, Ashby, Lever (API), Workday/BambooHR/Workable (detection only), generic (HTML heuristics).

**Slug resolution:** When using slug-based targets, probes Greenhouse > Ashby > Lever APIs in order. Provider hint skips probing. Fallback URL used if all APIs fail.

**TTY vs piped:** Interactive terminal shows Ink progress UI. Piped mode outputs structured data to stdout, progress to stderr.

## Development

```bash
npm run dev -- <command> [options]    # Run in dev mode
npm run build                         # Compile TypeScript
npm test                              # Run vitest
npm run test:watch                    # Watch mode
npm run format                        # Prettier
```

**Source layout:**
- `src/entrypoints/cli/` — Commander.js commands + Ink UI
- `src/core/` — Fetch, detect, extract, match, format
- `src/core/providers/` — Greenhouse, Ashby, Lever, generic extractors
- `src/core/aggregators/` — YC (Algolia)
- `src/threads/` — Per-URL pipeline + concurrency pool
- `src/orchestrators/` — Multi-URL + aggregator coordination
- `src/utils/` — Config (Zod), LLM (Claude), web search
- `src/data/companies.ts` — 2800+ company dataset
- `src/events.ts` — Typed EventBus (pub/sub for progress)
- `src/types/index.ts` — All type definitions

**Key types:** `Job`, `SearchCriteria`, `Target` (SlugTarget | UrlTarget), `Provider`, `Aggregator`, `CrawlResult`, `OutputFormat`
