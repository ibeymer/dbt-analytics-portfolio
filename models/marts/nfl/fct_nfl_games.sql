with games as (

    select * from {{ ref('stg_nfl__games') }}

),

teams as (

    select * from {{ ref('stg_nfl__teams') }}

)

select
    g.game_id,
    g.season,
    g.week,
    g.game_date,
    g.home_team_id,
    home.display_name           as home_team,
    g.away_team_id,
    away.display_name           as away_team,
    g.home_score,
    g.away_score,
    g.home_score + g.away_score as total_points,
    abs(g.home_score - g.away_score) as margin,
    case
        when g.home_score > g.away_score then 'home_win'
        when g.home_score < g.away_score then 'away_win'
        else 'tie'
    end                         as outcome
from games g
inner join teams home on g.home_team_id = home.team_id
inner join teams away on g.away_team_id = away.team_id
