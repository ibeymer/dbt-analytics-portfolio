# dbt Analytics Portfolio — NFL & PGA Golf Pipelines

An end-to-end analytics-engineering project built with **dbt** on **DuckDB**, fed
by a **live API extract**. It pulls real sports data from ESPN's public API,
loads it into a warehouse, and transforms it through a layered pipeline
(`staging → intermediate → marts`) into clean, tested, documented data marts for
two domains:

- **NFL** — full 2023 regular season (teams, games) → standings & game facts
- **PGA golf** — the 2024 majors + The Players (leaderboards with per-round
  scores) → player scoring profiles & round facts

It is designed to be **cloned and run with one command** — DuckDB is an embedded
warehouse (no accounts/servers) and the ESPN API needs no key.

```
  ESPN API  ──▶  EXTRACT (Python)  ──▶  seeds   ──▶  staging  ──▶ intermediate ──▶  marts
  (NFL +PGA)     extract_nfl.py         raw CSVs     clean/type    business        dims · facts
                 extract_golf.py                                   logic           aggregates
```

## What this demonstrates

- **Live API integration** — a Python extract layer that pulls from a real
  external API (retries, backoff, JSON shaping) into raw CSVs.
- **Layered dbt architecture** — staging views, intermediate business logic,
  materialized marts, with clear separation of concerns.
- **Dimensional modeling** — conformed dimensions (`dim_*`), fact tables
  (`fct_*`), and aggregate marts (`mart_*`).
- **Data quality testing** — 40+ tests: uniqueness, not-null, referential
  integrity (`relationships`), accepted values/ranges (`dbt_utils`), composite
  keys, and **singular reconciliation tests** (e.g. team-grain points must equal
  game-grain points).
- **Real-world data cleaning** — the extract filters source anomalies
  (withdrawals, partial rounds, ESPN score-to-par inconsistencies) so the
  warehouse stays trustworthy.
- **Orchestration** — `run_pipeline.py` runs extract → load → transform → test in
  one command, exiting non-zero on failure so a scheduler/CI can gate on it.
- **Documentation & lineage** — every model and column is described; `dbt docs`
  renders the full DAG.
- **Git branching workflow** — `main` (production) + `qa` (validation) branches,
  changes promoted via pull request.

## Tech stack

| Layer            | Tool                              |
| ---------------- | --------------------------------- |
| Source           | ESPN public JSON API (no key)     |
| Extract          | Python 3 (standard library)       |
| Transformation   | dbt-core                          |
| Warehouse        | DuckDB (embedded, file-based)     |
| Testing          | dbt tests + dbt_utils             |
| Version control  | Git / GitHub (`main` + `qa`)      |

## Project structure

```
dbt-analytics-portfolio/
├── scripts/
│   ├── run_pipeline.py           # one-command orchestrator: extract -> load -> transform -> test
│   ├── espn_api.py               # shared ESPN HTTP client (retries/backoff)
│   ├── extract_nfl.py            # pull NFL teams + season games from ESPN
│   └── extract_golf.py           # pull PGA leaderboards (per-round scores) from ESPN
├── seeds/                        # raw CSVs pulled from the API (nfl/, golf/) + tests
├── models/
│   ├── staging/                  # 1:1 with sources — clean & type only (views)
│   ├── intermediate/             # reusable business logic (views)
│   └── marts/                    # dims, facts, aggregates (tables)
│       ├── nfl/                  # standings, game facts, team dim
│       └── golf/                 # scoring summary, round facts, player/tournament dims
├── macros/safe_divide.sql        # null-safe division / percentage helpers
├── tests/                        # singular (reconciliation / business-rule) tests
├── analyses/                     # ad-hoc compiled queries
├── dbt_project.yml
├── profiles.yml                  # DuckDB, in-repo (use --profiles-dir .)
└── packages.yml                  # dbt_utils
```

## Quickstart

Requires Python 3.9+.

```bash
pip install -r requirements.txt
python scripts/run_pipeline.py
```

That's it. `run_pipeline.py` is the orchestrator — it runs the whole flow end to
end, the way a scheduler (Airflow, Dagster, cron) would:

```
EXTRACT  -> pull NFL + PGA data from ESPN     (scripts/extract_*.py)
LOAD     -> load CSVs into DuckDB             (dbt seed)
TRANSFORM-> build staging -> int -> marts     (dbt run)
TEST     -> run all data-quality tests        (dbt test)
```

Useful flags:

```bash
python scripts/run_pipeline.py --target qa       # run against the qa warehouse
python scripts/run_pipeline.py --skip-generate   # reuse committed CSVs (no API call)
python scripts/run_pipeline.py --full-refresh    # rebuild all tables from scratch
```

It exits non-zero if any step fails, so CI / schedulers can gate on it.

### Or run the steps manually

```bash
python scripts/extract_nfl.py && python scripts/extract_golf.py   # 1. extract
dbt deps --profiles-dir .                                         # 2. install dbt_utils
dbt build --profiles-dir .                                        # 3. seed + run + test
```

Either path creates `dev.duckdb` in the project root with all marts populated. Explore it:

```bash
dbt show --profiles-dir . --limit 10 --inline "select * from main_marts.mart_nfl_standings order by win_pct desc"
```

### Browse the docs & lineage graph

```bash
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

## Headline marts

**NFL**
- `mart_nfl_standings` — season standings per team: wins/losses/ties, win pct,
  points for/against, point differential, and division rank.
- `fct_nfl_games` — every game with team names, margin, and outcome.

**PGA golf**
- `mart_golf_player_scoring_summary` — scoring average, average score to par,
  tournaments/rounds played, cuts made, and best finish, ranked (min 4 rounds).
- `fct_golf_rounds` — every player-round with strokes, par, and score to par.

## Data sources & reproducibility

Data comes from ESPN's public (undocumented) JSON API — no key required:

- NFL: `site.api.espn.com/.../football/nfl/scoreboard` + `cdn.espn.com/core/nfl/standings`
- PGA: `site.api.espn.com/.../golf/pga/scoreboard`

The extract targets **fixed historical seasons** (NFL 2023, PGA 2024 majors) so
the committed CSVs are stable and pipeline runs are comparable over time. The raw
CSVs are committed under `seeds/`, so the project also runs fully offline with
`--skip-generate`. Because the API is unofficial, response shapes can change; the
extract code is defensive (retries, missing-field handling, anomaly filtering).

## Branching workflow

| Branch | Purpose                                                       |
| ------ | ------------------------------------------------------------ |
| `main` | Production-ready models. Changes arrive via PR.              |
| `qa`   | Validation branch — run `dbt build --target qa` (isolated `qa.duckdb`) to vet changes before promoting to `main`. |

Typical flow: branch from `qa` → develop → `dbt build --target qa` → open PR into
`main` once tests pass.
