"""Extract PGA golf data from ESPN's public API into raw seed CSVs.

Pulls a fixed set of completed 2024 tournaments (the majors + The Players) so the
data is reproducible. For each tournament it captures the full leaderboard:

  * tournaments  — id, name, season, final-round date
  * players      — unique golfers across all tournaments (stable surrogate ids)
  * results      — one row per player per tournament (finish, total strokes/to-par)
  * round_scores — one row per player per round (strokes and score to par)

Round-level par is derived downstream in dbt as (strokes - score_to_par).

    python scripts/extract_golf.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from espn_api import get_json

SEASON = 2024
SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "golf"
SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/golf/pga/scoreboard?dates={date}"

# Curated, completed 2024 events keyed by their final-round date (YYYYMMDD).
TOURNAMENTS = {
    "20240317": "The Players Championship",
    "20240414": "Masters Tournament",
    "20240519": "PGA Championship",
    "20240616": "U.S. Open",
    "20240721": "The Open Championship",
}


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {len(rows):>4} rows -> {path.relative_to(SEEDS_DIR.parent.parent)}")


def parse_to_par(value) -> int | None:
    """ESPN renders to-par as 'E', '-6', '+2'. Return a signed int or None."""
    if value is None:
        return None
    s = str(value).strip()
    if s in ("E", "e"):
        return 0
    try:
        return int(s)          # int() handles leading '+' and '-'
    except ValueError:
        return None


def pick_event(events: list[dict], expected_name: str) -> dict | None:
    """Choose the event matching the expected name, else the one with the most players."""
    if not events:
        return None
    for e in events:
        if e.get("name") == expected_name:
            return e
    return max(events, key=lambda e: len(e["competitions"][0].get("competitors", [])))


def main() -> None:
    print(f"Golf extract (ESPN PGA, season {SEASON}):")

    tournaments: list[list] = []
    raw_results: list[dict] = []   # collected before player ids are assigned
    raw_rounds: list[dict] = []
    player_names: set[str] = set()

    for date, name in TOURNAMENTS.items():
        data = get_json(SCOREBOARD.format(date=date))
        event = pick_event(data.get("events", []), name)
        if event is None:
            print(f"  ! no event found for {name} ({date}); skipping")
            continue
        comp = event["competitions"][0]
        event_id = int(event["id"])
        tournaments.append([event_id, event["name"], SEASON, event["date"][:10]])

        for c in comp.get("competitors", []):
            athlete = c.get("athlete") or {}
            pname = athlete.get("displayName")
            if not pname:
                continue
            player_names.add(pname)

            rounds = []
            for ls in c.get("linescores") or []:
                strokes = ls.get("value")
                to_par = parse_to_par(ls.get("displayValue"))
                # Skip rounds that aren't a completed 18 holes: withdrawals and
                # partial rounds come back as 0 / missing score-to-par.
                if strokes is None or to_par is None:
                    continue
                strokes = int(strokes)
                if not 55 <= strokes <= 100:
                    continue
                # Drop records where ESPN's score-to-par is internally inconsistent
                # (implied par outside a real course range, e.g. 62 or 64).
                if not 69 <= strokes - to_par <= 73:
                    continue
                rounds.append({
                    "tournament_id": event_id,
                    "player_name": pname,
                    "round_number": int(ls.get("period")),
                    "strokes": strokes,
                    "score_to_par": to_par,
                })
            raw_rounds.extend(rounds)

            total_strokes = sum(r["strokes"] for r in rounds) if rounds else None
            raw_results.append({
                "tournament_id": event_id,
                "player_name": pname,
                "finish_position": c.get("order"),
                "total_strokes": total_strokes,
                "total_to_par": parse_to_par(c.get("score")),
            })

    # Deterministic player ids: sort unique names, number 1..N.
    player_id = {name: i for i, name in enumerate(sorted(player_names), start=1)}

    write_csv(
        SEEDS_DIR / "raw_golf_tournaments.csv",
        ["tournament_id", "tournament_name", "season", "end_date"],
        tournaments,
    )
    write_csv(
        SEEDS_DIR / "raw_golf_players.csv",
        ["player_id", "player_name"],
        [[pid, name] for name, pid in sorted(player_id.items(), key=lambda kv: kv[1])],
    )
    write_csv(
        SEEDS_DIR / "raw_golf_results.csv",
        ["tournament_id", "player_id", "finish_position", "total_strokes", "total_to_par"],
        [[r["tournament_id"], player_id[r["player_name"]], r["finish_position"],
          r["total_strokes"], r["total_to_par"]] for r in raw_results],
    )
    write_csv(
        SEEDS_DIR / "raw_golf_round_scores.csv",
        ["tournament_id", "player_id", "round_number", "strokes", "score_to_par"],
        [[r["tournament_id"], player_id[r["player_name"]], r["round_number"],
          r["strokes"], r["score_to_par"]] for r in raw_rounds],
    )


if __name__ == "__main__":
    main()
