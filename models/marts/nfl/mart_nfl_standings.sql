{#
    Season standings: aggregate the per-team game grain into wins/losses/ties,
    win percentage, and points for/against, then rank within each division
    (NFL tie-break is simplified to win pct then point differential).
#}

with results as (

    select * from {{ ref('int_nfl__game_results') }}

),

teams as (

    select * from {{ ref('stg_nfl__teams') }}

),

aggregated as (

    select
        season,
        team_id,
        count(*)                                        as games_played,
        sum(case when result = 'W' then 1 else 0 end)   as wins,
        sum(case when result = 'L' then 1 else 0 end)   as losses,
        sum(case when result = 'T' then 1 else 0 end)   as ties,
        sum(points_for)                                 as points_for,
        sum(points_against)                             as points_against,
        sum(point_differential)                         as point_differential
    from results
    group by season, team_id

)

select
    a.season,
    a.team_id,
    t.display_name,
    t.conference,
    t.division,
    a.games_played,
    a.wins,
    a.losses,
    a.ties,
    round({{ safe_divide('a.wins + 0.5 * a.ties', 'a.games_played') }}, 3)
        as win_pct,
    a.points_for,
    a.points_against,
    a.point_differential,
    row_number() over (
        partition by a.season, t.division
        order by {{ safe_divide('a.wins + 0.5 * a.ties', 'a.games_played') }} desc,
                 a.point_differential desc
    ) as division_rank
from aggregated a
inner join teams t on a.team_id = t.team_id
order by t.conference, t.division, division_rank
