{#
    Per-player season totals and rates, joining match-level stats up to player
    and team dimensions. Goal contributions per 90 uses the safe_divide macro.
#}

with stats as (

    select * from {{ ref('stg_football__player_match_stats') }}

),

matches as (

    select * from {{ ref('stg_football__matches') }}

),

players as (

    select * from {{ ref('stg_football__players') }}

),

teams as (

    select * from {{ ref('stg_football__teams') }}

),

stats_with_season as (

    select
        s.*,
        m.season
    from stats s
    inner join matches m on s.match_id = m.match_id

),

aggregated as (

    select
        season,
        player_id,
        count(*)                as appearances,
        sum(minutes_played)     as minutes_played,
        sum(goals)              as goals,
        sum(assists)            as assists,
        sum(shots)              as shots,
        sum(passes)             as passes,
        sum(tackles)            as tackles,
        sum(yellow_cards)       as yellow_cards,
        sum(red_cards)          as red_cards
    from stats_with_season
    group by season, player_id

)

select
    a.season,
    a.player_id,
    p.full_name,
    p.position,
    t.team_name,
    a.appearances,
    a.minutes_played,
    a.goals,
    a.assists,
    a.goals + a.assists                                          as goal_contributions,
    a.shots,
    a.passes,
    a.tackles,
    a.yellow_cards,
    a.red_cards,
    round({{ safe_divide('(a.goals + a.assists) * 90', 'a.minutes_played') }}, 3)
        as goal_contributions_per_90
from aggregated a
inner join players p on a.player_id = p.player_id
left join teams t on p.team_id = t.team_id
