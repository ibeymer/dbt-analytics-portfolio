# dbt Analytics Portfolio — Football & Golf Pipelines

An end-to-end analytics-engineering project built with **dbt** on **DuckDB**. It
takes synthetic raw sports data through a layered transformation pipeline
(`staging → intermediate → marts`) into clean, tested, documented data marts for
two domains: **football** (league results & player stats) and **golf**
(tournament scoring).

It is designed to be **cloned and run in under two minutes** — DuckDB is an
embedded warehouse, so there are no accounts, servers, or credentials.

```
                ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  Python  ──▶   │   seeds      │ ──▶ │   staging    │ ──▶ │ intermediate │ ──┐
 generator      │  (raw CSVs)  │     │ (clean/type) │     │  (business   │   │
                └──────────────┘     └──────────────┘     │    logic)    │   │
                                                          └──────────────┘   │
                                                                             ▼
                                                          ┌──────────────────────┐
                                                          │        marts         │
                                                          │  dims · facts · agg  │
                                                          └──────────────────────┘
```

## What this demonstrates

- **Layered dbt architecture** with clear separation of concerns (staging views,
  intermediate business logic, materialized marts).
- **Dimensional modeling** — conformed dimensions (`dim_*`), fact tables
  (`fct_*`), and aggregate marts (`mart_*`).
- **Data quality testing** — 60+ tests: uniqueness, not-null, referential
  integrity (`relationships`), accepted values/ranges (`dbt_utils`), composite
  keys, and **singular business-rule tests** (e.g. every team plays 38 matches).
- **Reusable Jinja macros** (`safe_divide`, `pct`) to keep rate calculations DRY.
- **Reproducible source data** — a dependency-free Python generator
  (`scripts/generate_seeds.py`) produces deterministic seed CSVs.
- **Documentation & lineage** — every model and column is described; `dbt docs`
  renders a full DAG.
- **Git branching workflow** — `main` (production) + `qa` (validation) branches,
  with a matching dbt `qa` target for environment isolation.

## Tech stack

| Layer            | Tool                          |
| ---------------- | ----------------------------- |
| Transformation   | dbt-core                      |
| Warehouse        | DuckDB (embedded, file-based) |
| Source data      | Python 3 (standard library)   |
| Testing          | dbt tests + dbt_utils         |
| Version control  | Git / GitHub (`main` + `qa`)  |

## Project structure

```
dbt-analytics-portfolio/
├── scripts/
│   ├── run_pipeline.py           # one-command orchestrator: extract -> load -> transform -> test
│   └── generate_seeds.py         # deterministic synthetic-data generator (the "extract" step)
├── seeds/                        # raw CSVs (football/, golf/) + tests
├── models/
│   ├── staging/                  # 1:1 with sources — clean & type only (views)
│   ├── intermediate/             # reusable business logic (views)
│   └── marts/                    # dims, facts, aggregates (tables)
│       ├── football/             # standings, player season summary, ...
│       └── golf/                 # scoring summary, round facts, ...
├── macros/safe_divide.sql        # null-safe division / percentage helpers
├── tests/                        # singular (business-rule) tests
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
end, the same way a scheduler (Airflow, Dagster, cron) would:

```
EXTRACT  -> generate raw source CSVs        (scripts/generate_seeds.py)
LOAD     -> load CSVs into DuckDB           (dbt seed)
TRANSFORM-> build staging -> int -> marts   (dbt run)
TEST     -> run all data-quality tests      (dbt test)
```

Useful flags:

```bash
python scripts/run_pipeline.py --target qa       # run against the qa warehouse
python scripts/run_pipeline.py --skip-generate   # reuse committed seed CSVs
python scripts/run_pipeline.py --full-refresh    # rebuild all tables from scratch
```

It exits non-zero if any step fails, so CI / schedulers can gate on it.

### Or run the steps manually

```bash
python scripts/generate_seeds.py     # 1. extract: regenerate raw CSVs (optional)
dbt deps --profiles-dir .            # 2. install the dbt_utils package
dbt build --profiles-dir .           # 3. load seeds + run models + run tests
```

Either path creates `dev.duckdb` in the project root with all marts populated. Explore it:

```bash
dbt show --profiles-dir . --inline "select * from main_marts.mart_football_team_standings order by league_position limit 10"
```

### Browse the docs & lineage graph

```bash
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

## Headline marts

**Football**
- `mart_football_team_standings` — full league table per season (points, W/D/L,
  goal difference, position).
- `mart_football_player_season_summary` — per-player goals, assists, minutes, and
  goal contributions per 90.

**Golf**
- `mart_golf_player_scoring_summary` — scoring average, average score to par,
  putts per round, GIR% and fairway%, ranked.
- `fct_golf_rounds` — every round with score-to-par and per-round shot metrics.

## Branching workflow

| Branch | Purpose                                                       |
| ------ | ------------------------------------------------------------ |
| `main` | Production-ready models. Protected; changes arrive via PR.   |
| `qa`   | Validation branch — run `dbt build --target qa` here to vet changes against an isolated `qa.duckdb` before promoting to `main`. |

Typical flow: branch from `qa` → develop → `dbt build --target qa` → open PR into
`main` once tests pass.
