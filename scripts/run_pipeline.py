"""End-to-end pipeline runner: extract -> load -> transform -> test.

A single entry point that mirrors what an orchestrator (Airflow, Dagster, cron)
would call in production:

    1. EXTRACT   pull raw source data from the ESPN API into CSVs
                 (scripts/extract_nfl.py, scripts/extract_golf.py)
    2. LOAD      `dbt seed`  — load those CSVs into DuckDB
    3. TRANSFORM `dbt run`   — build staging -> intermediate -> marts
    4. TEST      `dbt test`  — run all data-quality tests

Steps 2-4 are executed by a single `dbt build`, which interleaves them in
dependency order. dbt is invoked through its programmatic API (dbtRunner) so we
don't depend on the `dbt` executable being on PATH.

Examples
--------
    python scripts/run_pipeline.py                 # full run against the dev target
    python scripts/run_pipeline.py --target qa     # run against the qa warehouse
    python scripts/run_pipeline.py --skip-generate # reuse the committed seed CSVs
    python scripts/run_pipeline.py --skip-deps     # skip `dbt deps` (already installed)

Exit code is 0 on success, 1 if any step fails — so CI / schedulers can gate on it.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Project root = the directory containing dbt_project.yml (one level up from here).
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Make sibling modules (generate_seeds) importable regardless of how this is run.
sys.path.insert(0, str(Path(__file__).resolve().parent))


def banner(step: str, message: str) -> None:
    line = "=" * 70
    print(f"\n{line}\n[{step}] {message}\n{line}", flush=True)


def run_extract() -> None:
    """Step 1 — pull raw source data from the ESPN API into seed CSVs."""
    banner("EXTRACT", "Pulling source data from ESPN -> seeds/*.csv")
    import extract_nfl
    import extract_golf

    extract_nfl.main()
    extract_golf.main()


def run_dbt(args: list[str]) -> None:
    """Invoke dbt via its programmatic API; raise on failure."""
    from dbt.cli.main import dbtRunner

    print(f"\n$ dbt {' '.join(args)}", flush=True)
    result = dbtRunner().invoke(args)
    if not result.success:
        # result.exception is set for hard failures; otherwise a node failed/tested red.
        detail = result.exception or "one or more dbt nodes failed (see output above)"
        raise RuntimeError(f"dbt {args[0]} failed: {detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target", default="dev",
                        help="dbt target / environment to run against (default: dev)")
    parser.add_argument("--skip-generate", action="store_true",
                        help="reuse the committed seed CSVs instead of re-pulling from the API")
    parser.add_argument("--skip-deps", action="store_true",
                        help="skip `dbt deps` (use when packages are already installed)")
    parser.add_argument("--full-refresh", action="store_true",
                        help="pass --full-refresh to dbt build (rebuild tables from scratch)")
    cli_args = parser.parse_args()

    # dbt resolves dbt_project.yml and the in-repo profiles.yml relative to cwd,
    # so anchor everything at the project root no matter where we're invoked from.
    profiles_dir = str(PROJECT_ROOT)
    started = time.time()

    try:
        # 1. EXTRACT
        if cli_args.skip_generate:
            print("[EXTRACT] skipped (--skip-generate); using committed seed CSVs")
        else:
            run_extract()

        # 2. install packages (dbt_utils)
        if not cli_args.skip_deps:
            banner("DEPS", "Installing dbt packages")
            run_dbt(["deps", "--project-dir", str(PROJECT_ROOT),
                     "--profiles-dir", profiles_dir])

        # 3. LOAD + TRANSFORM + TEST (seed -> run -> test, in dependency order)
        banner("BUILD", f"dbt build  (target={cli_args.target})  "
                         f"load -> transform -> test")
        build_args = ["build", "--target", cli_args.target,
                      "--project-dir", str(PROJECT_ROOT),
                      "--profiles-dir", profiles_dir]
        if cli_args.full_refresh:
            build_args.append("--full-refresh")
        run_dbt(build_args)

    except RuntimeError as exc:
        elapsed = time.time() - started
        print(f"\n PIPELINE FAILED after {elapsed:.1f}s: {exc}", file=sys.stderr)
        return 1

    elapsed = time.time() - started
    banner("DONE", f"Pipeline completed successfully in {elapsed:.1f}s "
                   f"(target={cli_args.target})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
