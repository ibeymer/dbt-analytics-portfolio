with matches as (

    select * from {{ ref('stg_football__matches') }}

),

teams as (

    select * from {{ ref('stg_football__teams') }}

)

select
    m.match_id,
    m.season,
    m.match_date,
    m.home_team_id,
    home.team_name              as home_team,
    m.away_team_id,
    away.team_name              as away_team,
    m.home_goals,
    m.away_goals,
    m.home_goals + m.away_goals as total_goals,
    case
        when m.home_goals > m.away_goals then 'home_win'
        when m.home_goals < m.away_goals then 'away_win'
        else 'draw'
    end                         as outcome,
    m.attendance
from matches m
inner join teams home on m.home_team_id = home.team_id
inner join teams away on m.away_team_id = away.team_id
