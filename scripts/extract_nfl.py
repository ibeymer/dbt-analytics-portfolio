"""Extract NFL data from ESPN's public API into raw seed CSVs.

Pulls two things for a fixed historical season (default 2023, for reproducibility):

  * teams  — id, names, conference, division (from the standings endpoint)
  * games  — every regular-season game with home/away teams and final scores
             (from the weekly scoreboard, weeks 1-18)

Standings are intentionally NOT pulled pre-computed — they are derived downstream
in dbt from the game results, which is the point of the pipeline.

    python scripts/extract_nfl.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from espn_api import get_json

SEASON = 2023
REGULAR_SEASON = 2          # ESPN seasontype: 2 = regular season
WEEKS = range(1, 19)        # 2021+ regular season has 18 weeks
SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "nfl"

SITE = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
STANDINGS = "https://cdn.espn.com/core/nfl/standings?xhr=1&season={season}"


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {len(rows):>4} rows -> {path.relative_to(SEEDS_DIR.parent.parent)}")


def extract_teams() -> list[list]:
    """Teams with conference + division, read from the standings tree."""
    data = get_json(STANDINGS.format(season=SEASON))
    conferences = data["content"]["standings"]["groups"]
    rows = []
    for conf in conferences:
        conf_name = conf["name"]
        for div in conf["groups"]:
            div_name = div["name"]
            for entry in div["standings"]["entries"]:
                t = entry["team"]
                rows.append([
                    int(t["id"]),
                    t.get("abbreviation"),
                    t.get("displayName"),
                    t.get("location"),
                    t.get("nickname") or t.get("name"),
                    conf_name,
                    div_name,
                ])
    return rows


def extract_games() -> list[list]:
    """Every regular-season game from the weekly scoreboards."""
    rows = []
    for week in WEEKS:
        url = f"{SITE}/scoreboard?seasontype={REGULAR_SEASON}&week={week}&dates={SEASON}"
        data = get_json(url)
        for event in data.get("events", []):
            comp = event["competitions"][0]
            if comp["status"]["type"]["name"] != "STATUS_FINAL":
                continue
            home = next(c for c in comp["competitors"] if c["homeAway"] == "home")
            away = next(c for c in comp["competitors"] if c["homeAway"] == "away")
            rows.append([
                int(event["id"]),
                SEASON,
                week,
                event["date"][:10],
                int(home["team"]["id"]),
                int(away["team"]["id"]),
                int(home["score"]),
                int(away["score"]),
            ])
    return rows


def main() -> None:
    print(f"NFL extract (ESPN, season {SEASON}):")
    teams = extract_teams()
    write_csv(
        SEEDS_DIR / "raw_nfl_teams.csv",
        ["team_id", "abbreviation", "display_name", "location", "nickname",
         "conference", "division"],
        teams,
    )
    games = extract_games()
    write_csv(
        SEEDS_DIR / "raw_nfl_games.csv",
        ["game_id", "season", "week", "game_date", "home_team_id", "away_team_id",
         "home_score", "away_score"],
        games,
    )


if __name__ == "__main__":
    main()
