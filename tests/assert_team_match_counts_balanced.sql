-- Business-rule test: in a 20-team double round-robin season, every team must
-- play exactly 38 matches (home and away vs each of the other 19). Any team
-- with a different count signals a data or modeling error.
-- A singular test passes when it returns zero rows.

select
    season,
    team_id,
    matches_played
from {{ ref('mart_football_team_standings') }}
where matches_played != 38
