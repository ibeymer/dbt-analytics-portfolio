"""Generate synthetic raw data for the football and golf dbt pipelines.

Everything is deterministic (fixed RNG seed) so the committed seed CSVs are
reproducible: re-running this script produces byte-identical output. Uses only
the Python standard library — no third-party dependencies — so reviewers can run
it with a bare interpreter.

Output: CSV files under seeds/football/ and seeds/golf/, which dbt loads as raw
source tables via `dbt seed`.

    python scripts/generate_seeds.py
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds"

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"  wrote {len(rows):>6} rows -> {path.relative_to(SEEDS_DIR.parent)}")


# --------------------------------------------------------------------------- #
# Football
# --------------------------------------------------------------------------- #

FOOTBALL_TEAMS = [
    ("Arsenal", "London"), ("Aston Villa", "Birmingham"), ("Brighton", "Brighton"),
    ("Burnley", "Burnley"), ("Chelsea", "London"), ("Crystal Palace", "London"),
    ("Everton", "Liverpool"), ("Fulham", "London"), ("Leeds United", "Leeds"),
    ("Liverpool", "Liverpool"), ("Manchester City", "Manchester"),
    ("Manchester United", "Manchester"), ("Newcastle", "Newcastle"),
    ("Nottingham Forest", "Nottingham"), ("Sheffield United", "Sheffield"),
    ("Tottenham", "London"), ("West Ham", "London"), ("Wolves", "Wolverhampton"),
    ("Bournemouth", "Bournemouth"), ("Brentford", "London"),
]

POSITIONS = ["GK", "DF", "MF", "FW"]
SQUAD_TEMPLATE = ["GK"] * 3 + ["DF"] * 8 + ["MF"] * 7 + ["FW"] * 5  # 23 per squad

FIRST_NAMES = [
    "James", "Oliver", "Harry", "Jack", "George", "Noah", "Leo", "Mason", "Lucas",
    "Diego", "Mohamed", "Bruno", "Kevin", "Luka", "Erling", "Kylian", "Vinicius",
    "Pedro", "Marcus", "Bukayo", "Phil", "Declan", "Trent", "Jordan", "Raheem",
]
LAST_NAMES = [
    "Smith", "Jones", "Williams", "Brown", "Taylor", "Davies", "Silva", "Santos",
    "Fernandes", "Salah", "Haaland", "Mbappe", "Rodriguez", "Mueller", "Kovacic",
    "Walker", "Saka", "Rice", "Foden", "Sterling", "Kane", "Son", "Nunez", "Diaz",
]
COUNTRIES = [
    "England", "Spain", "France", "Brazil", "Portugal", "Germany", "Argentina",
    "Netherlands", "Belgium", "Italy", "Norway", "Egypt", "Croatia", "Uruguay",
]


def generate_football(rng: random.Random) -> None:
    print("Football:")
    # Teams
    team_rows = []
    for i, (name, city) in enumerate(FOOTBALL_TEAMS, start=1):
        team_rows.append([
            i, name, city,
            rng.randint(1878, 1905),
            f"{name} Stadium",
            20000 + rng.randint(0, 55) * 1000,  # capacity
        ])
    write_csv(
        SEEDS_DIR / "football" / "raw_football_teams.csv",
        ["team_id", "team_name", "city", "founded_year", "stadium", "capacity"],
        team_rows,
    )

    # Players
    player_rows = []
    player_id = 0
    team_players: dict[int, list[int]] = {}
    for team_id, _ in enumerate(FOOTBALL_TEAMS, start=1):
        team_players[team_id] = []
        for pos in SQUAD_TEMPLATE:
            player_id += 1
            name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            birth = date(1988, 1, 1) + timedelta(days=rng.randint(0, 365 * 16))
            player_rows.append([
                player_id, team_id, name, pos,
                rng.choice(COUNTRIES), birth.isoformat(),
                rng.randint(1, 35),  # shirt number
            ])
            team_players[team_id].append(player_id)
    write_csv(
        SEEDS_DIR / "football" / "raw_football_players.csv",
        ["player_id", "team_id", "full_name", "position", "country",
         "birth_date", "shirt_number"],
        player_rows,
    )

    # Matches: single season, double round-robin
    season = "2023-2024"
    team_ids = [t[0] for t in team_rows]
    fixtures = [(h, a) for h in team_ids for a in team_ids if h != a]
    rng.shuffle(fixtures)
    match_rows = []
    match_day = date(2023, 8, 12)
    for match_id, (home, away) in enumerate(fixtures, start=1):
        # Home advantage baked into the scoring distribution.
        home_goals = rng.choices([0, 1, 2, 3, 4, 5], weights=[12, 26, 28, 18, 10, 6])[0]
        away_goals = rng.choices([0, 1, 2, 3, 4], weights=[20, 30, 27, 15, 8])[0]
        capacity = team_rows[home - 1][5]
        attendance = int(capacity * rng.uniform(0.78, 1.0))
        match_rows.append([
            match_id, season, match_day.isoformat(), home, away,
            home_goals, away_goals, attendance,
        ])
        if match_id % 10 == 0:
            match_day += timedelta(days=7)
    write_csv(
        SEEDS_DIR / "football" / "raw_football_matches.csv",
        ["match_id", "season", "match_date", "home_team_id", "away_team_id",
         "home_goals", "away_goals", "attendance"],
        match_rows,
    )

    # Player match stats: ~14 appearances per team per match
    stat_rows = []
    stat_id = 0
    for match in match_rows:
        match_id, _, _, home, away, home_goals, away_goals, _ = match
        for team_id, team_goals in ((home, home_goals), (away, away_goals)):
            squad = team_players[team_id]
            appearing = rng.sample(squad, 14)
            goals_left = team_goals
            for idx, pid in enumerate(appearing):
                stat_id += 1
                minutes = 90 if idx < 11 else rng.randint(5, 45)
                # Distribute the team's goals across the appearing players.
                goals = 0
                if goals_left > 0 and rng.random() < 0.25:
                    goals = rng.randint(1, goals_left)
                    goals_left -= goals
                assists = 1 if (goals == 0 and rng.random() < 0.15) else 0
                stat_rows.append([
                    stat_id, match_id, pid, minutes, goals, assists,
                    rng.randint(0, 5),                       # shots
                    rng.randint(8, 75),                      # passes
                    rng.randint(0, 6),                       # tackles
                    1 if rng.random() < 0.12 else 0,         # yellow card
                    1 if rng.random() < 0.015 else 0,        # red card
                ])
    write_csv(
        SEEDS_DIR / "football" / "raw_football_player_match_stats.csv",
        ["stat_id", "match_id", "player_id", "minutes_played", "goals", "assists",
         "shots", "passes", "tackles", "yellow_cards", "red_cards"],
        stat_rows,
    )


# --------------------------------------------------------------------------- #
# Golf
# --------------------------------------------------------------------------- #

GOLF_FIRST = [
    "Tiger", "Rory", "Scottie", "Jon", "Brooks", "Dustin", "Justin", "Collin",
    "Xander", "Patrick", "Viktor", "Jordan", "Hideki", "Cameron", "Matt",
    "Tony", "Max", "Sam", "Will", "Tom",
]
GOLF_LAST = [
    "Woods", "McIlroy", "Scheffler", "Rahm", "Koepka", "Johnson", "Thomas",
    "Morikawa", "Schauffele", "Cantlay", "Hovland", "Spieth", "Matsuyama",
    "Smith", "Fitzpatrick", "Finau", "Homa", "Burns", "Zalatoris", "Kim",
]
GOLF_COUNTRIES = ["USA", "Northern Ireland", "Spain", "Norway", "Japan",
                  "Australia", "England", "South Korea", "Canada"]
COURSE_NAMES = [
    ("Augusta National", "Augusta, GA"), ("Pebble Beach", "Pebble Beach, CA"),
    ("St Andrews", "St Andrews, Scotland"), ("Pinehurst No. 2", "Pinehurst, NC"),
    ("Torrey Pines", "San Diego, CA"), ("Bethpage Black", "Farmingdale, NY"),
    ("Whistling Straits", "Kohler, WI"), ("TPC Sawgrass", "Ponte Vedra, FL"),
    ("Royal Melbourne", "Melbourne, Australia"), ("Muirfield", "Gullane, Scotland"),
    ("Oakmont", "Oakmont, PA"), ("Shinnecock Hills", "Southampton, NY"),
]
TOURNAMENTS = ["The Masters", "PGA Championship", "US Open", "The Open",
               "Players Championship", "FedEx Cup Playoff"]


def generate_golf(rng: random.Random) -> None:
    print("Golf:")
    # Players: each has a latent skill that drives scoring.
    player_rows = []
    skills: dict[int, float] = {}
    for pid in range(1, 41):
        name = f"{rng.choice(GOLF_FIRST)} {rng.choice(GOLF_LAST)}"
        skills[pid] = rng.gauss(0.0, 1.8)  # lower is better
        player_rows.append([
            pid, name, rng.choice(GOLF_COUNTRIES),
            rng.randint(2005, 2021),                       # turned pro
            rng.choice(["R", "R", "R", "L"]),              # handedness
        ])
    write_csv(
        SEEDS_DIR / "golf" / "raw_golf_players.csv",
        ["player_id", "full_name", "country", "turned_pro_year", "handedness"],
        player_rows,
    )

    # Courses (par 3/4/5 layout per hole)
    course_rows = []
    course_holes: dict[int, list[int]] = {}
    for cid, (name, loc) in enumerate(COURSE_NAMES, start=1):
        pars = []
        for _ in range(18):
            pars.append(rng.choices([3, 4, 5], weights=[4, 10, 4])[0])
        total_par = sum(pars)
        yardage = 6800 + rng.randint(0, 600)
        course_rows.append([cid, name, loc, total_par, yardage, 18])
        course_holes[cid] = pars
    write_csv(
        SEEDS_DIR / "golf" / "raw_golf_courses.csv",
        ["course_id", "course_name", "location", "par", "yardage", "num_holes"],
        course_rows,
    )

    # Rounds + hole-by-hole scores
    round_rows = []
    hole_rows = []
    round_id = 0
    score_id = 0
    round_date = date(2023, 4, 6)
    for tournament in TOURNAMENTS:
        course_id = rng.randint(1, len(COURSE_NAMES))
        pars = course_holes[course_id]
        field = rng.sample(range(1, 41), 30)  # 30-player field
        for round_number in range(1, 5):  # 4 rounds per tournament
            for pid in field:
                round_id += 1
                skill = skills[pid]
                total_strokes = 0
                for hole_number, par in enumerate(pars, start=1):
                    # Score relative to par driven by skill + hole difficulty.
                    roll = rng.gauss(skill * 0.06 + (par - 4) * 0.05, 0.7)
                    delta = max(-1, min(3, round(roll)))
                    strokes = par + delta
                    total_strokes += strokes
                    putts = 1 if strokes <= par - 1 else rng.choice([1, 2, 2, 2, 3])
                    gir = 1 if strokes <= par - (2 if par == 5 else 1) + 1 else 0
                    fairway = "" if par == 3 else (1 if rng.random() < 0.62 else 0)
                    score_id += 1
                    hole_rows.append([
                        score_id, round_id, hole_number, par, strokes,
                        fairway, gir, putts,
                    ])
                round_rows.append([
                    round_id, pid, course_id, tournament,
                    round_date.isoformat(), round_number, total_strokes,
                ])
            round_date += timedelta(days=1)
        round_date += timedelta(days=21)
    write_csv(
        SEEDS_DIR / "golf" / "raw_golf_rounds.csv",
        ["round_id", "player_id", "course_id", "tournament", "round_date",
         "round_number", "total_strokes"],
        round_rows,
    )
    write_csv(
        SEEDS_DIR / "golf" / "raw_golf_hole_scores.csv",
        ["score_id", "round_id", "hole_number", "par", "strokes",
         "fairway_hit", "green_in_regulation", "putts"],
        hole_rows,
    )


def main() -> None:
    rng = random.Random(SEED)
    print(f"Generating synthetic seeds (RNG seed={SEED})\n")
    generate_football(rng)
    generate_golf(rng)
    print("\nDone.")


if __name__ == "__main__":
    main()
