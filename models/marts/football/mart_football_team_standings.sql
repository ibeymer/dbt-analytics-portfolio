{#
    League table: aggregate the per-team match grain into a season standings
    board, ranked by points then goal difference (standard football tie-break).
#}

with results as (

    select * from {{ ref('int_football__match_results') }}

),

teams as (

    select * from {{ ref('stg_football__teams') }}

),

aggregated as (

    select
        r.season,
        r.team_id,
        count(*)                                          as matches_played,
        sum(case when r.result = 'W' then 1 else 0 end)   as wins,
        sum(case when r.result = 'D' then 1 else 0 end)   as draws,
        sum(case when r.result = 'L' then 1 else 0 end)   as losses,
        sum(r.goals_for)                                  as goals_for,
        sum(r.goals_against)                              as goals_against,
        sum(r.goal_difference)                            as goal_difference,
        sum(r.points)                                     as points
    from results r
    group by r.season, r.team_id

)

select
    a.season,
    a.team_id,
    t.team_name,
    a.matches_played,
    a.wins,
    a.draws,
    a.losses,
    a.goals_for,
    a.goals_against,
    a.goal_difference,
    a.points,
    row_number() over (
        partition by a.season
        order by a.points desc, a.goal_difference desc, a.goals_for desc
    ) as league_position
from aggregated a
inner join teams t on a.team_id = t.team_id
order by a.season, league_position
