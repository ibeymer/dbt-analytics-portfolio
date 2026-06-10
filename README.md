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
├── scripts/generate_seeds.py     # deterministic synthetic-data generator
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
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) regenerate the synthetic raw data — already committed under seeds/
python scripts/generate_seeds.py

# 3. Install the dbt_utils package
dbt deps --profiles-dir .

# 4. Build everything: load seeds, run all models, run all tests
dbt build --profiles-dir .
```

That creates `dev.duckdb` in the project root with all marts populated. Explore it:

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
