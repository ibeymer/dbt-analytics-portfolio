-- Reconciliation test: total points scored across all teams (from the unpivoted
-- per-team game grain) must equal the total points across all games (from the
-- game grain). A mismatch means the unpivot dropped or double-counted data.
-- A singular test passes when it returns zero rows.

with from_team_grain as (
    select sum(points_for) as total_points
    from {{ ref('int_nfl__game_results') }}
),

from_game_grain as (
    select sum(home_score) + sum(away_score) as total_points
    from {{ ref('stg_nfl__games') }}
)

select t.total_points as team_grain_points, g.total_points as game_grain_points
from from_team_grain t
cross join from_game_grain g
where t.total_points != g.total_points
